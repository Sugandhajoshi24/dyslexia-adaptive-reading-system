"""
PDF export — multilingual.
Uses OpenDyslexic for English, Noto Sans Devanagari for Hindi.
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import time
import re
import pyphen

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")

dic_en = pyphen.Pyphen(lang="en")


def _syllabify_word(word, difficult_words):
    clean = re.sub(r'[^\w]', '', word).lower()
    if clean in difficult_words:
        return dic_en.inserted(word)
    return word


def _register_font(font_name, font_file):
    """Register a font if the file exists. Returns True if successful."""
    font_path = os.path.join(FONT_DIR, font_file)
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            return True
        except Exception:
            return False
    return False


def generate_accessible_pdf(
    text,
    difficult_words=None,
    use_syllables=False,
    font_size=20,
    line_spacing=1.8,
    lang="en"
):
    """Generate a dyslexia-friendly PDF with correct font for each language."""
    if difficult_words is None:
        difficult_words = set()

    os.makedirs("downloads", exist_ok=True)
    filename = "downloads/dyslexia_reader_" + str(int(time.time())) + ".pdf"

    # Register and select font based on language
    font_name = "Helvetica"  # fallback

    if lang == "hi":
        # Try Noto Sans Devanagari for Hindi
        if _register_font("NotoDevanagari", "NotoSansDevanagari-Regular.ttf"):
            font_name = "NotoDevanagari"
        elif _register_font("NotoDevanagariVar", "NotoSansDevanagari-VariableFont_wdth,wght.ttf"):
            font_name = "NotoDevanagariVar"
    else:
        # English — try OpenDyslexic
        if _register_font("OpenDyslexic", "OpenDyslexic3-Regular.ttf"):
            font_name = "OpenDyslexic"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=72, rightMargin=72,
        topMargin=72, bottomMargin=72
    )

    style = ParagraphStyle(
        "DyslexiaBody",
        fontName=font_name,
        fontSize=font_size,
        leading=font_size * line_spacing,
        spaceAfter=10
    )

    content = []

    paragraphs = text.split("\n")

    for para in paragraphs:
        if not para.strip():
            content.append(Spacer(1, font_size * 0.5))
            continue

        words = para.split()
        tagged = []

        for word in words:
            # Get root word for lookup
            if lang == "hi":
                root = re.sub(r'[^\u0900-\u097F]', '', word)
            else:
                root = re.sub(r'[^\w]', '', word).lower()

            if use_syllables and lang == "en":
                display = _syllabify_word(word, difficult_words)
            else:
                display = word

            # Escape XML
            safe = (
                display
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            # Highlight
            if root in difficult_words and len(difficult_words) > 0:
                tagged.append(
                    '<font backColor="#FFD54F"><b>' + safe + '</b></font>'
                )
            else:
                tagged.append(safe)

        para_xml = " ".join(tagged)

        try:
            content.append(Paragraph(para_xml, style))
        except Exception:
            safe_para = (
                para
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            content.append(Paragraph(safe_para, style))

        content.append(Spacer(1, 8))

    doc.build(content)
    return filename