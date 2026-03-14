from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "OpenDyslexic3-Regular.ttf")


def generate_accessible_pdf(text, font_size=20, line_spacing=1.8):

    os.makedirs("downloads", exist_ok=True)

    filename = f"downloads/dyslexia_reader_{int(time.time())}.pdf"

    # Register font
    pdfmetrics.registerFont(TTFont("OpenDyslexic", FONT_PATH))

    # PDF document layout
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=90,
        rightMargin=90,
        topMargin=80,
        bottomMargin=80
    )

    # Dyslexia friendly style
    style = ParagraphStyle(
        name="DyslexiaStyle",
        fontName="OpenDyslexic",
        fontSize=font_size,
        leading=font_size * line_spacing,
        spaceAfter=14
    )

    content = []

    paragraphs = text.split("\n")

    for p in paragraphs:

        if p.strip():
            content.append(Paragraph(p, style))
            content.append(Spacer(1, 12))

    doc.build(content)

    return filename