"""
Auto-detect language from text using Unicode script analysis.
"""

import re


def detect_language(text):
    """
    Detect language from text based on character scripts.

    Returns language code: 'en', 'hi', 'ta', etc.
    """
    if not text or len(text.strip()) < 10:
        return "en"

    # Count characters in each script
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    tamil_count = len(re.findall(r'[\u0B80-\u0BFF]', text))
    latin_count = len(re.findall(r'[a-zA-Z]', text))

    total = devanagari_count + tamil_count + latin_count

    if total == 0:
        return "en"

    # Whichever script has the most characters wins
    if devanagari_count > latin_count and devanagari_count > tamil_count:
        return "hi"
    elif tamil_count > latin_count and tamil_count > devanagari_count:
        return "ta"
    else:
        return "en"


def get_script_name(lang_code):
    """Return human-readable script name."""
    scripts = {
        "en": "Latin",
        "hi": "Devanagari",
        "ta": "Tamil",
    }
    return scripts.get(lang_code, "Latin")