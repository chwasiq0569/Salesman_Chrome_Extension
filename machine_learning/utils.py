def max_values(lst):
   result = []
   for item in lst:
       max_key = max(item, key=item.get)
       result.append({max_key: item[max_key]})
   return result

def extract_text_after_word(word, string):
    index = string.find(word)
    if index != -1:
        return string[index + len(word):]
    else:
        return "Word not found in string."

