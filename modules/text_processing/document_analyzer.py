"""
Document difficulty analysis.

Provides:
    - Flesch-Kincaid readability score
    - Difficulty level (Easy/Medium/Hard/Advanced)
    - Word statistics
    - Sentence statistics
"""

import re
import pyphen

try:
    from wordfreq import word_frequency
    HAS_WORDFREQ = True
except ImportError:
    HAS_WORDFREQ = False

dic = pyphen.Pyphen(lang="en")


def analyze_document(text, difficult_words):
    """
    Analyze document difficulty.

    Returns a dict with:
        - flesch_kincaid_grade: grade level (float)
        - difficulty_level: Easy / Medium / Hard / Advanced
        - total_words: int
        - total_sentences: int
        - difficult_word_count: int
        - difficult_word_pct: float (percentage)
        - avg_word_length: float
        - avg_sentence_length: float
        - avg_syllables_per_word: float
        - reading_time_minutes: float
    """
    # Extract words and sentences
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    total_words = len(words)
    total_sentences = max(1, len(sentences))

    if total_words == 0:
        return _empty_result()

    # Syllable count
    total_syllables = 0
    for word in words:
        syls = dic.inserted(word.lower()).split("-")
        total_syllables += max(1, len(syls))

    # Averages
    avg_word_length = sum(len(w) for w in words) / total_words
    avg_sentence_length = total_words / total_sentences
    avg_syllables = total_syllables / total_words

    # Flesch-Kincaid Grade Level
    fk_grade = (
        0.39 * avg_sentence_length +
        11.8 * avg_syllables -
        15.59
    )
    fk_grade = max(0, round(fk_grade, 1))

    # Flesch Reading Ease (for reference)
    fk_ease = (
        206.835 -
        1.015 * avg_sentence_length -
        84.6 * avg_syllables
    )
    fk_ease = max(0, min(100, round(fk_ease, 1)))

    # Difficult word stats
    difficult_count = len(difficult_words)
    difficult_pct = round((difficult_count / total_words) * 100, 1) if total_words > 0 else 0

    # Difficulty level
    difficulty_level = _calculate_difficulty_level(
        fk_grade, difficult_pct, avg_sentence_length
    )

    # Reading time (average reading speed ~200 words/min for dyslexic readers)
    reading_time = round(total_words / 120, 1)  # 120 wpm for dyslexic readers

    return {
        "flesch_kincaid_grade": fk_grade,
        "flesch_reading_ease": fk_ease,
        "difficulty_level": difficulty_level,
        "total_words": total_words,
        "total_sentences": total_sentences,
        "difficult_word_count": difficult_count,
        "difficult_word_pct": difficult_pct,
        "avg_word_length": round(avg_word_length, 1),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_syllables_per_word": round(avg_syllables, 2),
        "reading_time_minutes": reading_time,
    }


def _calculate_difficulty_level(fk_grade, difficult_pct, avg_sent_len):
    """Determine overall difficulty level."""
    score = 0

    # Grade level component
    if fk_grade >= 12:
        score += 3
    elif fk_grade >= 8:
        score += 2
    elif fk_grade >= 5:
        score += 1

    # Difficult word percentage
    if difficult_pct >= 15:
        score += 3
    elif difficult_pct >= 8:
        score += 2
    elif difficult_pct >= 4:
        score += 1

    # Sentence length
    if avg_sent_len >= 25:
        score += 2
    elif avg_sent_len >= 18:
        score += 1

    if score >= 7:
        return "Advanced"
    elif score >= 4:
        return "Hard"
    elif score >= 2:
        return "Medium"
    else:
        return "Easy"


def _empty_result():
    """Return empty analysis for edge cases."""
    return {
        "flesch_kincaid_grade": 0,
        "flesch_reading_ease": 100,
        "difficulty_level": "Easy",
        "total_words": 0,
        "total_sentences": 0,
        "difficult_word_count": 0,
        "difficult_word_pct": 0,
        "avg_word_length": 0,
        "avg_sentence_length": 0,
        "avg_syllables_per_word": 0,
        "reading_time_minutes": 0,
    }