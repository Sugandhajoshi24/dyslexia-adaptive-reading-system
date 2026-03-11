import re
import time
import streamlit as st
import pyttsx3

from modules.text_extraction import extract_pdf_text
from modules.syllable_processor import syllabify_text


st.title("Dyslexia-Friendly Adaptive Reading System")

st.write(
"""
This system helps readers with dyslexia by providing customizable reading tools such as
syllable splitting, visual adjustments, focus mode, and text-to-speech support.
Upload a document to begin reading.
"""
)

uploaded_file = st.file_uploader("Upload Document as PDF or TXT", type=["pdf", "txt"])

st.info("Upload a PDF or TXT document to start using the reading tools.")


# ---------- Sentence Splitting ----------

def split_into_lines(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences


# ---------- Speech + Highlight ----------

def speak_with_highlight(text, speed, font_size, font_family):

    import pyttsx3

    engine = pyttsx3.init()
    engine.setProperty('rate', speed)

    words = text.split()

    placeholder = st.empty()

    # Start speech
    engine.say(text)
    engine.startLoop(False)

    for i in range(len(words)):

        highlighted_text = ""

        for j, word in enumerate(words):

            if j == i:
                highlighted_text += f"<span style='background-color:yellow'>{word}</span> "
            else:
                highlighted_text += word + " "

        placeholder.markdown(
            f"""
            <div style="
            font-size:{font_size}px;
            font-family:{font_family};
            max-width:800px;
            margin:auto;
            padding:15px;
            ">
            {highlighted_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        engine.iterate()
        time.sleep(0.35)

    engine.endLoop()


# ---------- Main Logic ----------

if uploaded_file is not None:

    # Sidebar Controls
    st.sidebar.header("Reading Controls")

    font_family = st.sidebar.selectbox(
        "Reading Font",
        ["Arial", "Verdana", "Georgia", "Times New Roman"]
    )

    use_syllables = st.sidebar.checkbox("Enable Syllable Splitting")

    font_size = st.sidebar.slider("Font Size", 14, 40, 20)

    line_spacing = st.sidebar.slider("Line Spacing", 1.0, 3.0, 1.5)

    letter_spacing = st.sidebar.slider("Letter Spacing", 0.0, 5.0, 1.0)

    theme = st.sidebar.selectbox(
        "Color Theme",
        ["Default", "Sepia", "Dark", "High Contrast"]
    )

    focus_mode = st.sidebar.checkbox("Enable Focus Mode")

    st.sidebar.header("Audio Controls")

    speech_speed = st.sidebar.slider("Speech Speed", 100, 250, 150)

    speak_button = st.sidebar.button("Read Text Aloud")

    # ---------- Text Extraction ----------

    if uploaded_file.type == "application/pdf":
        text = extract_pdf_text(uploaded_file)
    else:
        text = uploaded_file.read().decode("utf-8")

    if use_syllables:
        text = syllabify_text(text)

    # ---------- Theme Settings ----------

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

    # ---------- Speech ----------

    if speak_button:
        speak_with_highlight(
            text,
            speech_speed,
            font_size,
            font_family
        )

    # ---------- Display Section ----------

    st.subheader("Extracted Text")
    st.divider()

    styled_text = f"""
    <div style="
    background-color:{background};
    color:{text_color};
    font-family:{font_family};
    font-size:{font_size}px;
    line-height:{line_spacing};
    letter-spacing:{letter_spacing}px;
    padding:20px;
    border-radius:10px;
    max-width:800px;
    margin:auto;
    box-shadow:0 2px 8px rgba(0,0,0,0.1);
    ">
    {text}
    </div>
    """

    # ---------- Focus Mode ----------

    if focus_mode and not speak_button:

        lines = split_into_lines(text)
        total_lines = len(lines)

        current_line = st.slider(
            "Focus Line",
            0,
            total_lines - 1,
            0
        )

        progress = (current_line + 1) / total_lines

        st.progress(progress)
        st.write(f"Reading Progress: {int(progress * 100)}%")

        for i, line in enumerate(lines):

            if i == current_line:

                st.markdown(
                    f"""
                    <div style="
                    background-color:#fff3b0;
                    color:black;
                    font-family:{font_family};
                    font-size:{font_size}px;
                    padding:12px;
                    border-radius:8px;
                    border-left:6px solid orange;
                    margin-bottom:10px;
                    ">
                    {line}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                    opacity:0.35;
                    font-family:{font_family};
                    font-size:{font_size}px;
                    padding:10px;
                    margin-bottom:10px;
                    ">
                    {line}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    elif not speak_button:

        st.markdown(styled_text, unsafe_allow_html=True)
