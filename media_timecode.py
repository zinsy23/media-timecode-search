import re

def contiguous_search(text, array):
    target = text.strip()
    n = len(array)
    
    # print([row[1] for row in array[0:4]])

    for start in range(n):
        for end in range(start, n):
            segment = " ".join(s.strip() for s in [row[1] for row in array[start:end+1]])

            if target in segment:
                print(segment)
                return (start, end)
    
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

source_srt = load_srt("subtitles/time_travel.srt")

print(contiguous_search("escape from this right here but I", source_srt))