import re
import math

def contiguous_search(text, array):
    target = text.strip()
    n = len(array)
    start = 0
    
    # print([row[1] for row in array[0:4]])

    for end in range(n):
        segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])

        if target in segment:
            start = end - 1
            segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])
            while (target not in segment):
                start = start - 1
                print(start)
                segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])
            return (start, end)
        else:
            start = max(end - 10, math.ceil(len(text.split()) / 15))
    
    return (-1, -1)

# regex timecode: \d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}
# regex index: ^[0-9]+$
def load_srt(source):
    sourceSrt = open(source, "r").read().split("\n")
    sourceTimeTexts = []
    currentTimeText = []
    lastTimeIndex = -1

    for i in range(len(sourceSrt) - 1):
        if(re.search("\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", sourceSrt[i])):
            lastTimeIndex = i
            currentTimeText.append(sourceSrt[i])
        elif(sourceSrt[i] == ''):
            currentTimeText.append(" ".join(sourceSrt[lastTimeIndex + 1:i]))
            if(len(currentTimeText) > 1):
                sourceTimeTexts.append(currentTimeText)
                currentTimeText = []

    return sourceTimeTexts    