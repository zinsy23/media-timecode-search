import re
import math
from difflib import SequenceMatcher

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

    return fuzzyScores

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