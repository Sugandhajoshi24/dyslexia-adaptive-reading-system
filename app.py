import streamlit as st
from PyPDF2 import PdfReader

st.title("Dyslexia-Friendly Adaptive Reading System")

st.write("Upload a PDF or TXT file to read it in an accessible format.")

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "txt"])

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    return text


if uploaded_file is not None:

    if uploaded_file.type == "application/pdf":
        text = extract_pdf_text(uploaded_file)

    else:
        text = uploaded_file.read().decode("utf-8")

    st.subheader("Extracted Text")

    st.text_area("Document Content", text, height=400)