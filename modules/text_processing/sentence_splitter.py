"""
Sentence splitting — multilingual.
Single source of truth for splitting text into sentences.
"""

import re


def split_into_lines(text, lang="en"):
    """
    Split text into sentences for focus reading mode.

    Language-aware:
    - English: splits on . ! ?
    - Hindi: also splits on । (purna viram)
    - Tamil: splits on . ! ? (Tamil uses standard punctuation)
    """
    if lang == "hi":
        sentences = re.split(r'(?<=[।.!?])\s+', text)
    elif lang == "ta":
        # Tamil uses standard punctuation (no special sentence-end character)
        sentences = re.split(r'(?<=[.!?])\s+', text)
    else:
        sentences = re.split(r'(?<=[.!?])\s+', text)

    return [s.strip() for s in sentences if s.strip()]