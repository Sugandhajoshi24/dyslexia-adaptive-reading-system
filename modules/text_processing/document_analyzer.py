"""
Document difficulty analysis — multilingual.
"""

import re
import pyphen

try:
    from wordfreq import word_frequency
    HAS_WORDFREQ = True
except ImportError:
    HAS_WORDFREQ = False

dic_en = pyphen.Pyphen(lang="en")


def analyze_document(text, difficult_words, lang="en"):
    """Analyze document difficulty — language aware."""
    if lang == "hi":
        return _analyze_hindi(text, difficult_words)
    elif lang == "ta":
        return _analyze_tamil(text, difficult_words)
    else:
        return _analyze_english(text, difficult_words)


def _analyze_english(text, difficult_words):
    """English document analysis using Flesch-Kincaid."""
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    total_words = len(words)
    total_sentences = max(1, len(sentences))

    if total_words == 0:
        return _empty_result()

    total_syllables = 0
    for word in words:
        syls = dic_en.inserted(word.lower()).split("-")
        total_syllables += max(1, len(syls))

    avg_word_length = sum(len(w) for w in words) / total_words
    avg_sentence_length = total_words / total_sentences
    avg_syllables = total_syllables / total_words

    fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables - 15.59
    fk_grade = max(0, round(fk_grade, 1))

    fk_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
    fk_ease = max(0, min(100, round(fk_ease, 1)))

    difficult_count = len(difficult_words)
    difficult_pct = round((difficult_count / total_words) * 100, 1) if total_words > 0 else 0

    difficulty_level = _calculate_level(fk_grade, difficult_pct, avg_sentence_length)
    reading_time = round(total_words / 120, 1)

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


def _analyze_hindi(text, difficult_words):
    """Hindi document analysis using custom complexity."""
    words = re.findall(r'[\u0900-\u097F]+', text)
    english_words = re.findall(r'\b[a-zA-Z]+\b', text)
    all_word_count = len(words) + len(english_words)

    sentences = re.split(r'[।.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    total_words = max(1, all_word_count)
    total_sentences = max(1, len(sentences))

    if total_words <= 1:
        return _empty_result()

    avg_word_length = sum(len(w) for w in words) / max(1, len(words)) if words else 0
    avg_sentence_length = total_words / total_sentences

    virama_count = text.count('\u094D')
    avg_conjuncts = virama_count / max(1, len(words)) if words else 0

    difficult_count = len(difficult_words)
    difficult_pct = round((difficult_count / total_words) * 100, 1)

    complexity_score = (
        avg_sentence_length * 0.4 +
        avg_word_length * 1.5 +
        avg_conjuncts * 3.0
    )

    if complexity_score >= 15:
        fk_grade = 12.0
    elif complexity_score >= 12:
        fk_grade = 10.0
    elif complexity_score >= 9:
        fk_grade = 8.0
    elif complexity_score >= 6:
        fk_grade = 5.0
    else:
        fk_grade = 3.0

    fk_ease = max(0, min(100, round(100 - complexity_score * 5, 1)))

    difficulty_level = _calculate_level(fk_grade, difficult_pct, avg_sentence_length)
    reading_time = round(total_words / 100, 1)

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
        "avg_syllables_per_word": round(avg_conjuncts, 2),
        "reading_time_minutes": reading_time,
    }


def _analyze_tamil(text, difficult_words):
    """
    Tamil document analysis.
    Uses word length and pulli (conjunct) complexity.

    Formula notes:
    - Tamil is agglutinative — long words are structurally normal
    - avg_word_length weighted at 0.7 (lower than Hindi's 1.5)
      because Tamil word length alone is not a strong difficulty signal
    - The ease multiplier is 3.5 (not 5) to avoid clamping to 0
      on normal Tamil text with naturally long words
    """
    words = re.findall(r'[\u0B80-\u0BFF]+', text)
    english_words = re.findall(r'\b[a-zA-Z]+\b', text)
    all_word_count = len(words) + len(english_words)

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    total_words = max(1, all_word_count)
    total_sentences = max(1, len(sentences))

    if total_words <= 1:
        return _empty_result()

    avg_word_length = (
        sum(len(w) for w in words) / max(1, len(words))
        if words else 0
    )
    avg_sentence_length = total_words / total_sentences

    pulli_count = text.count('\u0BCD')
    avg_conjuncts = pulli_count / max(1, len(words)) if words else 0

    difficult_count = len(difficult_words)
    difficult_pct = round((difficult_count / total_words) * 100, 1)

    # ── Complexity formula ────────────────────────────────────────
    # Tamil-specific weights:
    # - sentence length: 0.4 (same as Hindi)
    # - word length: 0.7 (reduced — long words are normal in Tamil)
    # - conjuncts: 3.0 (slightly reduced — pulli less common than virama)
    # Multiplier: 3.5 (reduced from 5 — prevents clamping to 0)
    complexity_score = (
        avg_sentence_length * 0.4 +
        avg_word_length * 0.7 +
        avg_conjuncts * 3.0
    )

    fk_ease = max(0, min(100, round(100 - complexity_score * 3.5, 1)))

    # Map complexity to grade level
    if complexity_score >= 15:
        fk_grade = 12.0
    elif complexity_score >= 12:
        fk_grade = 10.0
    elif complexity_score >= 9:
        fk_grade = 8.0
    elif complexity_score >= 6:
        fk_grade = 5.0
    else:
        fk_grade = 3.0

    difficulty_level = _calculate_level(fk_grade, difficult_pct, avg_sentence_length)
    reading_time = round(total_words / 100, 1)

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
        "avg_syllables_per_word": round(avg_conjuncts, 2),
        "reading_time_minutes": reading_time,
    }

def _calculate_level(fk_grade, difficult_pct, avg_sent_len):
    """Determine overall difficulty level."""
    score = 0

    if fk_grade >= 12:
        score += 3
    elif fk_grade >= 8:
        score += 2
    elif fk_grade >= 5:
        score += 1

    if difficult_pct >= 15:
        score += 3
    elif difficult_pct >= 8:
        score += 2
    elif difficult_pct >= 4:
        score += 1

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