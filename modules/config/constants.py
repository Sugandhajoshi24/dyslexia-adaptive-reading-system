"""
Application-wide constants and default values.
"""

# ── Font options ──────────────────────────────────────────
FONT_OPTIONS = [
    "Arial",
    "OpenDyslexic",
    "Georgia",
    "Verdana",
    "Tahoma",
    "Comic Sans MS",
]

# ── Font size ─────────────────────────────────────────────
DEFAULT_FONT_SIZE = 20
MIN_FONT_SIZE = 14
MAX_FONT_SIZE = 40

# ── Line spacing ──────────────────────────────────────────
DEFAULT_LINE_SPACING = 1.8
MIN_LINE_SPACING = 1.0
MAX_LINE_SPACING = 3.0
LINE_SPACING_STEP = 0.1

# ── Letter spacing ────────────────────────────────────────
DEFAULT_LETTER_SPACING = 1.0
MIN_LETTER_SPACING = 0.0
MAX_LETTER_SPACING = 5.0
LETTER_SPACING_STEP = 0.5

# ── Adaptive line length ──────────────────────────────────
# Auto-calculated based on font size:
# Larger font → fewer words per line
# Base: 10 words at 16px, scales down as font increases
def get_max_line_width(font_size, letter_spacing):
    """Calculate optimal max-width in pixels for the reading panel."""
    avg_char_width = font_size * 0.55 + letter_spacing
    words_per_line = max(6, min(12, int(180 / font_size * 5)))
    avg_word_chars = 5
    max_width = int(words_per_line * avg_word_chars * avg_char_width) + 100
    return max(400, min(900, max_width))

# ── Audio ─────────────────────────────────────────────────
MAX_TTS_CHARS = 3000

# ── Reading modes ─────────────────────────────────────────
READING_MODES = [
    "📖 Normal Reading",
    "🔍 Focus Mode",
    "🔊 Guided Reading",
]

# ── Highlight modes ───────────────────────────────────────
HIGHLIGHT_MODES = [
    "All Difficult Words",
    "Smart",
]

# ── Sentence splitting ────────────────────────────────────
MIN_SENTENCE_LENGTH = 8

# ── Supported file types ─────────────────────────────────
SUPPORTED_FILE_TYPES = ["txt", "pdf", "docx"]

# ── Font path ─────────────────────────────────────────────
FONT_DIR = "assets/fonts"
FONT_FILENAME = "OpenDyslexic3-Regular.ttf"

# ── Bionic reading ────────────────────────────────────────
# Bold ratio: how much of each word to bold (0.3 = first 30%)
BIONIC_BOLD_RATIO = 0.4

# ── Sample text ───────────────────────────────────────────
SAMPLE_TEXT = (
    "Assistive reading systems have become increasingly important for supporting "
    "individuals with dyslexia and other reading challenges. Traditional reading "
    "interfaces often fail to account for the visual and cognitive difficulties "
    "experienced by these users. This system proposes an adaptive reading approach "
    "that integrates syllable segmentation, customizable visual layouts, and "
    "synchronized audio narration. The system transforms traditional documents into "
    "accessible formats designed to improve readability. Hippopotamuses are "
    "extraordinarily large semiaquatic mammals that predominantly inhabit "
    "sub-Saharan Africa. These magnificent creatures congregate near rivers and "
    "lakes to regulate their body temperature and protect their extraordinarily "
    "sensitive skin. Despite their appearance, hippopotamuses are surprisingly "
    "agile and can run at considerable speeds on land. Communication among "
    "hippopotamuses involves sophisticated vocalizations that travel both above "
    "and below water."
)