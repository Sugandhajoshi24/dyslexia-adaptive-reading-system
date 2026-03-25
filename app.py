"""
Dyslexia Adaptive Reading System — Multilingual
"""

import streamlit as st
import streamlit.components.v1 as components
import os

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
from modules.ui.word_tooltip import get_tooltip_css

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
        ["None", "English Sample", "Hindi Sample (हिंदी)"],
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

# ── Word Tooltip (English only) ──────────────────────────
if detected_lang == "en":
    st.markdown(get_tooltip_css(theme), unsafe_allow_html=True)

# ── Main Processing ──────────────────────────────────────
if original_text and detected_lang:

    lang = detected_lang
    lang_config = get_language_config(lang)

    result = process_text(original_text, settings)

    # ── Document Analysis (pass lang) ─────────────────
    analysis = analyze_document(original_text, result["difficult_words"], lang=lang)
    render_document_stats(analysis, theme)

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
            speech_lang=lang_config["speech_lang"]
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
        if "focus_audio" not in st.session_state:
            st.session_state.focus_audio = {}

        st.session_state.focus_idx = max(
            0, min(st.session_state.focus_idx, total - 1)
        )
        idx = st.session_state.focus_idx

        if total > 0 and idx not in st.session_state.focus_audio:
            with st.spinner("🎵 Preparing audio for sentence " + str(idx + 1) + "..."):
                af = generate_audio(
                    sentences_tts[idx],
                    lang=lang_config["tts_code"]
                )
                if af and os.path.exists(af):
                    with open(af, "rb") as f:
                        st.session_state.focus_audio[idx] = f.read()
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
                audio_cache=st.session_state.focus_audio
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