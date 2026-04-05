"""
Difficulty detection — multilingual.
English: wordfreq + structural rules
Hindi: wordfreq + Devanagari complexity rules
Tamil: wordfreq + Tamil script complexity rules
"""

import re
import html as html_module
import pyphen

try:
    from wordfreq import word_frequency, top_n_list
    HAS_WORDFREQ = True
    EASY_WORDS_EN = set(top_n_list('en', 2000))
    try:
        EASY_WORDS_HI = set(top_n_list('hi', 1000))
    except Exception:
        EASY_WORDS_HI = set()
    try:
        EASY_WORDS_TA = set(top_n_list('ta', 1000))
    except Exception:
        EASY_WORDS_TA = set()
except ImportError:
    HAS_WORDFREQ = False
    EASY_WORDS_EN = set()
    EASY_WORDS_HI = set()
    EASY_WORDS_TA = set()

dic_en = pyphen.Pyphen(lang="en")


def detect_difficult_words(text, lang="en"):
    """Detect difficult words based on language."""
    if lang == "hi":
        return _detect_hindi_difficult(text)
    elif lang == "ta":
        return _detect_tamil_difficult(text)
    else:
        return _detect_english_difficult(text)


def _detect_english_difficult(text):
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
    words = re.findall(r'[\u0900-\u097F]+', text)
    difficult_words = set()
    virama = '\u094D'

    for word in words:
        if len(word) < 3:
            continue
        word_len = len(word)
        conjunct_count = word.count(virama)

        if HAS_WORDFREQ:
            if word in EASY_WORDS_HI:
                if word_len >= 8 and conjunct_count >= 2:
                    difficult_words.add(word)
                continue
            freq = word_frequency(word, 'hi')
            if freq > 1e-4:
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
            if word_len >= 4:
                difficult_words.add(word)
        else:
            if word_len >= 6 or conjunct_count >= 1:
                difficult_words.add(word)

    return difficult_words


def _detect_tamil_difficult(text):
    """
    Tamil difficulty detection.

    Calibration notes:
    - Tamil words are naturally longer (agglutinative morphology)
    - Minimum length threshold raised to 4 chars (was 3)
    - Length thresholds raised throughout — long words are normal
    - Frequency thresholds kept same as before
    - Grantha letters (ஜஷஸஹ) still flagged — they are genuinely
      harder for dyslexic readers unfamiliar with Sanskrit loanwords
    """
    words = re.findall(r'[\u0B80-\u0BFF]+', text)
    difficult_words = set()
    pulli = '\u0BCD'
    grantha_letters = set('ஜஷஸஹ')

    for word in words:
        # Raised minimum — very short Tamil words are never difficult
        if len(word) < 4:
            continue

        word_len = len(word)
        conjunct_count = word.count(pulli)
        has_grantha = any(ch in grantha_letters for ch in word)

        if HAS_WORDFREQ:
            if word in EASY_WORDS_TA:
                # Even easy/common words flagged if truly complex
                if word_len >= 14 and conjunct_count >= 2:
                    difficult_words.add(word)
                elif has_grantha and word_len >= 10:
                    difficult_words.add(word)
                continue

            freq = word_frequency(word, 'ta')

            if freq > 1e-4:
                # Very common words — only flag if exceptionally complex
                if word_len >= 14 and conjunct_count >= 2:
                    difficult_words.add(word)
                elif has_grantha and word_len >= 8:
                    difficult_words.add(word)
                continue

            if freq > 1e-5:
                # Moderately common — flag if structurally complex
                if word_len >= 10 and conjunct_count >= 1:
                    difficult_words.add(word)
                elif has_grantha:
                    difficult_words.add(word)
                continue

            if freq > 1e-6:
                # Uncommon words
                if word_len >= 8 or conjunct_count >= 1:
                    difficult_words.add(word)
                continue

            # Rare words — flag if reasonably long
            if word_len >= 6:
                difficult_words.add(word)

        else:
            # No wordfreq — structural rules only
            # Thresholds raised for Tamil's natural word length
            if word_len >= 10 or conjunct_count >= 1 or has_grantha:
                difficult_words.add(word)

    return difficult_words


