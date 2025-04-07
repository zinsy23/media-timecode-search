// Global variables to store the source and destination pairs to minimize API calls
let sourceType = "";
let destinationType = "";

// Configure the API base URL - needs to be actual IP address if not accessing page locally
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;  // Use same hostname as webpage but port 5000

// Update the source and destination pairs globally when the page loads
window.onload = updateTypes;

// Get basename from URL path
function getBasename() {
    // Get everything after the first slash, or empty string if no slash
    return window.location.pathname.substring(1) || '';
}

// Convert a string to title case
function toTitleCase(str) {
    if (!str) return '';  // Handle empty string case
    return str.replace(/\b\w/g, char => char.toUpperCase());
}

// Update the source and destination pairs globally
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

    // Update the website header and placeholders
    document.getElementById('main-header').innerHTML = `
        Find the corresponding timecode between the ${sourceType} and ${destinationType} versions of ${formattedBasename}:`;
    document.getElementById('source').placeholder = toTitleCase(sourceType) + " timecode";
    document.getElementById('destination').placeholder = toTitleCase(destinationType) + " timecode";
    document.getElementById('source-button').innerHTML = "Find " + destinationType;
    document.getElementById('destination-button').innerHTML = "Find " + sourceType;
}

// Get source pair type
async function getSourceType() {
    const basename = getBasename();
    const url = `${API_BASE_URL}/source?basename=${basename}`;
    const response = await fetch(url);
    const data = await response.json();
    return data;
}

// Get destination pair type
async function getDestinationType() {
    const basename = getBasename();
    const url = `${API_BASE_URL}/destination?basename=${basename}`;
    const response = await fetch(url);
    const data = await response.json();
    return data;
}

// Find destination button logic
async function findDestination() {
    // Clear the destination input field and placeholder
    document.getElementById('destination').value = "";
    document.getElementById('destination').placeholder = "Searching...";

    // Get the source and basename from the input fields
    const source = document.getElementById('source').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `${API_BASE_URL}/timecode?basename=${basename}&time=${source}&destination=${destinationType}`;
    const response = await fetch(url);
    const data = await response.json();
    document.getElementById('destination').value = (data == null) ? "Not found" : data;
    document.getElementById('destination').placeholder = toTitleCase(destinationType) + " timecode";
}

// Find source button logic
async function findSource() {
    // Clear the source input field and placeholder
    document.getElementById('source').value = "";
    document.getElementById('source').placeholder = "Searching...";

    // Get the destination and basename from the input fields
    const destination = document.getElementById('destination').value;
    const basename = getBasename();

    // Send the request to the server
    const url = `${API_BASE_URL}/timecode?basename=${basename}&time=${destination}&destination=${sourceType}`;
    const response = await fetch(url);
    const data = await response.json();
    document.getElementById('source').value = (data == null) ? "Not found" : data;
    document.getElementById('source').placeholder = toTitleCase(sourceType) + " timecode";
}

