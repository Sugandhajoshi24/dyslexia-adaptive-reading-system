"""
Text processing pipeline — multilingual.
"""

import re

from modules.text_processing.difficulty_detector import (
    detect_difficult_words,
    highlight_difficult_words
)
from modules.text_processing.syllable_splitter import syllabify_difficult_words
from modules.text_processing.bionic_reader import apply_bionic_reading, _bionic_word
from modules.text_processing.hindi_segmenter import segment_hindi_text
from modules.text_processing.tamil_segmenter import segment_tamil_text
from modules.config.language_config import get_language_config
from modules.text_processing.sentence_splitter import split_into_lines

BIONIC_BOLD_RATIO = 0.4


def _apply_segmentation(text, lang, difficult_words, separator="·"):
    """Apply language-appropriate segmentation."""
    if lang == "en":
        return syllabify_difficult_words(text, difficult_words, lang=lang)
    elif lang == "hi":
        return segment_hindi_text(
            text, difficult_words=difficult_words,
            only_difficult=True, separator=separator
        )
    elif lang == "ta":
        return segment_tamil_text(
            text, difficult_words=difficult_words,
            only_difficult=True, separator=separator
        )
    return text


def _make_bionic_fn(lang_config):
    """
    Return a per-word bionic function if bionic is supported,
    otherwise return None.
    """
    if not lang_config.get("bionic_support", False):
        return None

    def bionic_word_fn(word, bold_ratio):
        return _bionic_word(word, bold_ratio)

    return bionic_word_fn


def process_text(original_text, settings):
    """Run the full text processing pipeline."""
    lang = settings.get("language", "en")
    lang_config = get_language_config(lang)

    difficult_words = detect_difficult_words(original_text, lang=lang)

    tts_text = original_text
    reader_text = original_text
    pdf_text = original_text
    docx_text = original_text

    # ── Segmentation / syllable splitting ─────────────
    if settings.get("use_syllables", False):
        if lang == "en":
            reader_text = _apply_segmentation(reader_text, lang, difficult_words)
            pdf_text = reader_text
            docx_text = reader_text
        elif lang in ("hi", "ta"):
            reader_text = _apply_segmentation(
                reader_text, lang, difficult_words, separator="·"
            )
            export_segmented = _apply_segmentation(
                original_text, lang, difficult_words, separator="-"
            )
            pdf_text = export_segmented
            docx_text = export_segmented

    is_guided = settings.get("reading_mode", "") == "🔊 Guided Reading"
    is_normal = settings.get("reading_mode", "") == "📖 Normal Reading"

    want_bionic = (
        settings.get("bionic_reading", False)
        and lang_config.get("bionic_support", False)
        and not is_guided
    )

    want_highlight = settings.get("highlight_difficulty", False)

    if want_highlight:
        # Single pass: bionic + highlight together
        # This guarantees highlighted words also get bionic
        bionic_fn = _make_bionic_fn(lang_config) if want_bionic else None

        reader_text = highlight_difficult_words(
            reader_text,
            difficult_words,
            theme=settings.get("theme_name", "Light"),
            font_family=settings.get("font_family", "Arial"),
            lang=lang,
            enable_tooltip=is_normal,
            bionic_reader_fn=bionic_fn,
            bold_ratio=BIONIC_BOLD_RATIO
        )

    elif want_bionic:
        # Bionic only — no highlighting
        reader_text = apply_bionic_reading(reader_text)

    return {
        "original_text": original_text,
        "difficult_words": difficult_words,
        "tts_text": tts_text,
        "reader_text": reader_text,
        "pdf_text": pdf_text,
        "docx_text": docx_text,
    }


def process_sentence(sentence, difficult_words, settings):
    """Process a single sentence — same logic as process_text."""
    lang = settings.get("language", "en")
    lang_config = get_language_config(lang)

    result = sentence

    if settings.get("use_syllables", False):
        result = _apply_segmentation(result, lang, difficult_words, separator="·")

    is_guided = settings.get("reading_mode", "") == "🔊 Guided Reading"
    is_normal = settings.get("reading_mode", "") == "📖 Normal Reading"

    want_bionic = (
        settings.get("bionic_reading", False)
        and lang_config.get("bionic_support", False)
        and not is_guided
    )

    want_highlight = settings.get("highlight_difficulty", False)

    if want_highlight:
        bionic_fn = _make_bionic_fn(lang_config) if want_bionic else None
        result = highlight_difficult_words(
            result,
            difficult_words,
            theme=settings.get("theme_name", "Light"),
            font_family=settings.get("font_family", "Arial"),
            lang=lang,
            enable_tooltip=is_normal,
            bionic_reader_fn=bionic_fn,
            bold_ratio=BIONIC_BOLD_RATIO
        )
    elif want_bionic:
        result = apply_bionic_reading(result)

    return result


def split_into_sentences(text, min_length=8, lang="en"):
    """Split text into sentences — delegates to sentence_splitter."""
    sentences = split_into_lines(text, lang=lang)
    return [s for s in sentences if len(s.strip()) > min_length]