"""
Difficulty detection: combined frequency + structural rules.
"""

import re
import pyphen

try:
    from wordfreq import word_frequency, top_n_list
    HAS_WORDFREQ = True
    EASY_WORDS = set(top_n_list('en', 2000))
except ImportError:
    HAS_WORDFREQ = False
    EASY_WORDS = set()

dic = pyphen.Pyphen(lang="en")


def detect_difficult_words(text):
    """Detect difficult words using combined frequency + structure."""
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    difficult_words = set()

    for word in words:
        clean = word.lower()

        if len(clean) < 5:
            continue

        syllables = dic.inserted(clean).split("-")
        syl_count = len(syllables)
        word_len = len(clean)

        if HAS_WORDFREQ:
            if clean in EASY_WORDS:
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
            if (
                word_len >= 8 or
                syl_count >= 3 or
                (word_len >= 6 and syl_count >= 2)
            ):
                difficult_words.add(clean)

    return difficult_words


def get_word_difficulty_score(word):
    """Get difficulty score 0-10 for document analysis."""
    clean = word.lower()
    if len(clean) < 3:
        return 0

    syllables = dic.inserted(clean).split("-")
    syl_count = len(syllables)
    word_len = len(clean)

    score = 0

    if word_len >= 12:
        score += 3
    elif word_len >= 9:
        score += 2
    elif word_len >= 7:
        score += 1

    if syl_count >= 5:
        score += 3
    elif syl_count >= 4:
        score += 2
    elif syl_count >= 3:
        score += 1

    if HAS_WORDFREQ:
        if clean in EASY_WORDS:
            score = max(0, score - 2)
        else:
            freq = word_frequency(clean, 'en')
            if freq == 0:
                score += 4
            elif freq < 1e-7:
                score += 3
            elif freq < 1e-6:
                score += 2
            elif freq < 1e-5:
                score += 1

    return min(10, score)


def highlight_difficult_words(
    text,
    difficult_words,
    theme="Default",
    font_family="Arial",
    **kwargs
):
    """Wrap difficult words in styled <span> tags."""
    words = text.split()
    highlighted_words = []

    is_dyslexic = "OpenDyslexic" in font_family

    # KEY FIX: OpenDyslexic gets NO padding, NO border-radius
    # This prevents the overlapping boxes
    if is_dyslexic:
        padding_style = "padding:0;border-radius:0;margin:0;"
    else:
        padding_style = "padding:0px 2px;border-radius:2px;"

    if theme == "High Contrast":
        highlight_style = f"background-color:#FFF176;color:#000;font-weight:500;{padding_style}display:inline;"
    elif theme == "Dark":
        highlight_style = f"background-color:rgba(255,213,79,0.18);color:#fff;{padding_style}display:inline;"
    elif theme == "Sepia":
        highlight_style = f"background-color:rgba(200,150,100,0.22);color:#3e2f1c;{padding_style}display:inline;"
    else:
        highlight_style = f"background-color:rgba(255,180,180,0.18);{padding_style}display:inline;"

    # Additional fix for OpenDyslexic: use underline instead of background
    if is_dyslexic:
        if theme == "High Contrast":
            highlight_style = "border-bottom:3px solid #FFF176;padding-bottom:1px;display:inline;"
        elif theme == "Dark":
            highlight_style = "border-bottom:3px solid rgba(255,213,79,0.5);padding-bottom:1px;display:inline;"
        elif theme == "Sepia":
            highlight_style = "border-bottom:3px solid rgba(200,150,100,0.5);padding-bottom:1px;display:inline;"
        else:
            highlight_style = "border-bottom:3px solid rgba(255,150,150,0.5);padding-bottom:1px;display:inline;"

    for word in words:
        clean_word = re.sub(r'[^\w\-]', '', word)
        root_word = clean_word.replace("-", "").lower()

        if root_word in difficult_words:
            highlighted_words.append(
                f"<span style='{highlight_style}'>{word}</span>"
            )
        else:
            highlighted_words.append(word)

    return " ".join(highlighted_words)