def contiguous_search(text, array):
    target = text.strip()
    n = len(array)
    
    for start in range(n):
        for end in range(start, n):
            segment = " ".join(s.strip() for s in array[start:end+1])
            if target in segment:
                return (start, end)
    
    return (-1, -1)