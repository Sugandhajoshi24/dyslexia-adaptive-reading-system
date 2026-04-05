"""
TTS engine — multilingual.
Returns file path. Strips invisible characters.

Stability guarantees:
- try/finally ensures partial/invalid temp files are deleted on failure
- valid files are NEVER deleted here (caller must delete after reading)
- orphaned files from previous crashed sessions are cleaned on import
"""

from gtts import gTTS
import os
import re
import uuid


# ── Invisible Unicode characters that break TTS and rendering ─────────────
# Keep in sync with text_cleaner.py
_INVISIBLE_CHARS = [
    '\u200A',  # Hair space
    '\u200B',  # Zero width space
    '\u200C',  # Zero width non-joiner
    '\u200D',  # Zero width joiner
    '\u200E',  # Left-to-right mark
    '\u200F',  # Right-to-left mark
    '\u00AD',  # Soft hyphen
    '\uFEFF',  # BOM / zero width no-break space
    '\uFFFD',  # Unicode replacement character
    '\u2028',  # Line separator
    '\u2029',  # Paragraph separator
    '\u202A',  # Left-to-right embedding
    '\u202B',  # Right-to-left embedding
    '\u202C',  # Pop directional formatting
    '\u202D',  # Left-to-right override
    '\u202E',  # Right-to-left override
]


def _clean_for_tts(text):
    """
    Clean text specifically for TTS input.

    - strips HTML tags
    - removes invisible Unicode characters
    - normalizes whitespace
    """
    clean = re.sub(r'<[^>]+>', '', text)

    for ch in _INVISIBLE_CHARS:
        clean = clean.replace(ch, '')

    # Non-breaking space → regular space
    clean = clean.replace('\u00A0', ' ')

    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def _cleanup_orphaned_audio():
    """
    Delete leftover audio_*.mp3 files in downloads/ from previous crashed sessions.

    Safety:
    - deletes ONLY files matching audio_*.mp3
    - does NOT touch user-facing downloads (your app uses sentence_*.mp3, audio_part_*.mp3, etc.)
    """
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        return

    try:
        for fname in os.listdir(downloads_dir):
            if fname.startswith("audio_") and fname.endswith(".mp3"):
                fpath = os.path.join(downloads_dir, fname)
                try:
                    os.remove(fpath)
                    print("[TTS CLEANUP] Removed orphaned file: " + fname)
                except Exception as e:
                    print("[TTS CLEANUP] Could not remove " + fname + ": " + str(e))
    except Exception as e:
        print("[TTS CLEANUP] Skipped cleanup: " + str(e))


# Run orphan cleanup once when module is imported
_cleanup_orphaned_audio()


def generate_audio(text, lang='en', slow=False):
    """
    Generate MP3 audio file from text.
    Returns file path or None on failure.

    IMPORTANT:
    - On SUCCESS: returns filename and does NOT delete it (caller must delete).
    - On FAILURE: deletes partial/invalid files automatically via finally.
    """
    filename = None

    try:
        os.makedirs("downloads", exist_ok=True)
        filename = "downloads/audio_" + uuid.uuid4().hex + ".mp3"

        clean = _clean_for_tts(text)

        if not clean or len(clean) < 2:
            print("[TTS] Text too short after cleaning: '" + clean + "'")
            return None

        tts = gTTS(text=clean, lang=lang, slow=slow)
        tts.save(filename)

        # Validate output file
        if os.path.exists(filename) and os.path.getsize(filename) > 100:
            return filename

        print("[TTS] File too small or empty after save")
        return None

    except Exception as e:
        print("[TTS ERROR] " + str(e))
        return None

    finally:
        # Only delete on failure/invalid file.
        # Never delete valid files returned to the caller.
        if filename is not None and os.path.exists(filename):
            if os.path.getsize(filename) <= 100:
                try:
                    os.remove(filename)
                    print("[TTS CLEANUP] Removed invalid file: " + filename)
                except Exception:
                    pass