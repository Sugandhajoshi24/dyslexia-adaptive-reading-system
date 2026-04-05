"""
Tamil word segmentation (display-only).

Goal:
    - segment Tamil words into orthographic syllable chunks
    - only for visual support
    - never used for speech text
    - safe fallback: if segmentation fails, return original word

Tamil script structure:
    - Consonants: க-ஹ
    - Vowels: அ-ஔ
    - Vowel signs (matras): ா ி ீ ு ூ ெ ே ை ொ ோ ௌ
    - Pulli (virama): ் — marks pure consonant / conjunct
    - Anusvara: ஂ
    - Visarga: ஃ
"""

import re

try:
    from indicnlp.syllable import syllabifier as indic_syllabifier
    HAS_INDIC_SYLLABIFIER = True
except ImportError:
    HAS_INDIC_SYLLABIFIER = False


# Tamil Unicode helpers
TAMIL_WORD_RE = re.compile(r'^([^\u0B80-\u0BFF]*)([\u0B80-\u0BFF]+)([^\u0B80-\u0BFF]*)$')

# Tamil vowel signs (matras) and marks
TAMIL_VOWEL_SIGNS = set([
    'ா', 'ி', 'ீ', 'ு', 'ூ',
    'ெ', 'ே', 'ை',
    'ொ', 'ோ', 'ௌ',
    'ஂ', 'ஃ',
])

# Tamil pulli (virama)
TAMIL_PULLI = '்'

# Tamil consonants
TAMIL_CONSONANTS = set(
    'கஙசஞடணதநபமயரலவழளறனஜஷஸஹ'
)


def segment_tamil_text(text, difficult_words=None, only_difficult=True, separator="·"):
    """
    Segment Tamil words in a text.

    Args:
        text: input Tamil text
        difficult_words: set of difficult words
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
        segmented = segment_tamil_word(
            word,
            difficult_words=difficult_words,
            only_difficult=only_difficult,
            separator=separator
        )
        output.append(segmented)

    return " ".join(output)


def segment_tamil_word(word, difficult_words=None, only_difficult=True, separator="·"):
    """
    Segment a single Tamil word safely.
    Preserves punctuation around the word.
    """
    if difficult_words is None:
        difficult_words = set()

    match = TAMIL_WORD_RE.match(word)
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
    Segment the Tamil core word.

    Preferred: indic_nlp orthographic syllables
    Fallback: safe akshara-like chunking using pulli and vowel signs
    """
    if not core or len(core) <= 1:
        return core

    # Try indic_nlp first
    if HAS_INDIC_SYLLABIFIER:
        try:
            pieces = indic_syllabifier.orthographic_syllabify(core, "ta")
            if pieces and len(pieces) > 1:
                return separator.join(pieces)
        except Exception:
            pass

    # Fallback
    pieces = _fallback_tamil_segment(core)
    if len(pieces) > 1:
        return separator.join(pieces)

    return core


def _fallback_tamil_segment(text):
    """
    Approximate Tamil syllable segmentation.

    Rules:
        - Keep vowel signs with their base consonant
        - Keep pulli + next consonant in same cluster (conjunct)
        - Keep anusvara/visarga with current cluster
        - Handle two-part vowel signs (ொ = ெ + ா, ோ = ே + ா, ௌ = ெ + ௗ)

    This is approximate but safe — better than arbitrary splitting.
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

            # Attach vowel signs and marks
            if ch in TAMIL_VOWEL_SIGNS:
                unit += ch
                i += 1
                continue

            # Attach pulli + next consonant as same cluster
            if ch == TAMIL_PULLI and i + 1 < n and text[i + 1] in TAMIL_CONSONANTS:
                unit += ch + text[i + 1]
                i += 2
                continue

            # Standalone pulli (word-final) — attach to current unit
            if ch == TAMIL_PULLI:
                unit += ch
                i += 1
                continue

            break

        units.append(unit)

    return units