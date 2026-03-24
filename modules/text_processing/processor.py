"""
Text processing pipeline orchestrator.
"""

import re

from modules.text_processing.difficulty_detector import (
    detect_difficult_words, highlight_difficult_words
)
from modules.text_processing.syllable_splitter import syllabify_difficult_words
from modules.text_processing.bionic_reader import apply_bionic_reading


def process_text(original_text, settings):
    """
    Run the full text processing pipeline.
    Returns dict with all text versions.
    """
    difficult_words = detect_difficult_words(original_text)

    tts_text = original_text
    reader_text = original_text

    if settings["use_syllables"]:
        reader_text = syllabify_difficult_words(reader_text, difficult_words)

    pdf_text = reader_text

    if settings["highlight_difficulty"]:
        reader_text = highlight_difficult_words(
            reader_text, difficult_words,
            theme=settings["theme_name"],
            font_family=settings["font_family"]
        )

    # Bionic reading — only in Normal and Focus modes, NOT guided
    # Guided mode needs clean word boundaries for speech sync
    if settings.get("bionic_reading", False):
        if settings["reading_mode"] != "🔊 Guided Reading":
            reader_text = apply_bionic_reading(reader_text)

    return {
        "original_text": original_text,
        "difficult_words": difficult_words,
        "tts_text": tts_text,
        "reader_text": reader_text,
        "pdf_text": pdf_text,
    }


def process_sentence(sentence, difficult_words, settings):
    """Process a single sentence for Focus Mode."""
    result = sentence

    if settings["use_syllables"]:
        result = syllabify_difficult_words(result, difficult_words)

    if settings["highlight_difficulty"]:
        result = highlight_difficult_words(
            result, difficult_words,
            theme=settings["theme_name"],
            font_family=settings["font_family"]
        )

    if settings.get("bionic_reading", False):
        result = apply_bionic_reading(result)

    return result


def split_into_sentences(text, min_length=8):
    """Split text into sentences, filtering short fragments."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > min_length]