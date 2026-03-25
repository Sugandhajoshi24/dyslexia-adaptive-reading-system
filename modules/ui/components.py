"""
Reusable UI components — multilingual font loading.
"""

import streamlit as st
import os
import base64

from modules.config.constants import FONT_DIR


def load_custom_font(lang_code="en"):
    """Load the appropriate font for the detected language."""
    from modules.config.language_config import get_language_config

    lang_config = get_language_config(lang_code)
    font_file = lang_config.get("browser_font_file", "")
    font_family = lang_config.get("browser_font_family", "")

    if not font_file or not font_family:
        return

    font_path = os.path.join(FONT_DIR, font_file)

    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            "<style>"
            "@font-face {"
            "  font-family: '" + font_family + "';"
            "  src: url(data:font/truetype;base64," + b64 + ") format('truetype');"
            "  font-weight: normal;"
            "  font-style: normal;"
            "}"
            "</style>",
            unsafe_allow_html=True
        )

    # Also always load OpenDyslexic for English
    if lang_code != "en":
        od_path = os.path.join(FONT_DIR, "OpenDyslexic3-Regular.ttf")
        if os.path.exists(od_path):
            with open(od_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                "<style>"
                "@font-face {"
                "  font-family: 'OpenDyslexic';"
                "  src: url(data:font/truetype;base64," + b64 + ") format('truetype');"
                "  font-weight: normal;"
                "  font-style: normal;"
                "}"
                "</style>",
                unsafe_allow_html=True
            )


def render_header():
    """Render the app header."""
    st.markdown("""
    <div style='text-align:center; padding:14px 0 6px;'>
        <h1 style='font-size:2.1rem; font-weight:800; margin:0;'>
            📖 Dyslexia Adaptive Reader
        </h1>
        <p style='font-size:.95rem; margin-top:5px; opacity:0.6;'>
            Intelligent multilingual reading assistance
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_upload_hint():
    """Show upload prompt."""
    st.markdown("""
    <div class='upload-hint'>
        📂 Upload a file above — or choose a sample text to preview settings
    </div>
    """, unsafe_allow_html=True)


def render_mode_badge(label):
    """Render mode indicator badge."""
    st.markdown(
        "<div class='mode-badge'>" + label + "</div>",
        unsafe_allow_html=True
    )


def render_reading_panel(html_content):
    """Render the themed reading panel."""
    st.markdown(
        "<div class='reading-panel'>"
        "<div class='reader-text'>" + html_content + "</div>"
        "</div>",
        unsafe_allow_html=True
    )