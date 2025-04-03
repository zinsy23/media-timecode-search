import re
import os
from difflib import SequenceMatcher
from datetime import datetime
from sys import argv
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask backend server
app = Flask(__name__)
CORS(app)

# Define common source/destination pairs and their default order
VERSION_PAIRS = [
    ("edited", "live"),
    ("edit", "live"),
    ("edited", "livestream"),
    ("edit", "livestream"),
    ("source", "destination"),
    ("before", "after"),
    ("original", "edited")
]

# Define the route for the timecode API
@app.route('/timecode', methods=['GET'])
def get_timecode():
    basename = request.args.get('basename')
    time = request.args.get('time')
    destination = request.args.get('destination')

    # Check if required parameters are present
    if not all([basename, time, destination]):
        return jsonify({
            "error": "Missing required parameters",
            "required": ["basename", "time", "destination"]
        }), 400

    return jsonify(corresponding_timecode_finder(basename, time, sourceDestination=destination))

# API to return the source type of the subtitle file
@app.route('/source', methods=['GET'])
def get_source_type():
    basename = request.args.get('basename')
    versions = detect_subtitle_versions(basename) # Get source and destination pairs for website
    
    # Mechanism to detect if no valid subtitle files are found
    if not versions:
        return jsonify({"error": "No valid resource found"}), 404
        
    sourceType = versions[0] # Get source pair type
    return jsonify(sourceType)

# API to return the destination type of the subtitle file
@app.route('/destination', methods=['GET'])
def get_destination_type():
    basename = request.args.get('basename')
    versions = detect_subtitle_versions(basename) # Get source and destination pairs for website
    
    # Mechanism to detect if no valid subtitle files are found
    if not versions:
        return jsonify({"error": "No valid resource found"}), 404
        
    destinationType = versions[-1] # Get destination pair type
    return jsonify(destinationType)

# Get command line argument at index or return default if not provided
def get_arg_or_default(index, default=""):
    try:
        return argv[index]
    except IndexError:
        return default

# Detects the pair names of subtitles available for a given basename
def detect_subtitle_versions(basename):
    available_versions = set() # Use a set to avoid duplicates

    # Parse out the pair names from the subtitle files if they exist
    try:
        files = os.listdir("subtitles")
        for file in files:
            # Only match files that start with the exact basename followed by a space
            if file.startswith(basename + " "):
                # Extract the version part (everything between basename and .srt)
                version = file[len(basename):].strip().replace(".srt", "").strip()
                if version:  # Only add non-empty versions
                    available_versions.add(version)
    except OSError:
        return []
    
    return list(available_versions) # Convert set to list

# Determine source and destination versions based on available files and specified destination
def determine_source_destination(basename, specified_destination=None):
    versions = detect_subtitle_versions(basename)

    # Detect if subtitles are invalid
    if not versions:
        raise ValueError(f"No subtitle versions found for basename: {basename}")
    
    # If only one version exists, it must be both source and destination
    if len(versions) == 1:
        return versions[0], versions[0]
    
    # Determine the source and destination pairs and determine source and destination classifications
    for source, dest in VERSION_PAIRS:
        if source in versions and dest in versions:
            if specified_destination:
                # If destination is specified, use it as destination and find appropriate source
                if specified_destination == source:
                    return dest, source  # Reverse the direction
                elif specified_destination == dest:
                    return source, dest  # Keep normal direction
            return source, dest  # Use default direction
    
    # If no known pairs found, use alphabetical order as fallback
    versions.sort()
    source, dest = versions[0], versions[-1]
    
    if specified_destination:
        if specified_destination == source:
            return dest, source  # Reverse direction
        elif specified_destination == dest:
            return source, dest  # Keep direction
        else:
            raise ValueError(f"Specified destination '{specified_destination}' not found in available versions: {versions}")
    
    return source, dest

