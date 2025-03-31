// Import required modules
const express = require('express');
const path = require('path');

// Define express and port
const app = express();
const PORT = 8000;

// Serve static files from the current directory
app.use(express.static(__dirname));

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});