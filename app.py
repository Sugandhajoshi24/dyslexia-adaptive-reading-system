"""
Dyslexia Adaptive Reading System — Multilingual
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import hashlib

from modules.config.themes import get_theme_config
from modules.config.constants import SUPPORTED_FILE_TYPES, MIN_SENTENCE_LENGTH
from modules.config.css_generator import generate_global_css
from modules.config.language_config import get_language_config, get_supported_languages

from modules.ui.components import (
    load_custom_font, render_header,
    render_upload_hint, render_mode_badge, render_reading_panel
)
from modules.ui.sidebar import render_sidebar
from modules.ui.ui_styles import load_ui_styles
from modules.ui.guided_reader import render_speech_sync
from modules.ui.focus_reader import render_focus_mode
from modules.ui.document_stats import render_document_stats

from modules.document_processing.file_handler import extract_text_from_upload
from modules.text_processing.language_detector import detect_language
from modules.text_processing.processor import (
    process_text, process_sentence, split_into_sentences
)
from modules.text_processing.document_analyzer import analyze_document

from modules.export.export_handler import (
    handle_pdf_export, handle_docx_export, handle_audio_export
)
from modules.audio.tts_engine import generate_audio


# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Dyslexia Adaptive Reader",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Base styles ──────────────────────────────────────────
st.markdown(load_ui_styles(), unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
render_header()

# ── File Upload + Language Selection ─────────────────────
col_upload, col_lang = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload TXT, PDF, or DOCX",
        type=SUPPORTED_FILE_TYPES,
        help="Supports .txt, .pdf, and .docx files"
    )

with col_lang:
    supported = get_supported_languages()
    lang_options = ["Auto-detect"] + [supported[k] for k in supported]
    lang_keys = ["auto"] + list(supported.keys())

    lang_choice = st.selectbox("Language", lang_options, index=0)
    chosen_lang_code = lang_keys[lang_options.index(lang_choice)]

# ── Get text from upload or sample ───────────────────────
original_text = None
detected_lang = None

if uploaded_file:
    original_text = extract_text_from_upload(uploaded_file)

    if original_text:
        if chosen_lang_code == "auto":
            detected_lang = detect_language(original_text)
        else:
            detected_lang = chosen_lang_code

        lang_config = get_language_config(detected_lang)
        st.info(
            "📝 Detected language: **"
            + lang_config["name"] + " " + lang_config["flag"]
            + "** — You can change this in the Language dropdown above."
        )
else:
    render_upload_hint()

    sample_lang = st.radio(
        "📝 Try a sample text:",
        ["None", "English Sample", "Hindi Sample (हिंदी)", "Tamil Sample (தமிழ்)"],
        index=0,
        horizontal=True
    )

    if sample_lang == "English Sample":
        detected_lang = "en"
        lang_config = get_language_config("en")
        original_text = lang_config["sample_text"]
    elif sample_lang.startswith("Hindi"):
        detected_lang = "hi"
        lang_config = get_language_config("hi")
        original_text = lang_config["sample_text"]
    elif sample_lang.startswith("Tamil"):
        detected_lang = "ta"
        lang_config = get_language_config("ta")
        original_text = lang_config["sample_text"]

# ── Load fonts + Sidebar ─────────────────────────────────
text_loaded = original_text is not None

if detected_lang:
    load_custom_font(detected_lang)
else:
    load_custom_font("en")

settings = render_sidebar(
    lang_code=detected_lang,
    text_loaded=text_loaded
)

theme = get_theme_config(settings["theme_name"])

st.markdown(
    generate_global_css(
        theme,
        settings["font_family"],
        settings["font_size"],
        settings["line_spacing"],
        settings["letter_spacing"]
    ),
    unsafe_allow_html=True
)

# ── Cancel leftover speech ───────────────────────────────
if settings["reading_mode"] != "🔊 Guided Reading":
    components.html("""
        <script>
        try { speechSynthesis.cancel(); } catch(e) {}
        try { window.parent.speechSynthesis.cancel(); } catch(e) {}
        </script>
    """, height=0)


# ══════════════════════════════════════════════════════════
# AUDIO CACHE HELPERS
# ══════════════════════════════════════════════════════════

def _stable_text_hash(text):
    """
    Deterministic hash of the first 500 chars of text.

    Uses hashlib.md5 — NOT Python's built-in hash().
    Python's hash() is randomized per-session (since Python 3.3)
    and will produce different values across restarts.
    hashlib.md5 always produces the same output for the same input.
    """
    if not text:
        return "empty"
    return hashlib.md5(
        text[:500].encode("utf-8", errors="ignore")
    ).hexdigest()[:16]


def _get_focus_cache_key(lang, text):
    """
    Cache key for focus mode audio.
    Format: focus_audio_<lang>_<text_hash>

    Scoped to ONE language + ONE text version.
    Prevents cross-language contamination.
    """
    return "focus_audio_" + lang + "_" + _stable_text_hash(text)


def _get_guided_cache_key(lang, text):
    """
    Cache key for guided reading audio.
    Format: guided_audio_<lang>_<text_hash>

    Must match the key format used in guided_reader.py exactly.
    """
    return "guided_audio_" + lang + "_" + _stable_text_hash(text)


def _purge_stale_audio_cache(current_lang, current_text):
    """
    Remove all focus and guided audio cache entries that do NOT
    belong to the current language + text combination.

    Only removes keys that start with:
      - focus_audio_
      - guided_audio_

    Does NOT touch any other session_state keys.
    Does NOT clear session_state entirely.
    """
    current_focus_key = _get_focus_cache_key(current_lang, current_text)
    current_guided_key = _get_guided_cache_key(current_lang, current_text)

    keys_to_delete = [
        key for key in list(st.session_state.keys())
        if (
            key.startswith("focus_audio_") and key != current_focus_key
        ) or (
            key.startswith("guided_audio_") and key != current_guided_key
        )
    ]

    for key in keys_to_delete:
        del st.session_state[key]


def _reset_state_on_text_change(new_lang, text):
    """
    Detect language or text changes and reset reading state.

    On change:
      1. Reset focus_idx to 0
      2. Purge all stale audio cache entries
      3. Update tracking keys in session_state

    Tracking uses stable hashes — not Python hash().
    """
    prev_lang = st.session_state.get("active_language", None)
    prev_text_hash = st.session_state.get("active_text_hash", None)
    new_text_hash = _stable_text_hash(text)

    if prev_lang != new_lang or prev_text_hash != new_text_hash:
        # Reset navigation
        st.session_state.focus_idx = 0

        # Purge stale audio — only audio keys, nothing else
        _purge_stale_audio_cache(new_lang, text)

        # Update trackers
        st.session_state.active_language = new_lang
        st.session_state.active_text_hash = new_text_hash


# ── Main Processing ──────────────────────────────────────
if original_text and detected_lang:

    lang = detected_lang
    lang_config = get_language_config(lang)

    # Detect language/text change — reset state + purge stale audio
    _reset_state_on_text_change(lang, original_text)

    result = process_text(original_text, settings)

    # ── Word Tooltip (English only, Normal reading mode only) ──
    if lang == "en" and settings["reading_mode"] == "📖 Normal Reading":
        from modules.ui.word_tooltip import inject_tooltip_system
        inject_tooltip_system(theme)

    # ── Document Analysis ─────────────────────────────
    analysis = analyze_document(original_text, result["difficult_words"], lang=lang)
    render_document_stats(analysis, theme, lang=lang)

    # ── 🔊 GUIDED READING ────────────────────────────
    if settings["reading_mode"] == "🔊 Guided Reading":

        render_mode_badge("🔊 Guided Reading Mode")

        render_speech_sync(
            display_text=result["reader_text"],
            tts_text=result["tts_text"],
            font_family=settings["font_family"],
            font_size=settings["font_size"],
            theme=settings["theme_name"],
            line_spacing=settings["line_spacing"],
            letter_spacing=settings["letter_spacing"],
            theme_config=theme,
            speech_lang=lang_config["speech_lang"],
            lang_code=lang
        )

    # ── 🔍 FOCUS MODE ────────────────────────────────
    elif settings["reading_mode"] == "🔍 Focus Mode":

        render_mode_badge("🔍 Focus Mode — Sentence by Sentence")

        raw_sentences = split_into_sentences(
            original_text, MIN_SENTENCE_LENGTH, lang=lang
        )
        total = len(raw_sentences)

        sentences_tts = raw_sentences[:]
        sentences_rich = [
            process_sentence(s, result["difficult_words"], settings)
            for s in raw_sentences
        ]

        if "focus_idx" not in st.session_state:
            st.session_state.focus_idx = 0

        # Scoped cache key: language + stable text hash
        audio_cache_key = _get_focus_cache_key(lang, original_text)

        if audio_cache_key not in st.session_state:
            st.session_state[audio_cache_key] = {}

        focus_audio = st.session_state[audio_cache_key]

        st.session_state.focus_idx = max(
            0, min(st.session_state.focus_idx, total - 1)
        )
        idx = st.session_state.focus_idx

        # Generate audio for current sentence if not cached
        if total > 0 and idx not in focus_audio:
            with st.spinner("🎵 Preparing audio for sentence " + str(idx + 1) + "..."):
                af = generate_audio(
                    sentences_tts[idx],
                    lang=lang_config["tts_code"]
                )
                if af and os.path.exists(af):
                    try:
                        with open(af, "rb") as f:
                            focus_audio[idx] = f.read()
                    finally:
                        # Always delete temp file even if read fails
                        if os.path.exists(af):
                            os.remove(af)

        if total > 0:
            render_focus_mode(
                sentences_plain=sentences_tts,
                sentences_rich=sentences_rich,
                idx=idx,
                total=total,
                theme_config=theme,
                font_family=settings["font_family"],
                font_size=settings["font_size"],
                line_spacing=settings["line_spacing"],
                letter_spacing=settings["letter_spacing"],
                audio_cache=focus_audio
            )
        else:
            st.warning("No sentences found in the text.")

    # ── 📖 NORMAL READING ────────────────────────────
    else:
        render_mode_badge("📖 Normal Reading Mode")
        render_reading_panel(result["reader_text"])

    # ── EXPORTS ───────────────────────────────────────
    if settings["export_pdf"]:
        handle_pdf_export(
            result["pdf_text"],
            result["difficult_words"],
            settings["highlight_difficulty"],
            settings["font_size"],
            settings["line_spacing"],
            lang=lang
        )

    if settings["export_docx"]:
        handle_docx_export(
            result["pdf_text"],
            result["difficult_words"],
            settings["highlight_difficulty"],
            settings["use_syllables"],
            settings["font_size"],
            settings["line_spacing"],
            lang=lang
        )

    if settings["export_audio"]:
        handle_audio_export(
            result["tts_text"],
            lang=lang_config["tts_code"]
        )