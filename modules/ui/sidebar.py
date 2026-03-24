"""
Sidebar controls. Returns a settings dict.
"""

import streamlit as st
from modules.config.themes import get_theme_names
from modules.config.constants import (
    FONT_OPTIONS,
    DEFAULT_FONT_SIZE, MIN_FONT_SIZE, MAX_FONT_SIZE,
    DEFAULT_LINE_SPACING, MIN_LINE_SPACING, MAX_LINE_SPACING, LINE_SPACING_STEP,
    DEFAULT_LETTER_SPACING, MIN_LETTER_SPACING, MAX_LETTER_SPACING, LETTER_SPACING_STEP,
    READING_MODES,
)


def render_sidebar():
    """Render all sidebar controls and return settings dict."""

    st.sidebar.markdown("## 🎨 Appearance")

    theme_name = st.sidebar.selectbox("Theme", get_theme_names())
    font_family = st.sidebar.selectbox("Font", FONT_OPTIONS)

    font_size = st.sidebar.slider(
        "Font Size", MIN_FONT_SIZE, MAX_FONT_SIZE, DEFAULT_FONT_SIZE
    )
    line_spacing = st.sidebar.slider(
        "Line Spacing",
        MIN_LINE_SPACING, MAX_LINE_SPACING, DEFAULT_LINE_SPACING,
        step=LINE_SPACING_STEP
    )
    letter_spacing = st.sidebar.slider(
        "Letter Spacing (px)",
        MIN_LETTER_SPACING, MAX_LETTER_SPACING, DEFAULT_LETTER_SPACING,
        step=LETTER_SPACING_STEP
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🛠️ Reading Tools")

    use_syllables = st.sidebar.checkbox("Syllable Splitting")
    highlight_difficulty = st.sidebar.checkbox("Highlight Difficult Words")
    bionic_reading = st.sidebar.checkbox(
        "Bionic Reading ✨",
        help="Bold the first part of each word for faster reading"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🎯 Reading Mode")

    reading_mode = st.sidebar.radio("Select Mode", READING_MODES, index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📦 Export")

    export_pdf = st.sidebar.button("📄 Download PDF")
    export_docx = st.sidebar.button("📝 Download DOCX")
    export_audio = st.sidebar.button("🔊 Generate Full Audio")

    return {
        "theme_name": theme_name,
        "font_family": font_family,
        "font_size": font_size,
        "line_spacing": line_spacing,
        "letter_spacing": letter_spacing,
        "use_syllables": use_syllables,
        "highlight_difficulty": highlight_difficulty,
        "highlight_mode": "All Difficult Words",
        "bionic_reading": bionic_reading,
        "reading_mode": reading_mode,
        "export_pdf": export_pdf,
        "export_docx": export_docx,
        "export_audio": export_audio,
    }