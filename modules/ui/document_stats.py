"""
Renders document difficulty analysis as an expandable card.
"""

import streamlit as st


def render_document_stats(analysis, theme_config):
    """
    Render document difficulty analysis as an expandable section.
    """
    t = theme_config

    level = analysis["difficulty_level"]

    # Level colors and emojis
    level_config = {
        "Easy":     {"emoji": "🟢", "color": "#4CAF50"},
        "Medium":   {"emoji": "🟡", "color": "#FF9800"},
        "Hard":     {"emoji": "🟠", "color": "#f44336"},
        "Advanced": {"emoji": "🔴", "color": "#9C27B0"},
    }

    lc = level_config.get(level, level_config["Medium"])

    with st.expander(f"📊 Document Analysis — {lc['emoji']} {level} Level", expanded=False):

        # Top metrics row
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Difficulty",
                level,
                help="Based on word frequency, sentence length, and readability"
            )

        with c2:
            st.metric(
                "Grade Level",
                f"{analysis['flesch_kincaid_grade']}",
                help="Flesch-Kincaid grade level"
            )

        with c3:
            st.metric(
                "Difficult Words",
                f"{analysis['difficult_word_pct']}%",
                help=f"{analysis['difficult_word_count']} out of {analysis['total_words']} words"
            )

        with c4:
            st.metric(
                "Reading Time",
                f"{analysis['reading_time_minutes']} min",
                help="Estimated at 120 words/min (dyslexia-adjusted)"
            )

        # Detail row
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        c5, c6, c7, c8 = st.columns(4)

        with c5:
            st.metric("Total Words", analysis["total_words"])

        with c6:
            st.metric("Total Sentences", analysis["total_sentences"])

        with c7:
            st.metric("Avg Word Length", f"{analysis['avg_word_length']} chars")

        with c8:
            st.metric("Avg Sentence Length", f"{analysis['avg_sentence_length']} words")

        # Readability bar
        ease = analysis["flesch_reading_ease"]
        if ease >= 70:
            ease_label = "Easy to read"
            ease_color = "#4CAF50"
        elif ease >= 50:
            ease_label = "Moderate"
            ease_color = "#FF9800"
        else:
            ease_label = "Difficult to read"
            ease_color = "#f44336"

        st.markdown(f"""
            <div style='margin-top:10px;'>
                <div style='font-size:13px;font-weight:600;margin-bottom:4px;'>
                    Readability Score: {ease}/100 — {ease_label}
                </div>
                <div style='
                    background:#e0e0e0;
                    border-radius:8px;
                    height:8px;
                    width:100%;
                '>
                    <div style='
                        background:{ease_color};
                        width:{ease}%;
                        height:8px;
                        border-radius:8px;
                    '></div>
                </div>
            </div>
        """, unsafe_allow_html=True)