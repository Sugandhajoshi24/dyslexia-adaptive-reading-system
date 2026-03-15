import os
import time
from gtts import gTTS

def generate_audio(text):

    folder = "downloads"

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{folder}/audio_{int(time.time())}.mp3"

    tts = gTTS(text)
    tts.save(filename)

    return filename