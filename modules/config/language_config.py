"""
Language configuration — single source of truth for all language features.

To add a new language:
1. Add an entry here
2. Add word detection in difficulty_detector.py
3. Add segmenter if needed
4. Add font to assets/fonts/
5. Everything else works automatically
"""

LANGUAGE_CONFIG = {
    "en": {
        "name": "English",
        "flag": "🇬🇧",
        "tts_code": "en",
        "speech_lang": "en-US",
        "sentence_endings": r'[.!?]',

        "syllable_support": True,
        "segmentation_support": True,
        "segmentation_label": "Syllable Splitting",
        "segmentation_help": "Break difficult words into syllables for easier reading",
        "segmentation_engine": "pyphen",

        "bionic_support": True,
        "tooltip_support": True,

        "guided_method": "browser",
        "focus_audio": "gtts",
        "export_audio": "gtts",

        "analysis_method": "flesch_kincaid",
        "analysis_labels": {
            "grade_label": "Grade Level",
            "grade_help": (
                "Flesch-Kincaid grade level — "
                "the US school grade needed to understand this text"
            ),
            "syllable_label": "Avg Syllables/Word",
            "syllable_help": "Average number of syllables per word",
            "readability_label": "Readability Score (Flesch-Kincaid)",
            "method_explanation": (
                "📐 Analysis uses the Flesch-Kincaid readability formula, "
                "which measures sentence length and syllable complexity."
            ),
            "reading_speed_wpm": 120,
            "reading_speed_help": "Estimated at 120 words/min (dyslexia-adjusted)",
            "difficulty_help": (
                "Based on word frequency, sentence length, and readability score"
            ),
        },

        "font_options": [
            "Arial",
            "OpenDyslexic",
            "Georgia",
            "Verdana",
            "Tahoma",
            "Comic Sans MS",
        ],
        "default_font": "Arial",
        "export_font_name": "OpenDyslexic",
        "export_font_file": "OpenDyslexic3-Regular.ttf",
        "browser_font_file": "OpenDyslexic3-Regular.ttf",
        "browser_font_family": "OpenDyslexic",

        "sample_text": (
            "Assistive reading systems have become increasingly important for supporting "
            "individuals with dyslexia and other reading challenges. Traditional reading "
            "interfaces often fail to account for the visual and cognitive difficulties "
            "experienced by these users. This system proposes an adaptive reading approach "
            "that integrates syllable segmentation, customizable visual layouts, and "
            "synchronized audio narration. The system transforms traditional documents into "
            "accessible formats designed to improve readability."
        ),
    },

    "hi": {
        "name": "Hindi",
        "flag": "🇮🇳",
        "tts_code": "hi",
        "speech_lang": "hi-IN",
        "sentence_endings": r'[.!?।]',

        "syllable_support": False,
        "segmentation_support": True,
        "segmentation_label": "Word Segmentation",
        "segmentation_help": "Segment difficult words into readable visual chunks",
        "segmentation_engine": "indic-akshara",

        "bionic_support": True,
        "tooltip_support": False,

        "guided_method": "gtts",
        "focus_audio": "gtts",
        "export_audio": "gtts",

        "analysis_method": "custom_complexity",
        "analysis_labels": {
            "grade_label": "Complexity Level",
            "grade_help": (
                "Estimated reading complexity based on word length, "
                "conjunct characters, and sentence structure"
            ),
            "syllable_label": "Avg Conjuncts/Word",
            "syllable_help": (
                "Average conjunct consonants (virama) per word "
                "— indicates visual complexity"
            ),
            "readability_label": "Readability Score",
            "method_explanation": (
                "📐 Analysis uses a custom complexity formula based on "
                "word length, conjunct consonant density (virama), "
                "and sentence structure."
            ),
            "reading_speed_wpm": 100,
            "reading_speed_help": (
                "Estimated at 100 words/min (adjusted for script complexity)"
            ),
            "difficulty_help": (
                "Based on word complexity, conjunct density, and sentence length"
            ),
        },

        "font_options": [
            "Noto Sans Devanagari",
            "Arial",
            "Mangal",
        ],
        "default_font": "Noto Sans Devanagari",
        "export_font_name": "NotoDevanagari",
        "export_font_file": "NotoSansDevanagari-Regular.ttf",
        "browser_font_file": "NotoSansDevanagari-VariableFont_wdth,wght.ttf",
        "browser_font_family": "Noto Sans Devanagari",

        # Clean sample text — typed fresh, no hidden Unicode characters
        "sample_text": (
            "सहायक पठन प्रणालियाँ डिस्लेक्सिया और अन्य पठन चुनौतियों से "
            "जूझ रहे व्यक्तियों की सहायता के लिए तेजी से महत्वपूर्ण होती "
            "जा रही हैं। पारंपरिक पठन इंटरफेस अक्सर इन उपयोगकर्ताओं द्वारा "
            "अनुभव की जाने वाली दृश्य और संज्ञानात्मक कठिनाइयों को ध्यान "
            "में रखने में विफल रहते हैं। यह प्रणाली एक अनुकूली पठन "
            "दृष्टिकोण प्रस्तावित करती है जो शब्द विभाजन, अनुकूलन योग्य "
            "दृश्य लेआउट और समकालिक ऑडियो वर्णन को एकीकृत करती है।"
        ),
    },

    "ta": {
        "name": "Tamil",
        "flag": "🇮🇳",
        "tts_code": "ta",
        "speech_lang": "ta-IN",
        "sentence_endings": r'[.!?]',

        "syllable_support": False,
        "segmentation_support": True,
        "segmentation_label": "Word Segmentation",
        "segmentation_help": "Segment difficult Tamil words into readable visual chunks",
        "segmentation_engine": "indic-akshara",

        "bionic_support": True,
        "tooltip_support": False,

        "guided_method": "gtts",
        "focus_audio": "gtts",
        "export_audio": "gtts",

        "analysis_method": "custom_complexity",
        "analysis_labels": {
            "grade_label": "Complexity Level",
            "grade_help": (
                "Estimated reading complexity based on "
                "word length and character structure"
            ),
            "syllable_label": "Avg Complexity/Word",
            "syllable_help": "Average structural complexity per word",
            "readability_label": "Readability Score",
            "method_explanation": (
                "📐 Analysis uses a custom complexity formula based on "
                "word length, character composition, and sentence structure."
            ),
            "reading_speed_wpm": 100,
            "reading_speed_help": (
                "Estimated at 100 words/min (adjusted for script complexity)"
            ),
            "difficulty_help": (
                "Based on word complexity, character structure, and sentence length"
            ),
        },

        "font_options": [
            "Noto Sans Tamil",
            "Arial",
        ],
        "default_font": "Noto Sans Tamil",
        "export_font_name": "NotoTamil",
        "export_font_file": "static/NotoSansTamil-Regular.ttf",
        "browser_font_file": "static/NotoSansTamil-Regular.ttf",
        "browser_font_family": "Noto Sans Tamil",

        # Clean Tamil sample — uses . for sentence endings (not ।)
        # Multiple sentences so focus mode splits correctly
        "sample_text": (
            "டிஸ்லெக்சியா மற்றும் பிற வாசிப்பு சவால்களை எதிர்கொள்ளும் "
            "நபர்களுக்கு உதவும் வகையில் உதவி வாசிப்பு அமைப்புகள் "
            "முக்கியத்துவம் பெற்று வருகின்றன. "
            "பாரம்பரிய வாசிப்பு இடைமுகங்கள் இந்த பயனர்கள் அனுபவிக்கும் "
            "காட்சி மற்றும் அறிவாற்றல் சிரமங்களை கணக்கில் "
            "எடுத்துக்கொள்ளத் தவறுகின்றன. "
            "இந்த அமைப்பு சொல் பிரிப்பு, தனிப்பயனாக்கக்கூடிய "
            "தளவமைப்பு மற்றும் ஒத்திசைவான ஒலி விவரிப்பை "
            "ஒருங்கிணைக்கிறது. "
            "கற்றல் சிரமம் கொண்ட மாணவர்களுக்கு தொழில்நுட்ப உதவி "
            "கருவிகள் பெரிய மாற்றத்தை ஏற்படுத்தக்கூடும். "
            "வாசிப்பை அணுகக்கூடியதாக மற்றும் தெளிவாக மாற்றும் "
            "முயற்சிகள் கல்வி சமத்துவத்தை வலுப்படுத்துகின்றன."
        ),
    },
}


def get_language_config(lang_code):
    """Get config for a language. Defaults to English."""
    return LANGUAGE_CONFIG.get(lang_code, LANGUAGE_CONFIG["en"])


def get_supported_languages():
    """Return dict of code: display_name for all supported languages."""
    return {
        code: conf["name"] + " " + conf["flag"]
        for code, conf in LANGUAGE_CONFIG.items()
    }


def get_language_codes():
    """Return list of supported language codes."""
    return list(LANGUAGE_CONFIG.keys())


def supports_feature(lang_code, feature):
    """Check if a language supports a specific feature."""
    config = get_language_config(lang_code)
    return config.get(feature, False)