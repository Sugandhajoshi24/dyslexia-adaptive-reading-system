from gtts import gTTS
import os
import time


def generate_audio(text):

    os.makedirs("downloads", exist_ok=True)

    filename = f"downloads/audio_{int(time.time())}.mp3"

    tts = gTTS(text=text, lang="en")

    tts.save(filename)

    return filename