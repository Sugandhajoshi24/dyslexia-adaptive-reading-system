import streamlit as st
import time
import re
import os

from modules.document_processing.extract_text import extract_pdf_text
from modules.text_processing.syllable_splitter import syllabify_difficult_words
from modules.text_processing.sentence_splitter import split_into_lines
from modules.text_processing.text_cleaner import clean_text
from modules.text_processing.difficulty_detector import detect_difficult_words, highlight_difficult_words
from modules.reader.theme_manager import get_theme
from modules.audio.tts_engine import generate_audio
from modules.export.pdf_exporter import generate_accessible_pdf


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Dyslexia Adaptive Reader",
    page_icon="📖",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "focus_line" not in st.session_state:
    st.session_state.focus_line = 0

if "sentence_audio" not in st.session_state:
    st.session_state.sentence_audio = {}

if "full_audio" not in st.session_state:
    st.session_state.full_audio = None


# ---------------- HEADER ----------------

st.title("Dyslexia-Friendly Adaptive Reading System")

st.write(
"""
Assistive reading interface with syllable support, customizable layouts,
focus mode navigation, and text-to-speech narration.
"""
)

# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload PDF or TXT Document",
    type=["pdf", "txt"]
)

st.info("Upload a document to begin reading.")

# ---------------- MAIN PIPELINE ----------------

if uploaded_file is not None:

    # -------- SIDEBAR --------

    st.sidebar.title("Reader Controls")

    font_family = st.sidebar.selectbox(
        "Font",
        ["Arial", "Verdana", "Georgia", "Times New Roman"]
    )

    font_size = st.sidebar.slider("Font Size", 14, 40, 20)

    line_spacing = st.sidebar.slider("Line Spacing", 1.0, 3.0, 1.5)

    letter_spacing = st.sidebar.slider("Letter Spacing", 0.0, 5.0, 1.0)

    theme = st.sidebar.selectbox(
        "Color Theme",
        ["Default", "Sepia", "Dark", "High Contrast"]
    )

    use_syllables = st.sidebar.checkbox("Enable Syllable Splitting")

    highlight_difficulty = st.sidebar.checkbox("Highlight Difficult Words")

    focus_mode = st.sidebar.checkbox("Enable Focus Mode")

    generate_full_audio = st.sidebar.button("Generate Full Audio")

    export_pdf = st.sidebar.button("Download Dyslexia-Friendly PDF")

    # -------- TEXT EXTRACTION --------

    if uploaded_file.type == "application/pdf":
        original_text = extract_pdf_text(uploaded_file)
    else:
        original_text = uploaded_file.read().decode("utf-8")

    original_text = clean_text(original_text)

    # -------- DIFFICULT WORD DETECTION --------

    difficult_words = set()

    if use_syllables or highlight_difficulty:
        difficult_words = detect_difficult_words(original_text)

    # -------- TEXT PIPELINE --------

    reader_text = original_text

    if use_syllables:
        reader_text = syllabify_difficult_words(reader_text, difficult_words)

    if highlight_difficulty:
        reader_text = highlight_difficult_words(reader_text, difficult_words)

    # -------- THEME --------

    background, text_color = get_theme(theme)

    # -------- FULL AUDIO GENERATION --------

    if generate_full_audio:

        with st.spinner("Generating full narration audio..."):

            tts_text = re.sub(r'<[^>]+>', '', reader_text)
            tts_text = tts_text.replace("-", "")

            st.session_state.full_audio = generate_audio(tts_text)

    # ---------------- DISPLAY ----------------

    st.subheader("Reading Panel")
    st.divider()

    # -------- FOCUS MODE --------

    if focus_mode:

        clean_focus_text = re.sub(r'<[^>]+>', '', reader_text)

        lines = split_into_lines(clean_focus_text)
        total_lines = len(lines)

        col1, col2 = st.columns(2)

        if col1.button("Previous Sentence"):
            st.session_state.focus_line = max(0, st.session_state.focus_line - 1)

        if col2.button("Next Sentence"):
            st.session_state.focus_line = min(total_lines - 1, st.session_state.focus_line + 1)

        current_line = st.session_state.focus_line
        current_sentence = lines[current_line]

        # -------- SENTENCE AUDIO (LAZY GENERATION) --------

        if current_line not in st.session_state.sentence_audio:

            with st.spinner("Generating sentence audio..."):

                audio_path = generate_audio(current_sentence)
                st.session_state.sentence_audio[current_line] = audio_path

        audio_file = st.session_state.sentence_audio[current_line]

        if os.path.exists(audio_file):

            with open(audio_file, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        # -------- PROGRESS --------

        progress = (current_line + 1) / total_lines
        st.progress(progress)
        st.caption(f"Reading progress: {int(progress * 100)}%")

        # -------- DISPLAY WINDOW --------

        start = max(0, current_line - 2)
        end = min(total_lines, current_line + 3)

        for i in range(start, end):

            if i == current_line:

                st.markdown(
                    f"""
                    <div style="
                        background-color:rgba(255,214,102,0.6);
                        padding:12px;
                        border-radius:8px;
                        margin-bottom:10px;
                        font-size:{font_size}px;
                        font-family:{font_family};
                    ">
                    {lines[i]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        opacity:0.35;
                        margin-bottom:10px;
                        font-size:{font_size}px;
                        font-family:{font_family};
                    ">
                    {lines[i]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        formatted_text = reader_text.replace(
            "\n\n", '</div><div style="margin-bottom:1.2em;">'
        )

        styled_text = f"""
        <div style="
            background-color:{background};
            color:{text_color};
            font-family:{font_family};
            font-size:{font_size}px;
            line-height:{line_spacing + 0.4};
            letter-spacing:{letter_spacing}px;
            word-spacing:0.08em;
            padding:50px;
            border-radius:14px;
            max-width:750px;
            margin:40px auto;
        ">
        <div style="margin-bottom:1.2em;">
        {formatted_text}
        </div>
        </div>
        """

        st.markdown(styled_text, unsafe_allow_html=True)

    # -------- FULL AUDIO DOWNLOAD --------

    if st.session_state.full_audio and os.path.exists(st.session_state.full_audio):

        with open(st.session_state.full_audio, "rb") as f:

            st.download_button(
                "Download Full Narration",
                f,
                file_name="reading_audio.mp3",
                mime="audio/mp3"
            )

    # -------- PDF EXPORT --------

    if export_pdf:

        with st.spinner("Generating PDF..."):

            pdf_text = re.sub(r'<[^>]+>', '', reader_text)

            pdf_file = generate_accessible_pdf(
                pdf_text,
                font_size=font_size,
                line_spacing=line_spacing
            )

        with open(pdf_file, "rb") as f:

            st.download_button(
                "Download Accessible PDF",
                f,
                file_name="dyslexia_reader.pdf",
                mime="application/pdf"
            )