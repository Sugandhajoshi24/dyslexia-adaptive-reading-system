import streamlit as st

from modules.text_extraction import extract_pdf_text
from modules.syllable_processor import syllabify_text
from modules.tts_module import speak_text


st.title("Dyslexia-Friendly Adaptive Reading System")

uploaded_file = st.file_uploader("Upload Document as PDF or TXT", type=["pdf", "txt"])

st.sidebar.header("Reading Controls")

use_syllables = st.sidebar.checkbox("Enable Syllable Splitting")

font_size = st.sidebar.slider("Font Size", 14, 40, 20)
line_spacing = st.sidebar.slider("Line Spacing", 1.0, 3.0, 1.5)
letter_spacing = st.sidebar.slider("Letter Spacing", 0.0, 5.0, 1.0)

theme = st.sidebar.selectbox(
    "Color Theme",
    ["Default", "Sepia", "Dark", "High Contrast"]
)

st.sidebar.header("Audio Controls")

speech_speed = st.sidebar.slider("Speech Speed", 100, 250, 150)

speak_button = st.sidebar.button("Read Text Aloud")


if uploaded_file is not None:

    if uploaded_file.type == "application/pdf":
        text = extract_pdf_text(uploaded_file)

    else:
        text = uploaded_file.read().decode("utf-8")

    if use_syllables:
        text = syllabify_text(text)

    if speak_button:
        speak_text(text, speech_speed)    

    st.subheader("Extracted Text")
    if theme == "Sepia":
        background = "#f4ecd8"
        text_color = "#5b4636"

    elif theme == "Dark":
        background = "#1e1e1e"
        text_color = "#ffffff"

    elif theme == "High Contrast":
        background = "#000000"
        text_color = "#ffff00"

    else:
        background = "transparent"
        text_color = "inherit"

    styled_text = f"""
    <div style="
    background-color:{background};
    color:{text_color};
    font-size:{font_size}px;
    line-height:{line_spacing};
    letter-spacing:{letter_spacing}px;
    padding:15px;
    border-radius:8px;
    ">
    {text}
    </div>
    """

    st.markdown("### Extracted Text")
    st.markdown(styled_text, unsafe_allow_html=True)