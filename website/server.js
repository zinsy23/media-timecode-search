// Import required modules
const express = require('express');
const path = require('path');

// Define express and port
const app = express();
const PORT = 8000;

app.use(express.static(__dirname));

// Serve static files from the current directory
app.get('*', (req, res) => {
    console.log(req.url);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});