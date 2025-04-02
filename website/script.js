let sourceType = "";
let destinationType = "";

window.onload = updateTypes;

// Get basename from URL path
function getBasename() {
    // Get everything after the first slash, or empty string if no slash
    return window.location.pathname.substring(1) || '';
}

function toTitleCase(str) {
    if (!str) return '';  // Handle empty string case
    return str.replace(/\b\w/g, char => char.toUpperCase());
}

async function updateTypes() {
    const basename = getBasename();
    
    // If we're on the root path, don't try to get types
    if (!basename) {
        document.getElementById('main-header').innerHTML = 'Find the corresponding timecode between media versions:';
        document.getElementById('source').placeholder = "Source timecode";
        document.getElementById('destination').placeholder = "Destination timecode";
        document.getElementById('source-button').innerHTML = "Find Destination";
        document.getElementById('destination-button').innerHTML = "Find Source";
        return;
    }

    // The .replace() is a manual way to achieve title case
    sourceType = await getSourceType();
    destinationType = await getDestinationType();
    const formattedBasename = toTitleCase(basename.replace(/_/g, ' '));

    document.getElementById('main-header').innerHTML = `
        Find the corresponding timecode between the ${sourceType} and ${destinationType} versions of ${formattedBasename}:`;
    document.getElementById('source').placeholder = toTitleCase(sourceType) + " timecode";
    document.getElementById('destination').placeholder = toTitleCase(destinationType) + " timecode";
    document.getElementById('source-button').innerHTML = "Find " + destinationType;
    document.getElementById('destination-button').innerHTML = "Find " + sourceType;
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

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${source}&destination=${destinationType}`;
    console.log("Making request to:", url);
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response:", data);
    document.getElementById('destination').value = (data == null) ? "Not found" : data;
    document.getElementById('destination').placeholder = toTitleCase(destinationType) + " timecode";
}

// Find source button logic
async function findSource() {
    // Get the source, destination, and timecode from the input fields
    document.getElementById('source').value = "";
    document.getElementById('source').placeholder = "Searching...";
    console.log("findSource");
    const destination = document.getElementById('destination').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `http://localhost:5000/timecode?basename=${basename}&time=${destination}&destination=${sourceType}`;
    console.log("Making request to:", url);
    const response = await fetch(url);
    const data = await response.json();
    console.log("Received response:", data);
    document.getElementById('source').value = (data == null) ? "Not found" : data;
    document.getElementById('source').placeholder = toTitleCase(sourceType) + " timecode";
}

