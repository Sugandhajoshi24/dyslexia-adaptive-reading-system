from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import time
import re
import pyphen

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "OpenDyslexic3-Regular.ttf")

dic = pyphen.Pyphen(lang="en")


def _syllabify_word(word, difficult_words):
    """Return syllabified version of word if it is in difficult_words set."""
    clean = re.sub(r'[^\w]', '', word).lower()
    if clean in difficult_words:
        return dic.inserted(word)
    return word


def generate_accessible_pdf(
    text,
    difficult_words=None,
    use_syllables=False,
    font_size=20,
    line_spacing=1.8
):
    """
    Generate a dyslexia-friendly PDF.

    When use_syllables=False but the text already contains hyphens
    (pre-syllabified from app.py), those hyphens are preserved as-is
    without double-processing.
    """
    if difficult_words is None:
        difficult_words = set()

    os.makedirs("downloads", exist_ok=True)
    filename = f"downloads/dyslexia_reader_{int(time.time())}.pdf"

    # Register font
    if os.path.exists(FONT_PATH):
        try:
            pdfmetrics.registerFont(TTFont("OpenDyslexic", FONT_PATH))
            font_name = "OpenDyslexic"
        except Exception:
            font_name = "Helvetica"
    else:
        font_name = "Helvetica"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
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
            # Get the root word (strip hyphens + punctuation) for lookup
            root = re.sub(r'[^\w]', '', word).lower()

            # Only syllabify here if use_syllables=True
            # (app.py passes False because text is already syllabified)
            if use_syllables:
                display = _syllabify_word(word, difficult_words)
            else:
                display = word

            # Escape XML special characters
            safe = (
                display
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            # Highlight if the ROOT word (without hyphens) is difficult
            if root in difficult_words and len(difficult_words) > 0:
                tagged.append(
                    f'<font backColor="#FFD54F"><b>{safe}</b></font>'
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