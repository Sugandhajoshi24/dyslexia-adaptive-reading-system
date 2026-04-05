import re


def clean_text(text):
    """
    Clean extracted text for all languages.
    Removes HTML, fixes PDF artifacts, strips invisible Unicode.
    Safe for Tamil, Hindi, and English.
    """
    if not text:
        return ""

    # ── Remove HTML tags ──────────────────────────────────
    text = re.sub(r'<.*?>', '', text, flags=re.DOTALL)

    # ── Remove leftover HTML fragments ────────────────────
    text = re.sub(r'</?div[^>]*>', '', text)
    text = re.sub(r'</?span[^>]*>', '', text)
    text = re.sub(r'</?p[^>]*>', '', text)

    # ── Fix broken hyphenation from PDFs ─────────────────
    # Only join when hyphen is at true line-break (preceded by letter,
    # followed by newline then letter) — avoids destroying compound words
    text = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', text)

    # ── Strip invisible and zero-width Unicode characters ─
    # These cause rendering boxes in Tamil and Hindi scripts
    INVISIBLE_CHARS = [
        '\u200A',  # Hair space
        '\u200B',  # Zero width space
        '\u200C',  # Zero width non-joiner — breaks Tamil conjuncts
        '\u200D',  # Zero width joiner
        '\u200E',  # Left-to-right mark
        '\u200F',  # Right-to-left mark
        '\u00AD',  # Soft hyphen
        '\uFEFF',  # BOM / Zero width no-break space
        '\uFFFD',  # Unicode replacement character (encoding failure)
        '\u2028',  # Line separator
        '\u2029',  # Paragraph separator
        '\u00A0',  # Non-breaking space — replace with normal space
        '\u202A',  # Left-to-right embedding
        '\u202B',  # Right-to-left embedding
        '\u202C',  # Pop directional formatting
        '\u202D',  # Left-to-right override
        '\u202E',  # Right-to-left override
    ]

    for ch in INVISIBLE_CHARS:
        if ch == '\u00A0':
            # Non-breaking space → regular space (don't delete)
            text = text.replace(ch, ' ')
        else:
            text = text.replace(ch, '')

    # ── Normalize spaces ──────────────────────────────────
    text = re.sub(r'[ \t]+', ' ', text)

    # ── Normalize newlines ────────────────────────────────
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()