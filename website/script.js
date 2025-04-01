// Get basename from URL path
function getBasename() {
    // Get everything after the first slash, or empty string if no slash
    return window.location.pathname.substring(1) || '';
}

// Get source type
async function getSourceType() {
    const basename = getBasename();
    const url = `http://localhost:5000/source?basename=${basename}`;
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response for source:", data);
    return data;
}

// Get destination type
async function getDestinationType() {
    const basename = getBasename();
    const url = `http://localhost:5000/destination?basename=${basename}`;
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response for destination:", data);
    return data;
}

// Find destination button logic
async function findDestination() {
    // Get the source, destination, and timecode from the input fields
    document.getElementById('destination').value = "";
    document.getElementById('destination').placeholder = "Searching...";
    console.log("findDestination");
    const source = document.getElementById('source').value;
    const basename = getBasename();
    const destinationType = await getDestinationType();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${source}&destination=${destinationType}`;
    console.log("Making request to:", url);
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response:", data);
    document.getElementById('destination').value = (data == null) ? "Not found" : data;
    document.getElementById('destination').placeholder = "Destination";
}

// Find source button logic
async function findSource() {
    // Get the source, destination, and timecode from the input fields
    document.getElementById('source').value = "";
    document.getElementById('source').placeholder = "Searching...";
    console.log("findSource");
    const destination = document.getElementById('destination').value;
    const basename = getBasename();
    const sourceType = await getSourceType();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${destination}&destination=${sourceType}`;
    console.log("Making request to:", url);
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response:", data);
    document.getElementById('source').value = (data == null) ? "Not found" : data;
    document.getElementById('source').placeholder = "Source";
}

