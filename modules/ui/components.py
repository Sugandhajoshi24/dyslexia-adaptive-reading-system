"""
Reusable UI components for the Dyslexia Adaptive Reader.
Keeps rendering logic out of app.py.
"""

import streamlit as st
import os
import base64

from modules.config.constants import FONT_DIR, FONT_FILENAME


def load_custom_font():
    """Load OpenDyslexic font via base64 injection into browser CSS."""
    font_path = os.path.join(FONT_DIR, FONT_FILENAME)
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            @font-face {{
                font-family: 'OpenDyslexic';
                src: url(data:font/truetype;base64,{b64}) format('truetype');
                font-weight: normal;
                font-style: normal;
            }}
            </style>
        """, unsafe_allow_html=True)


def render_header():
    """Render the app title and subtitle."""
    st.markdown("""
    <div style='text-align:center; padding:14px 0 6px;'>
        <h1 style='font-size:2.1rem; font-weight:800; margin:0;'>
            📖 Dyslexia Adaptive Reader
        </h1>
        <p style='font-size:.95rem; margin-top:5px; opacity:0.6;'>
            Intelligent reading assistance for dyslexic readers
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_upload_hint():
    """Show the upload prompt when no file is loaded."""
    st.markdown("""
    <div class='upload-hint'>
        📂 Upload a file above — or use sample text below to preview settings
    </div>
    """, unsafe_allow_html=True)


def render_mode_badge(label):
    """Render a small badge showing the current reading mode."""
    st.markdown(
        f"<div class='mode-badge'>{label}</div>",
        unsafe_allow_html=True
    )


def render_reading_panel(html_content):
    """Render the themed reading panel with processed HTML text."""
    st.markdown(f"""
        <div class='reading-panel'>
            <div class='reader-text'>{html_content}</div>
        </div>
    """, unsafe_allow_html=True)