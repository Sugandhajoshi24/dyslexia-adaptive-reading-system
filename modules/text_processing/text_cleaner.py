import re

def clean_text(text):

    # Remove ANY html tags
    text = re.sub(r'<.*?>', '', text, flags=re.DOTALL)

    # Remove leftover html fragments
    text = re.sub(r'</?div[^>]*>', '', text)
    text = re.sub(r'</?span[^>]*>', '', text)
    text = re.sub(r'</?p[^>]*>', '', text)

    # Fix broken hyphenation from PDFs
    text = re.sub(r'-\n', '', text)

    # Normalize spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()