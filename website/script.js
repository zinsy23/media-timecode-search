// Find destination button logic
async function findDestination() {
    // Get the source, destination, and timecode from the input fields
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;

    // Send the request to the server
    const url = `http://localhost:5000/timecode?time=${time}&destination=${destination}`;
    const response = await fetch(url);
    const data = await response.json();
    document.getElementById('result').innerHTML = data.timecode;
}

// Find source button logic
async function findSource() {
    // Get the source, destination, and timecode from the input fields
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;

    // Send the request to the server
    const url = `http://localhost:5000/timecode?time=${time}&destination=${source}`;
    const response = await fetch(url);
    const data = await response.json();
    document.getElementById('result').innerHTML = data.timecode;
}

