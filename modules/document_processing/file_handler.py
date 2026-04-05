"""
Unified file upload handler.
Routes to the correct extractor based on file type.
"""

import streamlit as st
from modules.text_processing.text_cleaner import clean_text


# Encoding fallback chain for TXT files.
# Tried in order — first successful decode wins.
# Covers:
#   utf-8        — standard for modern files, Tamil, Hindi web content
#   utf-8-sig    — UTF-8 with BOM (common in Windows-saved files)
#   utf-16       — some Windows editors save Hindi/Tamil in UTF-16
#   cp1252       — Windows Western European (common English docs)
#   latin-1      — ISO-8859-1, never fails (accepts any byte sequence)
#                  used as final fallback — may produce wrong chars
#                  but will not crash
_TXT_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "utf-16",
    "cp1252",
    "latin-1",
]


def extract_text_from_upload(uploaded_file):
    """
    Extract text from an uploaded file.
    Supports: .txt, .pdf, .docx

    Returns cleaned text string or None.
    Shows user-friendly error messages — never crashes on bad input.
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
            st.error(
                "Unsupported file type: **" + filename + "**  \n"
                "Please upload a .txt, .pdf, or .docx file."
            )
            return None

    except ImportError as e:
        st.error(
            "A required library is missing:  \n"
            + str(e)
        )
        return None
    except Exception as e:
        st.error(
            "File extraction failed: **" + filename + "**  \n"
            + str(e)
        )
        return None


def _handle_txt(uploaded_file):
    """
    Extract and clean text from a .txt file.

    Tries multiple encodings in order:
        utf-8 → utf-8-sig → utf-16 → cp1252 → latin-1

    latin-1 is the final fallback — it accepts any byte sequence
    and will never raise UnicodeDecodeError, but may produce
    incorrect characters if the file is actually UTF-8 or UTF-16.

    Shows a warning if UTF-8 fails so the user knows the file
    may not have decoded perfectly.
    """
    raw_bytes = uploaded_file.read()

    if not raw_bytes:
        st.warning("The uploaded TXT file appears to be empty.")
        return None

    # Try each encoding in order
    last_error = None
    utf8_failed = False

    for encoding in _TXT_ENCODINGS:
        try:
            text = raw_bytes.decode(encoding)

            # Warn user if we fell back from UTF-8
            if utf8_failed and encoding != "utf-8-sig":
                st.warning(
                    "⚠️ File is not UTF-8 encoded. "
                    "Decoded using **" + encoding + "** — "
                    "some characters may not display correctly."
                )

            cleaned = clean_text(text)

            if not cleaned:
                st.warning("The TXT file appears to be empty after cleaning.")
                return None

            return cleaned

        except UnicodeDecodeError as e:
            last_error = e
            if encoding == "utf-8":
                utf8_failed = True
            continue

    # All encodings failed — this should not happen because
    # latin-1 accepts any byte sequence, but handle it safely
    st.error(
        "Could not decode the TXT file.  \n"
        "Please save the file as UTF-8 and try again."
    )
    return None


def _handle_pdf(uploaded_file):
    """
    Extract text from PDF using smart extraction.
    Falls back to pdfplumber if pymupdf is not available.
    """
    try:
        from modules.document_processing.pdf_extractor import extract_text_from_pdf
        text = extract_text_from_pdf(uploaded_file)

        if text:
            return clean_text(text)

    except ImportError:
        st.warning(
            "⚠️ PyMuPDF not installed. "
            "Using basic PDF extraction — quality may be lower."
        )

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
            st.warning(
                "⚠️ No text found in this PDF.  \n"
                "If it is a scanned document, text extraction "
                "is not supported."
            )
            return None

        raw = "\n".join(pages)
        return clean_text(raw)

    except ImportError:
        st.error(
            "No PDF library available.  \n"
            "Run: `pip install pymupdf` or `pip install pdfplumber`"
        )
        return None
    except Exception as e:
        st.error(
            "PDF extraction failed.  \n"
            + str(e)
        )
        return None


def _handle_docx(uploaded_file):
    """
    Extract and clean text from a .docx file.
    Shows user-friendly error if file is corrupt or invalid.
    """
    try:
        from modules.document_processing.docx_extractor import extract_text_from_docx
        text = extract_text_from_docx(uploaded_file)

        if text:
            return clean_text(text)

        st.warning(
            "⚠️ No text found in the DOCX file.  \n"
            "The file may be empty or use unsupported formatting."
        )
        return None

    except Exception as e:
        st.error(
            "DOCX extraction failed.  \n"
            + str(e)
        )
        return None