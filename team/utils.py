from django.conf import settings
import re
import uuid
import os
import requests

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



def persist_image(image_url):
    file_name = str(uuid.uuid4()) + ".png"
    file_path = os.path.join(settings.DOWNLOAD_IMAGES_ROOT, file_name)
    print(f"Downloading {image_url} and writing to {file_path}")
    img_data = requests.get(image_url).content
    with open(file_path, 'wb') as handler:
        handler.write(img_data)
    return f'{settings.DOWNLOAD_IMAGES_URL}/{file_name}'

