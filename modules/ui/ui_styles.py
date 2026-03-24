import os
import base64


def get_font_face_css():
    """Load OpenDyslexic font into browser via base64 embedded @font-face"""

    font_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "assets", "fonts", "OpenDyslexic3-Regular.ttf"
    )

    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            font_data = base64.b64encode(f.read()).decode("utf-8")

        return f"""
        <style>
        @font-face {{
            font-family: 'OpenDyslexic';
            src: url(data:font/truetype;base64,{font_data}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        </style>
        """
    else:
        return "<!-- OpenDyslexic font file not found -->"


def load_ui_styles():
    return """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 16px;
        color: gray;
        margin-bottom: 30px;
    }

    .reader-container {
        max-width: 850px;
        margin: auto;
        padding: 40px;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    .reader-text {
        text-align: left;
        word-spacing: 4px;
    }

    .difficult-word {
        background-color: rgba(255,235,140,0.45);
        padding: 2px 4px;
        border-radius: 4px;
    }

    </style>
    """