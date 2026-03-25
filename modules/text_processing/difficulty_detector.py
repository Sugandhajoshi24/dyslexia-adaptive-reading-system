"""
Difficulty detection — multilingual.
English: wordfreq + structural rules
Hindi: wordfreq + Devanagari complexity rules
"""

import re
import pyphen

try:
    from wordfreq import word_frequency, top_n_list
    HAS_WORDFREQ = True
    EASY_WORDS_EN = set(top_n_list('en', 2000))
    try:
        EASY_WORDS_HI = set(top_n_list('hi', 1000))
    except Exception:
        EASY_WORDS_HI = set()
except ImportError:
    HAS_WORDFREQ = False
    EASY_WORDS_EN = set()
    EASY_WORDS_HI = set()

dic_en = pyphen.Pyphen(lang="en")


def detect_difficult_words(text, lang="en"):
    """Detect difficult words based on language."""
    if lang == "hi":
        return _detect_hindi_difficult(text)
    else:
        return _detect_english_difficult(text)


def _detect_english_difficult(text):
    """English difficulty detection — unchanged from before."""
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    difficult_words = set()

    for word in words:
        clean = word.lower()
        if len(clean) < 5:
            continue

        syllables = dic_en.inserted(clean).split("-")
        syl_count = len(syllables)
        word_len = len(clean)

        if HAS_WORDFREQ:
            if clean in EASY_WORDS_EN:
                if word_len >= 11 and syl_count >= 4:
                    difficult_words.add(clean)
                continue

            freq = word_frequency(clean, 'en')

            if freq > 1e-4:
                if word_len >= 10 and syl_count >= 4:
                    difficult_words.add(clean)
                continue
            if freq > 1e-5:
                if (word_len >= 8 and syl_count >= 3) or syl_count >= 4:
                    difficult_words.add(clean)
                continue
            if freq > 1e-6:
                if word_len >= 7 and syl_count >= 2:
                    difficult_words.add(clean)
                elif syl_count >= 3:
                    difficult_words.add(clean)
                continue
            if word_len >= 6 or syl_count >= 2:
                difficult_words.add(clean)
        else:
            if word_len >= 8 or syl_count >= 3 or (word_len >= 6 and syl_count >= 2):
                difficult_words.add(clean)

    return difficult_words


def _detect_hindi_difficult(text):
    """
    Hindi difficulty detection.

    Criteria:
    1. Word length in characters (Hindi words tend to be shorter)
    2. Conjunct consonants (संयुक्त अक्षर) — visually complex
    3. Word frequency via wordfreq
    4. Rare/formal words
    """
    # Match Hindi words (Devanagari script)
    words = re.findall(r'[\u0900-\u097F]+', text)
    difficult_words = set()

    # Virama — indicates conjunct consonant
    virama = '\u094D'

    for word in words:
        if len(word) < 3:
            continue

        word_len = len(word)
        conjunct_count = word.count(virama)

        if HAS_WORDFREQ:
            if word in EASY_WORDS_HI:
                # Even easy words can be hard if very complex
                if word_len >= 8 and conjunct_count >= 2:
                    difficult_words.add(word)
                continue

            freq = word_frequency(word, 'hi')

            if freq > 1e-4:
                # Very common — only if structurally very complex
                if word_len >= 8 and conjunct_count >= 2:
                    difficult_words.add(word)
                continue

            if freq > 1e-5:
                if word_len >= 6 and conjunct_count >= 1:
                    difficult_words.add(word)
                continue

            if freq > 1e-6:
                if word_len >= 5 or conjunct_count >= 1:
                    difficult_words.add(word)
                continue

            # Rare word
            if word_len >= 4:
                difficult_words.add(word)
        else:
            # No wordfreq — structural rules only
            if word_len >= 6 or conjunct_count >= 1:
                difficult_words.add(word)

    return difficult_words


def get_word_difficulty_score(word, lang="en"):
    """Get difficulty score 0-10."""
    if lang == "hi":
        return _score_hindi(word)
    return _score_english(word)


def _score_english(word):
    clean = word.lower()
    if len(clean) < 3:
        return 0
    syllables = dic_en.inserted(clean).split("-")
    syl_count = len(syllables)
    word_len = len(clean)
    score = 0
    if word_len >= 12: score += 3
    elif word_len >= 9: score += 2
    elif word_len >= 7: score += 1
    if syl_count >= 5: score += 3
    elif syl_count >= 4: score += 2
    elif syl_count >= 3: score += 1
    if HAS_WORDFREQ:
        if clean in EASY_WORDS_EN:
            score = max(0, score - 2)
        else:
            freq = word_frequency(clean, 'en')
            if freq == 0: score += 4
            elif freq < 1e-7: score += 3
            elif freq < 1e-6: score += 2
            elif freq < 1e-5: score += 1
    return min(10, score)


def _score_hindi(word):
    if len(word) < 3:
        return 0
    score = 0
    word_len = len(word)
    conjuncts = word.count('\u094D')
    if word_len >= 10: score += 3
    elif word_len >= 7: score += 2
    elif word_len >= 5: score += 1
    if conjuncts >= 3: score += 3
    elif conjuncts >= 2: score += 2
    elif conjuncts >= 1: score += 1
    if HAS_WORDFREQ:
        freq = word_frequency(word, 'hi')
        if freq == 0: score += 4
        elif freq < 1e-7: score += 3
        elif freq < 1e-6: score += 2
        elif freq < 1e-5: score += 1
    return min(10, score)


def highlight_difficult_words(text, difficult_words, theme="Default",
                               font_family="Arial", lang="en", **kwargs):
    """Wrap difficult words in styled spans — works for any script."""
    words = text.split()
    highlighted = []

    is_dyslexic = "OpenDyslexic" in font_family

    if is_dyslexic:
        padding_style = "padding:0;border-radius:0;margin:0;"
    else:
        padding_style = "padding:0px 2px;border-radius:2px;"

    if theme == "High Contrast":
        hl = "background-color:#FFF176;color:#000;font-weight:500;" + padding_style + "display:inline;"
    elif theme == "Dark":
        hl = "background-color:rgba(255,213,79,0.18);color:#fff;" + padding_style + "display:inline;"
    elif theme == "Sepia":
        hl = "background-color:rgba(200,150,100,0.22);color:#3e2f1c;" + padding_style + "display:inline;"
    else:
        hl = "background-color:rgba(255,180,180,0.18);" + padding_style + "display:inline;"

    if is_dyslexic:
        if theme == "High Contrast":
            hl = "border-bottom:3px solid #FFF176;padding-bottom:1px;display:inline;"
        elif theme == "Dark":
            hl = "border-bottom:3px solid rgba(255,213,79,0.5);padding-bottom:1px;display:inline;"
        elif theme == "Sepia":
            hl = "border-bottom:3px solid rgba(200,150,100,0.5);padding-bottom:1px;display:inline;"
        else:
            hl = "border-bottom:3px solid rgba(255,150,150,0.5);padding-bottom:1px;display:inline;"

    for word in words:
        if lang == "hi":
            # For Hindi, match the word directly (Devanagari)
            core = re.sub(r'[^\u0900-\u097F]', '', word)
        else:
            clean_word = re.sub(r'[^\w\-]', '', word)
            core = clean_word.replace("-", "").lower()

        if core in difficult_words:
            highlighted.append("<span style='" + hl + "'>" + word + "</span>")
        else:
            highlighted.append(word)

    return " ".join(highlighted)