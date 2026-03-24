from gtts import gTTS
import os
import uuid


def generate_audio(text, lang='en', slow=False):
    """Generate audio from text using Google Text-to-Speech"""

    try:
        os.makedirs("downloads", exist_ok=True)

        filename = f"downloads/audio_{uuid.uuid4().hex[:8]}.mp3"

        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(filename)

        return filename

    except Exception as e:
        print(f"TTS ERROR: {e}")
        return None