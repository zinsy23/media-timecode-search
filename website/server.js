// Import required modules
const express = require('express');
const path = require('path');
const fetch = require('node-fetch');

// Define express and port
const app = express();
const PORT = 8000;

// Serve static files first
app.use(express.static(__dirname));

// Serve static files from the current directory
app.get('*', async (req, res) => {
    // Get the basename from the URL path (remove leading slash)
    const basename = req.url.substring(1);
    
    // Skip checking for static files
    if (basename.includes('.')) {
        return;
    }

    try {
        // Check if the resource exists by calling the source API
        const response = await fetch(`http://localhost:5000/source?basename=${basename}`);
        
        // Check if the response is ok (status in the range 200-299)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // If we get here, the resource exists
        res.sendFile(path.join(__dirname, 'index.html'));
    } catch (error) {
        // If there's an error (like no valid resource), serve the error page
        console.log(`Error for basename ${basename}:`, error);
        res.sendFile(path.join(__dirname, 'error.html'));
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});