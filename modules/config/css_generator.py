"""
Generates dynamic CSS based on theme and font settings.
"""

from modules.config.constants import get_max_line_width


def generate_global_css(theme_config, font_family, font_size, line_spacing, letter_spacing):
    """Return a <style> block for the current theme + adaptive line width."""
    t = theme_config
    max_width = get_max_line_width(font_size, letter_spacing)

    return f"""
    <style>
    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1080px;
    }}
    .mode-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: {t['active_sent']}; color: {t['accent']};
        border: 1px solid {t['accent']}; border-radius: 20px;
        padding: 4px 16px; font-size: 13px; font-weight: 600;
        margin-bottom: 12px;
    }}
    .upload-hint {{
        border: 2px dashed #ccc; border-radius: 14px;
        padding: 28px; text-align: center; color: #999;
        font-size: 15px; margin-bottom: 18px;
    }}
    .reading-panel {{
        background: {t['card']}; border: 1px solid {t['border']};
        border-radius: 18px; padding: 38px 48px; margin-top: 14px;
        box-shadow: {t['panel_shadow']}; min-height: 260px;
        max-width: {max_width}px;
        margin-left: auto;
        margin-right: auto;
    }}
    .reader-text {{
        font-family: '{font_family}', sans-serif;
        font-size: {font_size}px; line-height: {line_spacing};
        letter-spacing: {letter_spacing}px; color: {t['text']};
        word-spacing: 4px;
    }}
    audio {{ width: 100%; border-radius: 8px; }}
    .stAlert {{ border-radius: 10px !important; }}
    </style>
    """