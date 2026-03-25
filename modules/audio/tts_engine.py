"""
TTS engine — multilingual.
"""

from gtts import gTTS
import os
import re
import uuid


def generate_audio(text, lang='en', slow=False):
    """
    Generate MP3 audio from text.
    Supports: en, hi, ta, and 50+ languages via gTTS.
    """
    try:
        filename = "downloads/audio_" + uuid.uuid4().hex + ".mp3"
        os.makedirs("downloads", exist_ok=True)

        clean = re.sub(r'<[^>]+>', '', text)
        clean = clean.strip()

        if not clean:
            return None

        tts = gTTS(text=clean, lang=lang, slow=slow)
        tts.save(filename)

        return filename

    except Exception as e:
        print("[TTS ERROR] " + str(e))
        return None