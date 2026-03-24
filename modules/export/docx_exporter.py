"""
Export processed text to a dyslexia-friendly DOCX file.
"""

import os
import time
import re
import pyphen

dic = pyphen.Pyphen(lang="en")


def _syllabify_word(word, difficult_words):
    """Return syllabified version if word is difficult."""
    clean = re.sub(r'[^\w]', '', word).lower()
    if clean in difficult_words:
        return dic.inserted(word)
    return word


def generate_accessible_docx(
    text,
    difficult_words=None,
    use_syllables=False,
    font_size=20,
    line_spacing=1.8
):
    """
    Generate a dyslexia-friendly DOCX file.

    When use_syllables=False but text already contains hyphens
    (pre-syllabified), those hyphens are preserved without double-processing.
    """
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_LINE_SPACING

    if difficult_words is None:
        difficult_words = set()

    os.makedirs("downloads", exist_ok=True)
    filename = f"downloads/dyslexia_reader_{int(time.time())}.docx"

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.2)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)

    # Set default font on Normal style
    style = doc.styles['Normal']
    style.font.name = "OpenDyslexic"
    style.font.size = Pt(font_size)

    # Process paragraphs
    paragraphs = text.split("\n")

    for para_text in paragraphs:
        if not para_text.strip():
            doc.add_paragraph("")
            continue

        paragraph = doc.add_paragraph()

        para_format = paragraph.paragraph_format
        para_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        para_format.line_spacing = line_spacing
        para_format.space_after = Pt(8)

        words = para_text.split()

        for i, word in enumerate(words):
            root = re.sub(r'[^\w]', '', word).lower()

            if use_syllables:
                display = _syllabify_word(word, difficult_words)
            else:
                display = word

            if i > 0:
                space_run = paragraph.add_run(" ")
                space_run.font.size = Pt(font_size)
                space_run.font.name = "OpenDyslexic"

            run = paragraph.add_run(display)
            run.font.size = Pt(font_size)
            run.font.name = "OpenDyslexic"

            if root in difficult_words and len(difficult_words) > 0:
                run.bold = True
                run.font.highlight_color = 7  # Yellow

    doc.save(filename)
    return filename