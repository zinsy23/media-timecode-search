import re
import math
from difflib import SequenceMatcher
from datetime import datetime
from sys import argv

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
def corresponding_timecode_finder(destinationTime):
    sourceSrt = load_srt("subtitles/Time Travel GPT Edited.srt")
    destinationSrt = load_srt("subtitles/Time Travel GPT Live.srt")

    index = get_timecode_index(destinationTime, sourceSrt)

    bestMatchIndex, bestMatchScore = match_timecode(index, sourceSrt, destinationSrt)

    if bestMatchScore < 0.5:  # 50% minimum similarity threshold
        raise ValueError(f"Could not find reliable match between source and destination subtitles. Best match score: {bestMatchScore:.2%}")

    return destinationSrt[bestMatchIndex]

print(corresponding_timecode_finder(argv[1]))