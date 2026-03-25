"""
Text processing pipeline — multilingual.
"""

import re

from modules.text_processing.difficulty_detector import (
    detect_difficult_words, highlight_difficult_words
)
from modules.text_processing.syllable_splitter import syllabify_difficult_words
from modules.text_processing.bionic_reader import apply_bionic_reading
from modules.config.language_config import get_language_config


def process_text(original_text, settings):
    """Run the full text processing pipeline."""
    lang = settings.get("language", "en")
    lang_config = get_language_config(lang)

    difficult_words = detect_difficult_words(original_text, lang=lang)

    tts_text = original_text
    reader_text = original_text

    # Syllable splitting — only for English
    if settings.get("use_syllables", False) and lang == "en":
        reader_text = syllabify_difficult_words(reader_text, difficult_words, lang=lang)

    pdf_text = reader_text

    if settings.get("highlight_difficulty", False):
        reader_text = highlight_difficult_words(
            reader_text, difficult_words,
            theme=settings.get("theme_name", "Light"),
            font_family=settings.get("font_family", "Arial"),
            lang=lang
        )

    if settings.get("bionic_reading", False) and lang_config.get("bionic_support", False):
        if settings.get("reading_mode", "") != "🔊 Guided Reading":
            reader_text = apply_bionic_reading(reader_text)

    return {
        "original_text": original_text,
        "difficult_words": difficult_words,
        "tts_text": tts_text,
        "reader_text": reader_text,
        "pdf_text": pdf_text,
    }


def process_sentence(sentence, difficult_words, settings):
    """Process a single sentence."""
    lang = settings.get("language", "en")
    lang_config = get_language_config(lang)
    result = sentence

    if settings.get("use_syllables", False) and lang == "en":
        result = syllabify_difficult_words(result, difficult_words, lang=lang)

    if settings.get("highlight_difficulty", False):
        result = highlight_difficult_words(
            result, difficult_words,
            theme=settings.get("theme_name", "Light"),
            font_family=settings.get("font_family", "Arial"),
            lang=lang
        )

    if settings.get("bionic_reading", False) and lang_config.get("bionic_support", False):
        result = apply_bionic_reading(result)

    return result


def split_into_sentences(text, min_length=8, lang="en"):
    """Split text into sentences — language aware."""
    if lang == "hi":
        sentences = re.split(r'(?<=[।.!?])\s+', text.strip())
    else:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    return [s.strip() for s in sentences if len(s.strip()) > min_length]