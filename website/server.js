// Import required modules
const express = require('express');
const path = require('path');

// Define express and port
const app = express();
const PORT = 8000;

// Serve static files from the current directory
app.use(express.static(__dirname));

// Catch-all route to serve index.html for any unmatched routes
app.get('*', (req, res) => {
    // Get the basename from the URL path (remove leading slash)
    const basename = req.url.substring(1);
    console.log(basename);

    // Serve the index.html file
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});