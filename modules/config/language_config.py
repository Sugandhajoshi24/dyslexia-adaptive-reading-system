"""
Language configuration for multilingual support.

Each language defines:
    - Available features
    - Font options
    - TTS codes
    - Script detection ranges
    - Sentence splitting patterns
"""

LANGUAGE_CONFIG = {
    "en": {
        "name": "English",
        "flag": "🇬🇧",
        "tts_code": "en",
        "speech_lang": "en-US",
        "sentence_endings": r'[.!?]',
        "syllable_support": True,
        "syllable_engine": "pyphen",
        "bionic_support": True,
        "tooltip_support": True,
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
        "syllable_support": True,
        "syllable_engine": "indic",
        "bionic_support": False,
        "tooltip_support": False,
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
        "sample_text": (
            "सहायक पठन प्रणालियाँ डिस्लेक्सिया और अन्य पठन चुनौतियों से जूझ रहे "
            "व्यक्तियों की सहायता के लिए तेजी से महत्वपूर्ण होती जा रही हैं। "
            "पारंपरिक पठन इंटरफेस अक्सर इन उपयोगकर्ताओं द्वारा अनुभव की जाने वाली "
            "दृश्य और संज्ञानात्मक कठिनाइयों को ध्यान में रखने में विफल रहते हैं। "
            "यह अध्ययन एक अनुकूली पठन दृष्टिकोण प्रस्तावित करता है जो अक्षर "
            "विभाजन, अनुकूलन योग्य दृश्य लेआउट और समकालिक ऑडियो कथन को एकीकृत करता है।"
        ),
    },
}


def get_language_config(lang_code):
    """Get config for a language. Defaults to English."""
    return LANGUAGE_CONFIG.get(lang_code, LANGUAGE_CONFIG["en"])


def get_supported_languages():
    """Return dict of code: name for all supported languages."""
    return {
        code: conf["name"] + " " + conf["flag"]
        for code, conf in LANGUAGE_CONFIG.items()
    }


def get_language_codes():
    """Return list of supported language codes."""
    return list(LANGUAGE_CONFIG.keys())