def get_word_difficulty_score(word, lang="en"):
    if lang == "hi":
        return _score_hindi(word)
    elif lang == "ta":
        return _score_tamil(word)
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


def _score_tamil(word):
    if len(word) < 3:
        return 0
    score = 0
    word_len = len(word)
    conjuncts = word.count('\u0BCD')
    grantha_letters = set('ஜஷஸஹ')
    has_grantha = any(ch in grantha_letters for ch in word)
    if word_len >= 12: score += 3
    elif word_len >= 8: score += 2
    elif word_len >= 5: score += 1
    if conjuncts >= 3: score += 3
    elif conjuncts >= 2: score += 2
    elif conjuncts >= 1: score += 1
    if has_grantha: score += 1
    if HAS_WORDFREQ:
        freq = word_frequency(word, 'ta')
        if freq == 0: score += 4
        elif freq < 1e-7: score += 3
        elif freq < 1e-6: score += 2
        elif freq < 1e-5: score += 1
    return min(10, score)


def _extract_core(word, lang):
    """
    Extract the plain word core for difficulty matching.
    Strips HTML tags first (handles bionic <b> tags inside the word).
    """
    # Remove all HTML tags
    plain = re.sub(r'<[^>]+>', '', word)

    if lang == "hi":
        return re.sub(r'[^\u0900-\u097F]', '', plain)
    elif lang == "ta":
        return re.sub(r'[^\u0B80-\u0BFF]', '', plain)
    else:
        clean = re.sub(r'[^\w\-]', '', plain)
        return clean.replace("-", "").lower()


def highlight_difficult_words(text, difficult_words, theme="Default",
                               font_family="Arial", lang="en",
                               enable_tooltip=True,
                               bionic_reader_fn=None,
                               bold_ratio=0.4,
                               **kwargs):
    """
    Wrap difficult words in styled spans.

    If bionic_reader_fn is provided, applies bionic to EVERY word
    in a single pass — this ensures highlighted words also get
    bionic formatting correctly.

    bionic_reader_fn: callable that takes (word_text, bold_ratio) -> html_string
    """
    words = text.split()
    highlighted = []

    is_dyslexic = "OpenDyslexic" in font_family
    show_tooltip = (lang == "en" and enable_tooltip)

    if is_dyslexic:
        padding_style = "padding:0;border-radius:0;margin:0;"
    else:
        padding_style = "padding:0px 2px;border-radius:2px;"

    if theme == "High Contrast":
        hl = ("background-color:#FFF176;color:#000;font-weight:500;"
              + padding_style + "display:inline;")
    elif theme == "Dark":
        hl = ("background-color:rgba(255,213,79,0.18);color:#fff;"
              + padding_style + "display:inline;")
    elif theme == "Sepia":
        hl = ("background-color:rgba(200,150,100,0.22);color:#3e2f1c;"
              + padding_style + "display:inline;")
    else:
        hl = ("background-color:rgba(255,180,180,0.18);"
              + padding_style + "display:inline;")

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
        # Get the plain word for difficulty matching
        core = _extract_core(word, lang)

        # Apply bionic to the display word if bionic function provided
        if bionic_reader_fn is not None:
            display_word = bionic_reader_fn(word, bold_ratio)
        else:
            display_word = word

        if core in difficult_words:
            if show_tooltip:
                safe_core = html_module.escape(core)
                highlighted.append(
                    "<span class='difficult-word tooltip-trigger' style='"
                    + hl + "position:relative;cursor:help;' "
                    + "data-word='" + safe_core + "'>"
                    + display_word
                    +"<span class='tooltip-content'></span>"
                    + "</span>"
                )
            else:
                highlighted.append(
                    "<span class='difficult-word' style='" + hl + "'>"
                    + display_word + "</span>"
                )
        else:
            highlighted.append(display_word)

    return " ".join(highlighted)