"""
Renders document difficulty analysis as an expandable card.
Fully config-driven — no language-specific if/else in display logic.

Language awareness comes entirely from language_config.py analysis_labels.
The readability bar thresholds and labels are now language-aware:
- English: Flesch-Kincaid thresholds (70 = easy, 50 = moderate)
- Hindi/Tamil: Custom complexity thresholds (60 = easy, 35 = moderate)
  because their ease score uses a different formula entirely.
"""

import streamlit as st
from modules.config.language_config import get_language_config


# ── Readability bar config per analysis method ────────────────────────────
# Each method defines its own thresholds and labels.
# Add new languages here — do NOT add if/else in render function.

_READABILITY_CONFIG = {
    "flesch_kincaid": {
        # Flesch Reading Ease: 0–100, higher = easier
        # Standard FK thresholds
        "high_threshold": 70,
        "mid_threshold":  50,
        "high_label":     "Easy to read",
        "mid_label":      "Moderate",
        "low_label":      "Difficult to read",
    },
    "custom_complexity": {
        # Custom ease score: 100 - (complexity * 5)
        # Different scale — lower complexity texts score higher
        # Thresholds calibrated for Hindi/Tamil complexity range
        "high_threshold": 60,
        "mid_threshold":  35,
        "high_label":     "Accessible",
        "mid_label":      "Moderately complex",
        "low_label":      "Highly complex",
    },
}

# Fallback if analysis_method not found in config
_DEFAULT_READABILITY_CONFIG = _READABILITY_CONFIG["flesch_kincaid"]


def _get_readability_config(analysis_method):
    """
    Return readability bar config for the given analysis method.
    Safe fallback to Flesch-Kincaid if method unknown.
    """
    return _READABILITY_CONFIG.get(analysis_method, _DEFAULT_READABILITY_CONFIG)


def render_document_stats(analysis, theme_config, lang="en"):
    """
    Render document difficulty analysis.

    All labels come from language_config analysis_labels.
    Readability bar thresholds come from _READABILITY_CONFIG
    keyed by analysis_method — not hardcoded per language.
    """
    t = theme_config
    lang_config = get_language_config(lang)
    labels = lang_config.get("analysis_labels", {})
    analysis_method = lang_config.get("analysis_method", "flesch_kincaid")

    level = analysis["difficulty_level"]

    level_config = {
        "Easy":     {"emoji": "🟢", "color": "#4CAF50"},
        "Medium":   {"emoji": "🟡", "color": "#FF9800"},
        "Hard":     {"emoji": "🟠", "color": "#f44336"},
        "Advanced": {"emoji": "🔴", "color": "#9C27B0"},
    }

    lc = level_config.get(level, level_config["Medium"])

    with st.expander(
        "📊 Document Analysis — " + lc["emoji"] + " " + level + " Level",
        expanded=False
    ):

        # ── Top metrics row ───────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Difficulty",
                level,
                help=labels.get(
                    "difficulty_help",
                    "Overall difficulty assessment"
                )
            )

        with c2:
            st.metric(
                labels.get("grade_label", "Grade Level"),
                str(analysis["flesch_kincaid_grade"]),
                help=labels.get("grade_help", "Estimated grade level")
            )

        with c3:
            st.metric(
                "Difficult Words",
                str(analysis["difficult_word_pct"]) + "%",
                help=(
                    str(analysis["difficult_word_count"])
                    + " out of "
                    + str(analysis["total_words"])
                    + " words"
                )
            )

        with c4:
            st.metric(
                "Reading Time",
                str(analysis["reading_time_minutes"]) + " min",
                help=labels.get(
                    "reading_speed_help",
                    "Estimated reading time"
                )
            )

        # ── Detail row ────────────────────────────────────────
        st.markdown(
            "<div style='height:8px;'></div>",
            unsafe_allow_html=True
        )

        c5, c6, c7, c8 = st.columns(4)

        with c5:
            st.metric("Total Words", analysis["total_words"])

        with c6:
            st.metric("Total Sentences", analysis["total_sentences"])

        with c7:
            st.metric(
                "Avg Word Length",
                str(analysis["avg_word_length"]) + " chars"
            )

        with c8:
            st.metric(
                labels.get("syllable_label", "Avg Syllables/Word"),
                str(analysis["avg_syllables_per_word"]),
                help=labels.get("syllable_help", "")
            )

        # ── Readability bar ───────────────────────────────────
        # Thresholds and labels are method-aware — not hardcoded FK values
        ease = analysis["flesch_reading_ease"]
        rc = _get_readability_config(analysis_method)

        if ease >= rc["high_threshold"]:
            ease_label = rc["high_label"]
            ease_color = "#4CAF50"
        elif ease >= rc["mid_threshold"]:
            ease_label = rc["mid_label"]
            ease_color = "#FF9800"
        else:
            ease_label = rc["low_label"]
            ease_color = "#f44336"

        readability_title = labels.get("readability_label", "Readability Score")
        bar_label = (
            readability_title
            + ": "
            + str(ease)
            + "/100 — "
            + ease_label
        )

        st.markdown(
            """
            <div style='margin-top:10px;'>
                <div style='font-size:13px;font-weight:600;margin-bottom:4px;'>
                    """ + bar_label + """
                </div>
                <div style='
                    background:#e0e0e0;
                    border-radius:8px;
                    height:8px;
                    width:100%;
                '>
                    <div style='
                        background:""" + ease_color + """;
                        width:""" + str(ease) + """%;
                        height:8px;
                        border-radius:8px;
                    '></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ── Method explanation caption ─────────────────────────
        # This text is set per-language in language_config.py
        # English shows FK explanation
        # Hindi/Tamil show custom complexity explanation
        explanation = labels.get("method_explanation", "")
        if explanation:
            st.caption(explanation)