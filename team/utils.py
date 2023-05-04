def approximate_word_count(text):
    '''
    Function that takes a string of text and returns an approximate word count
    '''
    # Remove all non-word characters
    text = re.sub(r'\W', ' ', text)
    # Split the string into a list of words
    words = text.split()
    # Count the words
    count = len(words)
    return count
#test_string = "This is a test string with 12 words"
#print(approximate_word_count(test_string)) # Output: 12 lol

