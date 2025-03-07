import re
import math
from difflib import SequenceMatcher
from datetime import datetime

# Searches blocks of subtitle text
def contiguous_search(text, array):
    target = text.strip() # Remove spaces at beginning and end of input text
    n = len(array)
    start = 0

    for end in range(n):
        # Combines multiple lines of subtitle input based on start and end range for comparison
        segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])

        # If we have a match, adjust the start range to the true start of the match.
        # Otherwise, keep going until there is a match
        if target in segment:
            # Adjust the start to the very end and expand the search until we find our true start
            start = end - 1
            segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])
            while (target not in segment):
                start = start - 1
                segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])
            return (start, end)
        else:
            # Memory management to prevent the segment variable from growing too much.
            start = max(end - 10, math.ceil(len(text.split()) / 15)) # Start is a min of 10 but can grow if str(text) requires a greater gap to end
    
    return (-1, -1)

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

# Creates an array of fuzzy search scores throughout the source
def score_fuzzy_indexes(text, array):
    fuzzyScores = []

    # Score each index of array against the text for similarity between 0 an 1
    for i in range(len(array)):
        matcher = SequenceMatcher(None, text, array[i][1])
        fuzzyScores.append(matcher.ratio())

    return fuzzyScores, len(text.split()) # TODO: turn back into single return when destination subtitle is implemented

# Gets the index of the largest stored fuzzy of a fuzzy scores array
def get_largest(array):
    # Initialize the largest array and index for standard largest item algorithm
    largest = array[0]
    largestIndex = 0

    for i in range(len(array)):
        if array[i] > largest:
            largest = array[i]
            largestIndex = i

    return largestIndex

# Gets the starting time of the referenced moment
def get_starting_time(fuzzies, textLength):
    largestIndex = get_largest(fuzzies)

    start = end = largestIndex

    estimatedNumSnippets = math.ceil(textLength / 15)
    margin = 0.10

    for i in range(estimatedNumSnippets):
        if(largestIndex + i + 1 <= len(fuzzies)):
            if(fuzzies[largestIndex + i + 1] > fuzzies[largestIndex] - 12):
                end += 1
            else:
                break

    for i in range(estimatedNumSnippets):
        if(largestIndex - i - 1 >= len(fuzzies)):
            if(fuzzies[largestIndex - i - 1] > fuzzies[largestIndex] - 12):
                start -= 1
            else:
                break

    return start #TODO: verify reliability

# Gets the corresponding timecode of the desination source
# destinationTime format: HH:MM:SS
# We're matching a timecode like: 00:10:33,159 --> 00:10:35,559
def corresponding_timecode_finder(destinationTime):
    sourceSrt = load_srt("subtitles/time_travel.srt")
    destinationSrt = load_srt("subtitles/time_travel.srt")

    # Convert the destinationTime variable into a format friendly with comparing timecodes
    destinationTimeCompare = datetime.strptime(destinationTime, "%H:%M:%S").time()

    # Initialize our comparison tracking variables
    startCompare = 0
    endCompare = len(destinationSrt)
    index = -1

    # Check if the timecode we're finding exists to determine if rounding is needed. If so, we don't need to round our time
    for i in range(len(destinationSrt)):
        if(destinationTime in destinationSrt[i][0][0:14]):
            index = i
            break

    # If we do need to round our time down, do so
    if index == -1:
        index = math.floor(endCompare / 2)
        while True:
            destinationSearch = re.search("^\d{2}:\d{2}:\d{2}", destinationSrt[index][0]).group()
            destinationSrtCompare = datetime.strptime(destinationSearch, "%H:%M:%S").time()

            # Perform a binary search to quickly find the time in O(log n)
            if(endCompare - startCompare < 2):
                index = startCompare
                break
            elif(destinationTimeCompare > destinationSrtCompare):
                startCompare = index
                index += math.floor((endCompare - startCompare) / 2)
            elif(destinationTimeCompare <= destinationSrtCompare):
                endCompare = index
                index -= math.floor((endCompare - startCompare) / 2)

    return destinationSrt[index] #TODO: Make it return actual starting point when we compare actual SRTs