// Get basename from URL path
function getBasename() {
    // Get everything after the first slash, or empty string if no slash
    return window.location.pathname.substring(1) || '';
}

// Find destination button logic
async function findDestination() {
    // Get the source, destination, and timecode from the input fields
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${time}&destination=${destination}`;
    const response = await fetch(url);
    const data = await response.json();
    document.getElementById('destination').value = data.timecode;
}

// Find source button logic
async function findSource() {
    // Get the source, destination, and timecode from the input fields
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${time}&destination=${source}`;
    const response = await fetch(url);
    const data = await response.json();
    document.getElementById('source').value = data.timecode;
}

