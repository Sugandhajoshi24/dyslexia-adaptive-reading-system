"""
Bionic Reading Mode.
Bolds the first portion of each word for faster reading.
"""

import re

BIONIC_BOLD_RATIO = 0.4


def apply_bionic_reading(text, bold_ratio=None):
    """
    Apply bionic reading formatting to text.
    Each word gets its first N characters wrapped in <b> tags.
    Preserves existing HTML tags (highlights, etc.)
    """
    if bold_ratio is None:
        bold_ratio = BIONIC_BOLD_RATIO

    # Split text into HTML tags and text segments
    parts = re.split(r'(<[^>]+>)', text)

    result = []
    for part in parts:
        if part.startswith('<'):
            # HTML tag — keep as-is
            result.append(part)
        else:
            # Text segment — apply bionic to each word
            result.append(_bionic_segment(part, bold_ratio))

    return ''.join(result)


def _bionic_segment(segment, bold_ratio):
    """Apply bionic formatting to a plain text segment."""
    if not segment.strip():
        return segment

    words = segment.split(' ')
    processed = []

    for word in words:
        if not word or not any(c.isalpha() for c in word):
            processed.append(word)
            continue

        # Find the actual letters in the word
        # Preserve leading/trailing punctuation
        match = re.match(r'^([^a-zA-Z]*)([a-zA-Z][a-zA-Z\-]*[a-zA-Z]|[a-zA-Z])([^a-zA-Z]*)$', word)

        if match:
            prefix = match.group(1)
            core = match.group(2)
            suffix = match.group(3)

            if len(core) <= 1:
                processed.append(word)
            else:
                bold_len = max(1, int(len(core) * bold_ratio + 0.5))
                bold_part = core[:bold_len]
                rest_part = core[bold_len:]
                processed.append(f"{prefix}<b>{bold_part}</b>{rest_part}{suffix}")
        else:
            processed.append(word)

    return ' '.join(processed)