"""
Export handler — multilingual.
"""

import os
import streamlit as st

from modules.export.pdf_exporter import generate_accessible_pdf
from modules.export.docx_exporter import generate_accessible_docx
from modules.audio.tts_engine import generate_audio
from modules.config.constants import MAX_TTS_CHARS


def handle_pdf_export(pdf_text, difficult_words, highlight_enabled,
                      font_size, line_spacing, lang="en"):
    with st.spinner("Generating PDF..."):
        try:
            fp = generate_accessible_pdf(
                text=pdf_text,
                difficult_words=difficult_words if highlight_enabled else set(),
                use_syllables=False,
                font_size=font_size,
                line_spacing=line_spacing,
                lang=lang
            )
            with open(fp, "rb") as f:
                pdf_data = f.read()
            st.sidebar.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name="dyslexia_reader.pdf",
                mime="application/pdf",
                key="pdf_download"
            )
            st.sidebar.success("✅ PDF ready!")
            os.remove(fp)
        except Exception as e:
            st.sidebar.error("PDF Error: " + str(e))


def handle_docx_export(pdf_text, difficult_words, highlight_enabled,
                       use_syllables, font_size, line_spacing, lang="en"):
    with st.spinner("Generating DOCX..."):
        try:
            fp = generate_accessible_docx(
                text=pdf_text,
                difficult_words=difficult_words if highlight_enabled else set(),
                use_syllables=False,
                font_size=font_size,
                line_spacing=line_spacing,
                lang=lang
            )
            with open(fp, "rb") as f:
                docx_data = f.read()
            st.sidebar.download_button(
                label="📥 Download DOCX",
                data=docx_data,
                file_name="dyslexia_reader.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="docx_download"
            )
            st.sidebar.success("✅ DOCX ready!")

            # Language-aware font install hint
            font_hints = {
                "en": (
                    "💡 For best results, install OpenDyslexic font. "
                    "[Download here](https://opendyslexic.org/)"
                ),
                "hi": (
                    "💡 DOCX uses Noto Sans Devanagari font. "
                    "Install it for best display. "
                    "[Download here](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari)"
                ),
                "ta": (
                    "💡 DOCX uses Noto Sans Tamil font. "
                    "Install it for best display. "
                    "[Download here](https://fonts.google.com/noto/specimen/Noto+Sans+Tamil)"
                ),
            }
            hint = font_hints.get(lang)
            if hint:
                st.sidebar.info(hint)

            os.remove(fp)
        except Exception as e:
            st.sidebar.error("DOCX Error: " + str(e))


def handle_audio_export(tts_text, lang="en"):
    chunks = [
        tts_text[i:i + MAX_TTS_CHARS]
        for i in range(0, len(tts_text), MAX_TTS_CHARS)
    ]
    with st.spinner("🎵 Generating audio (" + str(len(chunks)) + " part(s))..."):
        all_ok = True
        for ci, chunk in enumerate(chunks):
            af = generate_audio(chunk, lang=lang)
            if af and os.path.exists(af):
                with open(af, "rb") as f:
                    ab = f.read()
                label = "Full Audio" if len(chunks) == 1 else "Part " + str(ci + 1)
                st.sidebar.audio(ab, format="audio/mp3")
                st.sidebar.download_button(
                    label="⬇️ Download " + label,
                    data=ab,
                    file_name="audio_part_" + str(ci + 1) + ".mp3",
                    mime="audio/mp3",
                    key="exp_audio_" + str(ci)
                )
                os.remove(af)
            else:
                all_ok = False
                st.sidebar.error("Failed: chunk " + str(ci + 1))
        if all_ok:
            st.sidebar.success("✅ Audio ready!")