import re
import math
import os
from difflib import SequenceMatcher
from datetime import datetime
from sys import argv

# Define common source/destination pairs and their default order
VERSION_PAIRS = [
    ("edited", "live"),
    ("source", "destination"),
    ("before", "after")
]

def get_arg_or_default(index, default=""):
    """Get command line argument at index or return default if not provided"""
    try:
        return argv[index]
    except IndexError:
        return default

def detect_available_versions(basename):
    """Detect available versions for a given basename by checking subtitle files"""
    available_versions = set()
    try:
        files = os.listdir("subtitles")
        for file in files:
            if file.startswith(basename):
                # Extract the version part (everything between basename and .srt)
                version = file[len(basename):].strip().replace(".srt", "").strip()
                if version:  # Only add non-empty versions
                    available_versions.add(version)
    except OSError:
        return []
    
    return list(available_versions)

def determine_source_destination(basename, specified_destination=None):
    """
    Determine source and destination versions based on available files and specified destination
    Returns: (source_version, destination_version)
    """
    versions = detect_available_versions(basename)
    if not versions:
        raise ValueError(f"No subtitle versions found for basename: {basename}")
    
    # If only one version exists, it must be both source and destination
    if len(versions) == 1:
        return versions[0], versions[0]
    
    # Try to match versions against known pairs
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

    for i in range(len(sourceSrt) - 1):
        if(re.search("\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", sourceSrt[i])):
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

def get_timecode_index(destinationTime, sourceSrt):
    # Convert the destinationTime variable into a format friendly with comparing timecodes
    destinationTimeCompare = datetime.strptime(destinationTime, "%H:%M:%S").time()

    # Binary search to find closest matching time
    left = 0
    right = len(sourceSrt) - 1
    
    while left <= right:
        mid = (left + right) // 2
        current_time = re.search("^\d{2}:\d{2}:\d{2}", sourceSrt[mid][0]).group()
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
    
    return (bestMatchIndex, bestMatchScore)

# Gets the corresponding timecode of the desination source
# destinationTime format: HH:MM:SS
# We're matching a timecode like: 00:10:33,159 --> 00:10:35,559
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

    index = get_timecode_index(destinationTime, sourceSrt)
    bestMatchIndex, bestMatchScore = match_timecode(index, sourceSrt, destinationSrt)

    if bestMatchScore < 0.5:  # 50% minimum similarity threshold
        return None

    timecode = re.search("^\d{2}:\d{2}:\d{2}", destinationSrt[bestMatchIndex][0]).group()
    return timecode

if __name__ == "__main__":
    if len(argv) < 3:
        print("Usage: python media_timecode.py <basename> <time> [destination_version]")
        exit(1)
        
    basename = argv[1]
    time = argv[2]
    destination = get_arg_or_default(3, "")
    
    result = corresponding_timecode_finder(basename, time, destination)
    if result:
        print(result)
    else:
        print("No matching timecode found")