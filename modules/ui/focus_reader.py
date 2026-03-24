import streamlit as st


def render_focus_mode(
    sentences_plain,
    sentences_rich,
    idx,
    total,
    theme_config,
    font_family,
    font_size,
    line_spacing,
    letter_spacing,
    audio_cache
):
    t = theme_config
    pct = int(((idx + 1) / total) * 100)

    # Use theme-aware colors for progress card
    prog_text = t.get("prog_text", t["text"])
    prog_bg   = t.get("prog_bg", t["card"])

    # ══════════════════════════════════════════════════════
    # PROGRESS CARD — theme-aware colors
    # ══════════════════════════════════════════════════════
    st.markdown(f"""
        <div style='
            background: {prog_bg};
            border: 1px solid {t["border"]};
            border-radius: 14px;
            padding: 16px 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        '>
            <div style='
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            '>
                <span style='
                    font-size: 15px;
                    font-weight: 700;
                    color: {prog_text};
                '>
                    📄 Sentence
                    <span style='color: {t["accent"]}; font-size: 18px;'>
                        {idx + 1}
                    </span>
                    of {total}
                </span>
                <span style='
                    font-size: 15px;
                    font-weight: 700;
                    color: {t["accent"]};
                '>
                    {pct}%
                </span>
            </div>
            <div style='
                background: {t["border"]};
                border-radius: 10px;
                height: 10px;
                width: 100%;
                overflow: hidden;
            '>
                <div style='
                    background: {t["accent"]};
                    width: {pct}%;
                    height: 10px;
                    border-radius: 10px;
                    transition: width 0.4s ease;
                '></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # NAVIGATION + AUDIO
    # ══════════════════════════════════════════════════════
    n1, n2, n3, n4, n5 = st.columns([1, 1, 1, 1, 3])

    with n1:
        if st.button("⏮ First", use_container_width=True, key="fm_first"):
            st.session_state.focus_idx = 0
            st.rerun()

    with n2:
        if st.button("◀ Prev", use_container_width=True, key="fm_prev"):
            if idx > 0:
                st.session_state.focus_idx -= 1
                st.rerun()

    with n3:
        if st.button("Next ▶", use_container_width=True, key="fm_next"):
            if idx < total - 1:
                st.session_state.focus_idx += 1
                st.rerun()

    with n4:
        if st.button("Last ⏭", use_container_width=True, key="fm_last"):
            st.session_state.focus_idx = total - 1
            st.rerun()

    with n5:
        if idx in audio_cache:
            st.audio(audio_cache[idx], format="audio/mp3")
        else:
            st.caption("🎵 Generating audio…")

    # Spacer
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # READING PANEL
    # ══════════════════════════════════════════════════════

    # Previous sentence (faded)
    if idx > 0:
        st.markdown(f"""
            <div style='
                border-left: 3px solid {t["border"]};
                border-radius: 8px;
                padding: 12px 22px;
                margin-bottom: 12px;
                font-family: "{font_family}", sans-serif;
                font-size: {int(font_size * 0.88)}px;
                line-height: {line_spacing};
                letter-spacing: {letter_spacing}px;
                color: {t["muted"]};
            '>
                <span style='
                    background: {t["border"]};
                    font-size: 10px; font-weight: 700;
                    padding: 1px 7px; border-radius: 10px;
                    margin-right: 8px; vertical-align: middle;
                '>{idx}</span>
                {sentences_rich[idx - 1]}
            </div>
        """, unsafe_allow_html=True)

    # Active sentence
    st.markdown(f"""
        <div style='
            background: {t["active_sent"]};
            border-left: 5px solid {t["accent"]};
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 12px;
            font-family: "{font_family}", sans-serif;
            font-size: {font_size}px;
            line-height: {line_spacing};
            letter-spacing: {letter_spacing}px;
            color: {t["text"]};
            box-shadow: 0 3px 14px rgba(0,0,0,0.09);
        '>
            <span style='
                background: {t["badge_bg"]};
                color: {t["badge_text"]};
                font-size: 11px; font-weight: 700;
                padding: 2px 9px; border-radius: 12px;
                margin-right: 10px; vertical-align: middle;
            '>{idx + 1}</span>
            {sentences_rich[idx]}
        </div>
    """, unsafe_allow_html=True)

    # Download audio
    if idx in audio_cache:
        st.download_button(
            label=f"⬇️ Download Sentence {idx + 1} Audio",
            data=audio_cache[idx],
            file_name=f"sentence_{idx + 1}.mp3",
            mime="audio/mp3",
            key=f"dl_sent_{idx}"
        )

    # Next sentence (faded)
    if idx < total - 1:
        st.markdown(f"""
            <div style='
                border-left: 3px solid {t["border"]};
                border-radius: 8px;
                padding: 12px 22px;
                margin-top: 12px;
                font-family: "{font_family}", sans-serif;
                font-size: {int(font_size * 0.88)}px;
                line-height: {line_spacing};
                letter-spacing: {letter_spacing}px;
                color: {t["muted"]};
            '>
                <span style='
                    background: {t["border"]};
                    font-size: 10px; font-weight: 700;
                    padding: 1px 7px; border-radius: 10px;
                    margin-right: 8px; vertical-align: middle;
                '>{idx + 2}</span>
                {sentences_rich[idx + 1]}
            </div>
        """, unsafe_allow_html=True)