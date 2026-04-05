"""
Word Tooltip — Pure CSS hover implementation.

English only. Normal reading mode only.

Design decisions:
- Pure CSS hover — no JavaScript, no iframe communication
- No dictionary API — removed for reliability
- Tooltip text comes from data-word attribute via CSS attr()
- Survives Streamlit re-renders — no event listeners to lose
- Works on Streamlit Cloud — no cross-origin iframe issues
"""

import streamlit as st


def inject_tooltip_system(theme_config):
    """
    Inject pure CSS tooltip into the main Streamlit page.

    Method: st.markdown only — no components.html, no JavaScript.
    CSS :hover is handled entirely by the browser.
    Survives Streamlit re-renders because CSS is stateless.

    Tooltip content comes from data-word attribute on each
    .tooltip-trigger span — set by difficulty_detector.py.
    No changes needed in difficulty_detector.py.
    """
    t = theme_config

    st.markdown(
        """
        <style>

        /* ── Tooltip trigger word ────────────────────────────────
           .tooltip-trigger class is set by difficulty_detector.py
           on every highlighted difficult word span.
           position:relative is required for ::before positioning.
        ─────────────────────────────────────────────────────── */
        .tooltip-trigger {
            position: relative;
            cursor: help;
        }

        /* ── Tooltip bubble ──────────────────────────────────────
           Uses CSS attr(data-word) to read the word directly
           from the span's data-word attribute.
           No JavaScript needed to populate this content.

           Positioned above the word.
           Hidden by default — shown only on :hover.
        ─────────────────────────────────────────────────────── */
        .tooltip-trigger::before {
            content: "Difficult word: " attr(data-word);

            /* Hidden until hover */
            display: block;
            visibility: hidden;
            opacity: 0;
            pointer-events: none;

            /* Position above the trigger word */
            position: absolute;
            bottom: calc(100% + 7px);
            left: 50%;
            transform: translateX(-50%);

            /* Prevent overflow on long words */
            white-space: normal;
            max-width: 220px;
            word-wrap: break-word;

            z-index: 9999;

            /* Appearance — theme-aware colors */
            background: """ + t.get('card', '#f7f7f7') + """;
            color: """ + t.get('text', '#1a1a1a') + """;
            border: 1px solid """ + t.get('border', '#e0e0e0') + """;
            border-radius: 8px;
            padding: 5px 12px;
            font-size: 12px;
            font-family: Arial, sans-serif;
            font-weight: 500;
            line-height: 1.4;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);

            /* Smooth reveal */
            transition: opacity 0.15s ease, visibility 0.15s ease;
        }

        /* ── Arrow pointing down toward the word ─────────────────
           ::after creates the small triangle below the bubble.
           Matches border color of the tooltip bubble.
        ─────────────────────────────────────────────────────── */
        .tooltip-trigger::after {
            content: '';

            display: block;
            visibility: hidden;
            opacity: 0;
            pointer-events: none;

            position: absolute;
            bottom: calc(100% + 2px);
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;

            /* Triangle via border trick */
            border: 5px solid transparent;
            border-top-color: """ + t.get('border', '#e0e0e0') + """;

            transition: opacity 0.15s ease, visibility 0.15s ease;
        }

        /* ── Show both bubble and arrow on hover ─────────────── */
        .tooltip-trigger:hover::before,
        .tooltip-trigger:hover::after {
            visibility: visible;
            opacity: 1;
        }

        /* ── Hide old tooltip-content spans ──────────────────────
           difficulty_detector.py still renders:
               <span class='tooltip-content'></span>
           inside each highlight span.
           We hide these completely — they remain in DOM safely
           but have no visible effect.
           CSS ::before handles display now.
        ─────────────────────────────────────────────────────── */
        .tooltip-content {
            display: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def get_tooltip_css(theme_config):
    """DEPRECATED — use inject_tooltip_system() instead."""
    return ""