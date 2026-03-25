"""
Sidebar — language-aware controls.
"""

import streamlit as st
from modules.config.themes import get_theme_names
from modules.config.constants import (
    DEFAULT_FONT_SIZE, MIN_FONT_SIZE, MAX_FONT_SIZE,
    DEFAULT_LINE_SPACING, MIN_LINE_SPACING, MAX_LINE_SPACING, LINE_SPACING_STEP,
    DEFAULT_LETTER_SPACING, MIN_LETTER_SPACING, MAX_LETTER_SPACING, LETTER_SPACING_STEP,
    READING_MODES,
)
from modules.config.language_config import get_language_config


def render_sidebar(lang_code=None, text_loaded=False):
    """Render sidebar controls filtered by language."""
    settings = {}

    # ── Always visible: Appearance ────────────────────
    st.sidebar.markdown("## 🎨 Appearance")

    settings["theme_name"] = st.sidebar.selectbox("Theme", get_theme_names())

    if lang_code:
        lang_config = get_language_config(lang_code)
        font_options = lang_config["font_options"]
        default_font = lang_config["default_font"]
    else:
        font_options = ["Arial", "OpenDyslexic", "Georgia", "Verdana", "Tahoma"]
        default_font = "Arial"

    default_idx = font_options.index(default_font) if default_font in font_options else 0
    settings["font_family"] = st.sidebar.selectbox("Font", font_options, index=default_idx)

    settings["font_size"] = st.sidebar.slider(
        "Font Size", MIN_FONT_SIZE, MAX_FONT_SIZE, DEFAULT_FONT_SIZE
    )
    settings["line_spacing"] = st.sidebar.slider(
        "Line Spacing",
        MIN_LINE_SPACING, MAX_LINE_SPACING, DEFAULT_LINE_SPACING,
        step=LINE_SPACING_STEP
    )
    settings["letter_spacing"] = st.sidebar.slider(
        "Letter Spacing (px)",
        MIN_LETTER_SPACING, MAX_LETTER_SPACING, DEFAULT_LETTER_SPACING,
        step=LETTER_SPACING_STEP
    )

    # Defaults
    settings["use_syllables"] = False
    settings["highlight_difficulty"] = False
    settings["highlight_mode"] = "All Difficult Words"
    settings["bionic_reading"] = False
    settings["reading_mode"] = "📖 Normal Reading"
    settings["export_pdf"] = False
    settings["export_docx"] = False
    settings["export_audio"] = False

    if text_loaded and lang_code:
        lang_config = get_language_config(lang_code)

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🛠️ Reading Tools")

        # Syllable splitting — only for languages that support it
        if lang_config.get("syllable_support", False) and lang_code == "en":
            settings["use_syllables"] = st.sidebar.checkbox("Syllable Splitting")
        elif lang_code != "en":
            st.sidebar.caption("ℹ️ Syllable splitting not available for " + lang_config["name"])

        settings["highlight_difficulty"] = st.sidebar.checkbox("Highlight Difficult Words")

        if lang_config.get("bionic_support", False):
            settings["bionic_reading"] = st.sidebar.checkbox(
                "Bionic Reading ✨",
                help="Bold the first part of each word for faster reading"
            )

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🎯 Reading Mode")

        settings["reading_mode"] = st.sidebar.radio(
            "Select Mode", READING_MODES, index=0
        )

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📦 Export")

        settings["export_pdf"] = st.sidebar.button("📄 Download PDF")
        settings["export_docx"] = st.sidebar.button("📝 Download DOCX")
        settings["export_audio"] = st.sidebar.button("🔊 Generate Full Audio")

    settings["language"] = lang_code or "en"

    return settings