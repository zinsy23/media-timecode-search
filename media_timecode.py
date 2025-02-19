def contiguous_search(text, array):
  text_words = text.split()
  start_index = -1
  end_index = -1

  for i, word in enumerate(array):
    if word == text_words[0]:
      start_index = i
      match_count = 1
      for j in range(i + 1, len(array)):
        if match_count == len(text_words):
          end_index = j - 1
          break
        if array[j] == text_words[match_count]:
          match_count += 1
        else:
          start_index = -1
          match_count = 0
          break
    if start_index != -1 and end_index != -1:
      break

  return start_index, end_index

text = "turn off my TV it automatically"
array = ["when I turn off my", "TV it automatically turns off that accessory as well"]
start, end = contiguous_search(text, array)