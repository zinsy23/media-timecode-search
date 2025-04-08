# Media Timecode Finder Site

Frontend website for the Media Timecode Finder.

## How to run

1. Install dependencies

```bash
npm i
```

2. Run the server

```bash
node server.js
```

3. Open the site. Ensure the resource exists in the referenced path.

```bash
http://localhost:8000/[resource]
```

## How to use

1. Ensure the resource exists in the referenced path in the URL. If it does not, the error page will be displayed.

2. Enter the timecode you are looking for. If you're looking for a destination timecode, enter the source timecode and click the "Find Destination" button or press enter.

3. If you're looking for a source timecode, enter the destination timecode and click the "Find Source" button or press enter.

4. The timecode will be displayed in the other input field.