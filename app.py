import streamlit as st
import time
import re

from modules.document_processing.extract_text import extract_pdf_text
from modules.text_processing.syllable_splitter import syllabify_text
from modules.text_processing.sentence_splitter import split_into_lines
from modules.reader.theme_manager import get_theme
from modules.audio.tts_engine import generate_audio
from modules.text_processing.text_cleaner import clean_text
from modules.export.pdf_exporter import generate_accessible_pdf
from modules.text_processing.difficulty_detector import detect_difficult_words, highlight_difficult_words


# ---------- Session State ----------

if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

if "focus_line" not in st.session_state:
    st.session_state.focus_line = 0

if "auto_reading" not in st.session_state:
    st.session_state.auto_reading = False

if "last_move_time" not in st.session_state:
    st.session_state.last_move_time = time.time()


# ---------- UI ----------

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


# ---------- Main Logic ----------

if uploaded_file is not None:

    # ---------- Sidebar Controls ----------

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

    highlight_difficulty = st.sidebar.checkbox("Highlight Difficult Words")


    # ---------- Reading Controls ----------

    st.sidebar.header("Reading")

    start_reading = st.sidebar.button("▶ Start Reading")
    pause_reading = st.sidebar.button("⏸ Pause")

    if start_reading:
        st.session_state.auto_reading = True
        st.session_state.last_move_time = time.time()

    if pause_reading:
        st.session_state.auto_reading = False


    # ---------- Text Extraction ----------

    if uploaded_file.type == "application/pdf":
        text = extract_pdf_text(uploaded_file)
    else:
        text = uploaded_file.read().decode("utf-8")

    text = clean_text(text)

    # Keep original text for difficulty detection
    original_text = text


    # ---------- Detect Difficult Words ----------

    difficult_words = set()

    if highlight_difficulty:
        difficult_words = detect_difficult_words(original_text)


    # ---------- Apply Syllable Splitting ----------

    if use_syllables:
        text = syllabify_text(text)


    # ---------- Highlight Difficult Words ----------

    if highlight_difficulty:
        text = highlight_difficult_words(text, difficult_words)


    # ---------- Theme ----------

    background, text_color = get_theme(theme)


    # ---------- Audio ----------

    if start_reading:
        with st.spinner("Generating audio..."):

            # Remove HTML tags
            audio_text = re.sub(r'<[^>]+>', '', text)

            # Remove syllable hyphens
            audio_text = audio_text.replace("-", "")

            st.session_state.audio_file = generate_audio(audio_text)


    if st.session_state.audio_file:

        st.audio(st.session_state.audio_file)

        with open(st.session_state.audio_file, "rb") as file:
            st.download_button(
                label="Download Audio",
                data=file,
                file_name="reading_audio.mp3",
                mime="audio/mp3"
            )


    # ---------- Export ----------

    st.sidebar.header("Export Options")

    if st.sidebar.button("Download Dyslexia-Friendly PDF"):

        with st.spinner("Generating accessible PDF..."):
            pdf_file = generate_accessible_pdf(
                text,
                font_size=font_size,
                line_spacing=line_spacing
            )

        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Download Accessible PDF",
                data=file,
                file_name="dyslexia_reader.pdf",
                mime="application/pdf"
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
    ">
    {text}
    </div>
    """


    # ---------- Focus Mode ----------

    if focus_mode:

        lines = split_into_lines(text)
        total_lines = len(lines)

        if st.session_state.focus_line >= total_lines:
            st.session_state.focus_line = 0


        col1, col2 = st.columns(2)

        if col1.button("⬅ Previous Sentence"):
            if st.session_state.focus_line > 0:
                st.session_state.focus_line -= 1

        if col2.button("Next Sentence ➡"):
            if st.session_state.focus_line < total_lines - 1:
                st.session_state.focus_line += 1


        if st.session_state.auto_reading:

            current_time = time.time()

            if current_time - st.session_state.last_move_time > 5:

                if st.session_state.focus_line < total_lines - 1:
                    st.session_state.focus_line += 1
                    st.session_state.last_move_time = current_time
                    st.rerun()

                else:
                    st.session_state.auto_reading = False


        current_line = st.session_state.focus_line

        progress = (current_line + 1) / total_lines

        st.progress(progress)
        st.write(f"Reading Progress: {int(progress * 100)}%")


        start = max(0, current_line - 2)
        end = min(total_lines, current_line + 3)

        for i in range(start, end):

            line = lines[i]

            if i == current_line:

                st.markdown(
                    f"""
                    <div style="
                    background-color: rgba(255,214,102,0.6);
                    color:{text_color};
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
                    background-color:{background};
                    color:{text_color};
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

    else:

        st.markdown(styled_text, unsafe_allow_html=True)