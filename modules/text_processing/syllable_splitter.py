"""
Syllable splitting — multilingual.

English: uses pyphen
Hindi: uses indic_nlp_library or Unicode-based fallback
"""

import re
import pyphen

dic_en = pyphen.Pyphen(lang="en")

# Try to load indic NLP
try:
    from indicnlp.syllable import syllabifier as indic_syllabifier
    HAS_INDIC_NLP = True
except ImportError:
    HAS_INDIC_NLP = False


def syllabify_difficult_words(text, difficult_words, lang="en"):
    """
    Split difficult words into syllables.
    Language-aware: uses different engines for different scripts.
    """
    words = text.split()
    processed = []

    for word in words:
        clean_word = re.sub(r'[^\w\-]', '', word)

        if lang == "en":
            root = clean_word.lower()
        else:
            root = clean_word

        if root in difficult_words or root.lower() in difficult_words:
            syllabified = _syllabify_word(word, lang)
            processed.append(syllabified)
        else:
            processed.append(word)

    return " ".join(processed)


def _syllabify_word(word, lang):
    """Syllabify a single word based on language."""
    # Extract the core word (without punctuation)
    match = re.match(r'^([^\w]*)(.+?)([^\w]*)$', word)
    if not match:
        return word

    prefix = match.group(1)
    core = match.group(2)
    suffix = match.group(3)

    if lang == "en":
        syllabified = dic_en.inserted(core)
    elif lang == "hi":
        syllabified = _syllabify_hindi(core)
    else:
        syllabified = core

    return prefix + syllabified + suffix


def _syllabify_hindi(word):
    """
    Syllabify a Hindi word.
    Uses indic_nlp_library if available, otherwise Unicode-based fallback.
    """
    if HAS_INDIC_NLP:
        try:
            syllables = indic_syllabifier.orthographic_syllabify(word, 'hi')
            if syllables and len(syllables) > 1:
                return "-".join(syllables)
            return word
        except Exception:
            return _hindi_unicode_syllabify(word)
    else:
        return _hindi_unicode_syllabify(word)


def _hindi_unicode_syllabify(word):
    """
    Fallback: Split Hindi word on vowel boundaries using Unicode.

    Devanagari vowel marks (matras): ा ि ी ु ू े ै ो ौ ं ः ँ
    Split BEFORE consonants that follow a vowel mark or virama.
    """
    if not word:
        return word

    # Devanagari ranges
    vowel_marks = set('ािीुूेैोौंःँ\u094D')  # includes virama
    consonants = set('कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')

    result = []
    current = ""

    for i, char in enumerate(word):
        current += char

        # Check if we should split here
        if i < len(word) - 1:
            next_char = word[i + 1]

            # Split before a consonant if current ends with vowel mark
            if char in vowel_marks and next_char in consonants:
                result.append(current)
                current = ""
            # Split after virama + consonant cluster
            elif char == '\u094D' and i + 2 < len(word):
                # Don't split conjuncts
                pass

    if current:
        result.append(current)

    if len(result) > 1:
        return "-".join(result)
    return word