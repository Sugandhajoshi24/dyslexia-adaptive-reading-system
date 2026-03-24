"""
Unified file upload handler.
Routes to the correct extractor based on file type.
"""

import streamlit as st
from modules.text_processing.text_cleaner import clean_text


def extract_text_from_upload(uploaded_file):
    """
    Extract text from an uploaded file.
    Supports: .txt, .pdf, .docx

    Returns cleaned text string or None.
    """
    if uploaded_file is None:
        return None

    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".pdf"):
            return _handle_pdf(uploaded_file)
        elif filename.endswith(".docx"):
            return _handle_docx(uploaded_file)
        elif filename.endswith(".txt"):
            return _handle_txt(uploaded_file)
        else:
            st.error(f"Unsupported file type: {filename}")
            return None

    except ImportError as e:
        st.error(str(e))
        return None
    except Exception as e:
        st.error(f"File extraction failed: {e}")
        return None


def _handle_txt(uploaded_file):
    """Extract and clean text from a .txt file."""
    raw = uploaded_file.read().decode("utf-8")
    return clean_text(raw)


def _handle_pdf(uploaded_file):
    """
    Extract text from PDF using smart extraction.
    Falls back to pdfplumber if pymupdf is not available.
    """
    try:
        # Try smart extraction first (handles multi-column, headers, etc.)
        from modules.document_processing.pdf_extractor import extract_text_from_pdf
        text = extract_text_from_pdf(uploaded_file)

        if text:
            return clean_text(text)

    except ImportError:
        st.warning("PyMuPDF not installed. Using basic PDF extraction.")

    # Fallback to pdfplumber
    try:
        import pdfplumber
        uploaded_file.seek(0)

        with pdfplumber.open(uploaded_file) as pdf:
            pages = [
                page.extract_text()
                for page in pdf.pages
                if page.extract_text()
            ]

        if not pages:
            st.warning("No text found in PDF.")
            return None

        raw = "\n".join(pages)
        return clean_text(raw)

    except ImportError:
        st.error("No PDF library installed. Run: pip install pymupdf")
        return None


def _handle_docx(uploaded_file):
    """Extract and clean text from a .docx file."""
    from modules.document_processing.docx_extractor import extract_text_from_docx

    text = extract_text_from_docx(uploaded_file)

    if text:
        return clean_text(text)

    st.warning("No text found in the DOCX file.")
    return None