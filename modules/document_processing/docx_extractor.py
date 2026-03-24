"""
Extract text from .docx files using python-docx.
"""

import re


def extract_text_from_docx(uploaded_file):
    """
    Extract text from a .docx file.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Cleaned text string or None
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "python-docx is not installed. Run: pip install python-docx"
        )

    try:
        doc = Document(uploaded_file)

        paragraphs = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        if not paragraphs:
            return None

        result = "\n".join(paragraphs)

        # Basic cleanup
        result = re.sub(r' {2,}', ' ', result)
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result.strip() if result.strip() else None

    except Exception as e:
        raise Exception(f"DOCX extraction failed: {e}")