"""
Hindi word segmentation (display-only).

Goal:
    - segment Hindi words into akshara/orthographic chunks
    - only for visual support
    - never used for speech text
    - safe fallback: if segmentation fails, return original word
"""

import re

try:
    from indicnlp.syllable import syllabifier as indic_syllabifier
    HAS_INDIC_SYLLABIFIER = True
except ImportError:
    HAS_INDIC_SYLLABIFIER = False


# Devanagari helpers
DEVANAGARI_WORD_RE = re.compile(r'^([^\u0900-\u097F]*)([\u0900-\u097F]+)([^\u0900-\u097F]*)$')

VOWEL_SIGNS_AND_MARKS = set([
    'ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ',
    'े', 'ै', 'ो', 'ौ',
    'ं', 'ः', 'ँ', '़', 'ॅ', 'ॉ'
])

VIRAMA = '्'


def segment_hindi_text(text, difficult_words=None, only_difficult=True, separator="·"):
    """
    Segment Hindi words in a text.

    Args:
        text: input Hindi text
        difficult_words: set of difficult words (Hindi roots)
        only_difficult: if True, segment only difficult words
        separator: visual separator between chunks

    Returns:
        Segmented display text
    """
    if difficult_words is None:
        difficult_words = set()

    words = text.split()
    output = []

    for word in words:
        segmented = segment_hindi_word(
            word,
            difficult_words=difficult_words,
            only_difficult=only_difficult,
            separator=separator
        )
        output.append(segmented)

    return " ".join(output)


def segment_hindi_word(word, difficult_words=None, only_difficult=True, separator="·"):
    """
    Segment a single Hindi word safely.

    Preserves punctuation around the word.
    """
    if difficult_words is None:
        difficult_words = set()

    match = DEVANAGARI_WORD_RE.match(word)
    if not match:
        return word

    prefix = match.group(1)
    core = match.group(2)
    suffix = match.group(3)

    # If only difficult words should be segmented, check membership
    if only_difficult:
        if core not in difficult_words:
            return word

    segmented_core = _segment_core(core, separator=separator)

    return prefix + segmented_core + suffix


def _segment_core(core, separator="·"):
    """
    Segment the Devanagari core.

    Preferred:
        - indic_nlp orthographic syllables

    Fallback:
        - safe akshara-like chunking using virama and vowel signs
    """
    if not core or len(core) <= 1:
        return core

    # Try indic_nlp first
    if HAS_INDIC_SYLLABIFIER:
        try:
            pieces = indic_syllabifier.orthographic_syllabify(core, "hi")
            if pieces and len(pieces) > 1:
                return separator.join(pieces)
        except Exception:
            pass

    # Fallback
    pieces = _fallback_akshara_segment(core)
    if len(pieces) > 1:
        return separator.join(pieces)

    return core


def _fallback_akshara_segment(text):
    """
    Approximate akshara segmentation.

    Rules:
        - keep vowel signs with their base consonant
        - keep virama + next consonant in same cluster
        - keep anusvara/chandrabindu/visarga with current cluster

    This is not perfect linguistic syllabification,
    but it is much safer than arbitrary splitting.
    """
    if not text:
        return [text]

    units = []
    i = 0
    n = len(text)

    while i < n:
        unit = text[i]
        i += 1

        while i < n:
            ch = text[i]

            # Attach marks/matras/nukta/anusvara etc.
            if ch in VOWEL_SIGNS_AND_MARKS:
                unit += ch
                i += 1
                continue

            # Attach virama + next consonant as same cluster
            if ch == VIRAMA and i + 1 < n:
                unit += ch + text[i + 1]
                i += 2
                continue

            break

        units.append(unit)

    return units