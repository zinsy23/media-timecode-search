// Import required modules
const express = require('express');
const path = require('path');
const fetch = require('node-fetch'); // Used for loading the website based on whether a valid resource exists
const cors = require('cors');

// Define express and port
const app = express();
const PORT = 8000;

// Enable CORS for all routes
app.use(cors());

// Define API URL using service name from docker-compose
const API_URL = process.env.API_URL || (process.env.NODE_ENV === 'production' 
    ? 'http://media-timecode:5000'  // Docker environment
    : 'http://localhost:5000');     // Local environment

// Handle root path first
app.get('/', (req, res) => {
    // Disable caching (comment res.set to enable caching)
    /*
    res.set({
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    });
    */
    res.sendFile(path.join(__dirname, 'error.html')); // Send error page if no resource is specified
});

// Handle all other paths
app.get('*', async (req, res, next) => {
    // Get the basename from the URL path (remove leading slash)
    const basename = req.url.substring(1);
    
    // Skip checking for static files
    if (basename.includes('.')) {
        // Disable caching (comment res.set to enable caching)
        /*
        res.set({
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        });
        */
        return next();  // Pass to next middleware (static file handler)
    }

    try {
        // Check if the resource exists by calling the source API
        const response = await fetch(`${API_URL}/source?basename=${basename}`);
        
        // Don't proceed if no resource exists
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`); // Jump to catch block if no resource exists
        }
        
        // If we get here, the resource exists
        res.sendFile(path.join(__dirname, 'index.html'));
    } catch (error) {
        // If there's an error (like no valid resource), serve the error page
        console.log(`Error for basename ${basename}:`, error);
        res.sendFile(path.join(__dirname, 'error.html'));
    }
});

// Serve static files last
app.use(express.static(__dirname));

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});