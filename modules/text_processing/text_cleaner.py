import re

def clean_text(text):

    # keep line breaks but remove extra spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # normalize multiple new lines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # trim spaces
    text = text.strip()

    return text