# Loads an SRT file into a data structure friendly for the rest of the program
def load_srt(source):
    # Read the input SRT and set up data structure friendly for all needed operations
    sourceSrt = open(source, "r").read().split("\n")
    sourceTimeTexts = []
    currentTimeText = []
    lastTimeIndex = -1

    # Add SRT timecode and text entries to a 2D array
    for i in range(len(sourceSrt) - 1):
        if(re.search(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", sourceSrt[i])):
            # Add timecode text entry to array
            lastTimeIndex = i
            currentTimeText.append(sourceSrt[i])
        elif(sourceSrt[i] == ''):
            # Add correspondingtext entry to array
            currentTimeText.append(" ".join(sourceSrt[lastTimeIndex + 1:i]))

            # When we have a time and text entry, we're read to put into 2D array
            if(len(currentTimeText) > 1):
                sourceTimeTexts.append(currentTimeText)
                currentTimeText = []

    return sourceTimeTexts

# Matches input timecode to actual timecode in source SRT file, rounding down to the nearest second
def get_timecode_index(destinationTime, sourceSrt):
    # Convert the destinationTime variable into a format friendly with comparing timecodes
    destinationTimeCompare = datetime.strptime(destinationTime, "%H:%M:%S").time()

    # Binary search to find closest matching time
    left = 0
    right = len(sourceSrt) - 1
    
    while left <= right:
        mid = (left + right) // 2
        current_time = re.search(r"^\d{2}:\d{2}:\d{2}", sourceSrt[mid][0]).group()
        current_time = datetime.strptime(current_time, "%H:%M:%S").time()
        
        if current_time == destinationTimeCompare:
            index = mid
            break
        elif current_time < destinationTimeCompare:
            left = mid + 1
        else:
            right = mid - 1
    else:
        # If exact match not found, use the closest time
        index = left if left < len(sourceSrt) else right

    return index
    
# Matches the timecode to the best matching text in the corresponding destination SRT file
def match_timecode(index, sourceSrt, destinationSrt):
    # Initialize variables
    searchRadius = 2
    searchText = ""
    startIdx = max(0, index - searchRadius)
    endIdx = min(len(sourceSrt) - 1, index + searchRadius)
    
    # Get the text from sourceSrt around our index to use as search context
    for i in range(startIdx, endIdx + 1):
        searchText += sourceSrt[i][1] + " "
    searchText = searchText.strip()

    # Search through destinationSrt with expanding window until good match found
    bestMatchScore = 0
    bestMatchIndex = -1
    searchWindow = max(20, abs(index - len(destinationSrt) // 2))  # Start with larger window if times are far apart
    
    while bestMatchScore < 0.8 and searchWindow <= len(destinationSrt):  # 80% similarity threshold
        windowStart = max(0, index - searchWindow//2)
        windowEnd = min(len(destinationSrt) - 1, index + searchWindow//2)
        
        for i in range(windowStart, windowEnd + 1):
            compareText = ""
            compareStart = max(0, i - searchRadius)
            compareEnd = min(len(destinationSrt) - 1, i + searchRadius)
            
            for j in range(compareStart, compareEnd + 1):
                compareText += destinationSrt[j][1] + " "
            compareText = compareText.strip()
            
            # Use SequenceMatcher for similarity comparison
            matcher = SequenceMatcher(None, searchText.lower(), compareText.lower())
            score = matcher.ratio()
            
            if score > bestMatchScore:
                bestMatchScore = score
                bestMatchIndex = i
        
        searchWindow *= 2
    
    return (bestMatchIndex, bestMatchScore) # Return the best match index and score

# Gets the corresponding timecode of the desination source
# destinationTime format: HH:MM:SS
# We're matching a timecode like: 00:10:33,159 --> 00:10:35,559 from let's say 00:10:34 input
def corresponding_timecode_finder(baseName, destinationTime, sourceDestination=""):
    # Determine source and destination versions
    try:
        source_version, dest_version = determine_source_destination(baseName, sourceDestination)
    except ValueError as e:
        print(f"Error: {e}")
        return None
        
    # Load the appropriate SRT files
    try:
        sourceSrt = load_srt(f"subtitles/{baseName} {source_version}.srt")
        destinationSrt = load_srt(f"subtitles/{baseName} {dest_version}.srt")
    except FileNotFoundError as e:
        print(f"Error: Could not load subtitle files - {e}")
        return None

    # Get the index of the user inputted timecode in the source SRT file
    index = get_timecode_index(destinationTime, sourceSrt)

    # Match the timecode to the best matching text in the corresponding destination SRT file
    bestMatchIndex, bestMatchScore = match_timecode(index, sourceSrt, destinationSrt)

    # If we don't have a good match, return None
    if bestMatchScore < 0.5:  # 50% minimum similarity threshold
        return None

    # Get the timecode from the best matching text in the destination SRT file
    timecode = re.search(r"^\d{2}:\d{2}:\d{2}", destinationSrt[bestMatchIndex][0]).group()
    return timecode

# Convert any supported time format (HH:MM:SS, MM:SS, SS) to HH:MM:SS format
def normalize_time_format(time_str):
    try:
        # HH:MM:SS format (now accepts 1 or 2 digits for hours)
        if re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
            hours, minutes, seconds = map(int, time_str.split(':'))
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        # MM:SS format
        elif re.match(r'^\d{1,2}:\d{2}$', time_str):
            minutes, seconds = map(int, time_str.split(':'))
            hours, minutes = divmod(minutes, 60)  # Handle case where minutes > 59
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        # SS format
        elif re.match(r'^\d+$', time_str):
            total_seconds = int(time_str)
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            raise ValueError("Invalid time format")
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Please use HH:MM:SS, MM:SS, or SS format.")

if __name__ == "__main__":
    if len(argv) < 2:
        app.run(host='0.0.0.0', port=5000)  # Run the Flask server if no arguments are provided
    else:
        basename = argv[1]
        try:
            time = normalize_time_format(argv[2])
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)
        destination = get_arg_or_default(3, "")
        
        # Run CLI with provided arguments
        result = corresponding_timecode_finder(basename, time, destination)
        if result:
            print(result)
        else:
            print("No matching timecode found")