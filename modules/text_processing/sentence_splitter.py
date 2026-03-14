import re

def split_into_lines(text):
    """
    Splits text into sentences for focus reading mode
    """

    sentences = re.split(r'(?<=[.!?])\s+', text)

    return [s.strip() for s in sentences if s.strip()]