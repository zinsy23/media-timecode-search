// Get basename from URL path
function getBasename() {
    // Get everything after the first slash, or empty string if no slash
    return window.location.pathname.substring(1) || '';
}

// Find destination button logic
async function findDestination() {
    // Get the source, destination, and timecode from the input fields
    console.log("findDestination");
    const source = document.getElementById('source').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${source}&destination=live`;
    console.log("Making request to:", url);
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response:", data);
    document.getElementById('destination').value = data;
}

// Find source button logic
async function findSource() {
    // Get the source, destination, and timecode from the input fields
    console.log("findSource");
    const destination = document.getElementById('destination').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${destination}&destination=edited`;
    console.log("Making request to:", url);
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response:", data);
    document.getElementById('source').value = data;
}

