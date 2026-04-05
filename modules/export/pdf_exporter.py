"""
PDF export — multilingual.
Uses OpenDyslexic for English, Noto Sans Devanagari for Hindi,
Noto Sans Tamil for Tamil.
Static fonts only — no variable fonts (ReportLab incompatible).
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

# ── Font directory resolution ─────────────────────────────────────────────
# Anchor from this file's location:
# modules/export/pdf_exporter.py
#   → modules/export/        (dirname once)
#   → modules/               (dirname twice)
#   → project root           (dirname three times)

_THIS_FILE   = os.path.abspath(__file__)
_EXPORT_DIR  = os.path.dirname(_THIS_FILE)
_MODULES_DIR = os.path.dirname(_EXPORT_DIR)
_PROJECT_ROOT = os.path.dirname(_MODULES_DIR)

# English static font lives in assets/fonts/ root
FONT_DIR = os.path.join(_PROJECT_ROOT, "assets", "fonts")

# Hindi + Tamil static fonts live in assets/fonts/static/
STATIC_FONT_DIR = os.path.join(_PROJECT_ROOT, "assets", "fonts", "static")

dic_en = pyphen.Pyphen(lang="en")


def _register_font(font_name, font_file, use_static_dir=False):
    """
    Register a font with ReportLab.

    Idempotent — safe to call multiple times (Streamlit reruns).
    Uses only static .ttf font files — no variable fonts.

    Args:
        font_name:      ReportLab internal name for this font
        font_file:      filename only (e.g. "NotoSansTamil-Regular.ttf")
        use_static_dir: if True, looks in assets/fonts/static/
                        if False, looks in assets/fonts/ root

    Returns True if font is available (registered or already was).
    Returns False if file not found or registration fails —
    caller falls back to Helvetica.
    """
    # Already registered — idempotent, safe for Streamlit reruns
    try:
        if font_name in pdfmetrics.getRegisteredFontNames():
            return True
    except Exception:
        pass

    # Select correct directory
    font_dir = STATIC_FONT_DIR if use_static_dir else FONT_DIR
    font_path = os.path.join(font_dir, font_file)

    if not os.path.exists(font_path):
        print("[PDF FONT] Not found: " + font_path)
        return False

    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        print("[PDF FONT] Registered: " + font_name + " from " + font_path)
        return True
    except Exception as e:
        print("[PDF FONT] Registration failed: " + font_name + " — " + str(e))
        return False


def _syllabify_word(word, difficult_words):
    """Syllabify English word if difficult."""
    clean = re.sub(r'[^\w]', '', word).lower()
    if clean in difficult_words:
        return dic_en.inserted(word)
    return word


def generate_accessible_pdf(
    text,
    difficult_words=None,
    use_syllables=False,
    font_size=20,
    line_spacing=1.8,
    lang="en"
):
    """
    Generate a dyslexia-friendly PDF with correct font for each language.

    Font selection:
    - English → OpenDyslexic3-Regular.ttf   (assets/fonts/)
    - Hindi   → NotoSansDevanagari-Regular.ttf (assets/fonts/static/)
    - Tamil   → NotoSansTamil-Regular.ttf      (assets/fonts/static/)
    - Fallback → Helvetica (built-in, always available, no Tamil/Hindi glyphs)
    """
    if difficult_words is None:
        difficult_words = set()

    os.makedirs("downloads", exist_ok=True)
    filename = (
        "downloads/dyslexia_reader_"
        + str(int(time.time()))
        + ".pdf"
    )

    # ── Font selection — static fonts only ───────────────────────
    # Helvetica is the safe fallback — always available in ReportLab
    # but has no Tamil or Hindi glyphs (shows boxes if used for those)
    font_name = "Helvetica"

    if lang == "hi":
        # Hindi static font lives in assets/fonts/static/
        if _register_font(
            "NotoDevanagari",
            "NotoSansDevanagari-Regular.ttf",
            use_static_dir=True
        ):
            font_name = "NotoDevanagari"
        else:
            print("[PDF] Hindi font registration failed — using Helvetica")

    elif lang == "ta":
        # Tamil static font lives in assets/fonts/static/
        if _register_font(
            "NotoTamil",
            "NotoSansTamil-Regular.ttf",
            use_static_dir=True
        ):
            font_name = "NotoTamil"
        else:
            print("[PDF] Tamil font registration failed — using Helvetica")

    else:
        # English — OpenDyslexic lives in assets/fonts/ root
        if _register_font(
            "OpenDyslexic",
            "OpenDyslexic3-Regular.ttf",
            use_static_dir=False
        ):
            font_name = "OpenDyslexic"
        else:
            print("[PDF] OpenDyslexic font registration failed — using Helvetica")

    print("[PDF] Font selected: " + font_name + " (lang=" + lang + ")")

    # ── Document setup ────────────────────────────────────────────
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
            if lang == "hi":
                root = re.sub(r'[^\u0900-\u097F]', '', word)
            elif lang == "ta":
                root = re.sub(r'[^\u0B80-\u0BFF]', '', word)
            else:
                root = re.sub(r'[^\w]', '', word).lower()

            if use_syllables and lang == "en":
                display = _syllabify_word(word, difficult_words)
            else:
                display = word

            safe = (
                display
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            if root in difficult_words and len(difficult_words) > 0:
                tagged.append(
                    '<font backColor="#FFD54F"><b>'
                    + safe
                    + '</b></font>'
                )
            else:
                tagged.append(safe)

        para_xml = " ".join(tagged)

        try:
            content.append(Paragraph(para_xml, style))
        except Exception as e:
            print("[PDF] Paragraph render failed: " + str(e))
            safe_para = (
                para
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            try:
                content.append(Paragraph(safe_para, style))
            except Exception as e2:
                print("[PDF] Plain paragraph also failed: " + str(e2))
                continue

        content.append(Spacer(1, 8))

    doc.build(content)
    return filename