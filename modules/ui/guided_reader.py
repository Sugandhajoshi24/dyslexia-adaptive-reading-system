import json
import hashlib
import streamlit as st
import streamlit.components.v1 as components
import os
import base64

from modules.audio.tts_engine import generate_audio


def _stable_text_hash(text):
    """
    Deterministic hash for cache keys.

    Uses hashlib.md5 — matches the same helper in app.py exactly.
    Both files must use identical logic so cache keys are consistent.

    Why not Python's hash():
      - hash() is randomized per Python session since Python 3.3
      - Two runs of the app produce different hash() values for same text
      - hashlib.md5 always produces the same value for the same input
    """
    if not text:
        return "empty"
    return hashlib.md5(
        text[:500].encode("utf-8", errors="ignore")
    ).hexdigest()[:16]


def render_speech_sync(
    display_text,
    tts_text,
    font_family="Arial",
    font_size=20,
    theme="Light",
    line_spacing=1.8,
    letter_spacing=1.0,
    theme_config=None,
    speech_lang="en-US",
    lang_code="en"
):
    """Route to correct guided reader based on language."""
    if theme_config is None:
        theme_config = {
            "bg": "#ffffff", "text": "#1a1a1a", "card": "#f9f9f9",
            "border": "#e0e0e0", "accent": "#2196F3", "badge_text": "#fff"
        }

    if speech_lang.startswith("en"):
        _render_browser_speech(
            display_text, tts_text, font_family, font_size,
            line_spacing, letter_spacing, theme_config, speech_lang
        )
    else:
        _render_gtts_speech(
            display_text, tts_text, font_family, font_size,
            line_spacing, letter_spacing, theme_config, speech_lang,
            lang_code
        )


def _render_gtts_speech(
    display_text, tts_text, font_family, font_size,
    line_spacing, letter_spacing, t, speech_lang,
    lang_code="hi"
):
    """
    gTTS-based guided reader for Hindi and other non-English languages.
    """
    tts_lang = speech_lang.split("-")[0]

    # ── Cache key: language-scoped + stable text hash ──────────
    # Uses _stable_text_hash (hashlib.md5) — NOT Python's hash()
    # Matches the key format in app.py _get_guided_cache_key()
    # Format: guided_audio_<lang>_<hash>
    cache_key = "guided_audio_" + lang_code + "_" + _stable_text_hash(tts_text)

    if cache_key not in st.session_state:
        with st.spinner("🎵 Generating audio for guided reading..."):
            af = generate_audio(tts_text, lang=tts_lang)
            if af and os.path.exists(af):
                try:
                    with open(af, "rb") as f:
                        st.session_state[cache_key] = f.read()
                finally:
                    # Always clean up temp file even if read fails
                    if os.path.exists(af):
                        os.remove(af)
            else:
                st.error("❌ Failed to generate audio. Check your internet connection.")
                return

    if cache_key not in st.session_state:
        st.error("❌ Audio generation failed.")
        return

    audio_bytes = st.session_state[cache_key]
    audio_b64 = base64.b64encode(audio_bytes).decode()

    safe_display = json.dumps(display_text)

    words = tts_text.split()
    word_count = len(words)

    TOTAL_HEIGHT = 700

    css = """
    html, body {
        height: """ + str(TOTAL_HEIGHT) + """px;
        overflow: hidden;
        margin: 0; padding: 0;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        background: """ + t['card'] + """;
        color: """ + t['text'] + """;
        font-family: '""" + font_family + """', Arial, sans-serif;
    }

    #bar {
        flex-shrink: 0;
        background: """ + t['card'] + """;
        border-bottom: 2px solid """ + t['border'] + """;
        padding: 10px 14px 6px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.10);
        z-index: 999;
    }

    .btn {
        padding: 7px 16px; border: none; border-radius: 8px;
        font-size: 13px; font-weight: 700; cursor: pointer;
        transition: all 0.18s;
    }
    .btn:hover { opacity: .85; }
    .btn:disabled { opacity: .35; cursor: not-allowed; }
    #btnStart { background: #4CAF50; color: #fff; }
    #btnPause { background: #FF9800; color: #fff; }
    #btnStop  { background: #f44336; color: #fff; }

    .speed-presets {
        display: flex; gap: 3px; align-items: center;
        margin-left: 4px;
    }
    .speed-btn {
        padding: 3px 8px; border: 1px solid """ + t['border'] + """;
        border-radius: 5px; font-size: 10px; font-weight: 600;
        cursor: pointer; background: transparent; color: """ + t['text'] + """;
        transition: all 0.15s;
    }
    .speed-btn:hover, .speed-btn.active {
        background: """ + t['accent'] + """; color: """ + t['badge_text'] + """;
        border-color: """ + t['accent'] + """;
    }

    #audioPlayer {
        margin-left: 4px;
        height: 30px;
        border-radius: 6px;
    }

    #lblStatus {
        margin-left: auto; font-size: 11px;
        font-style: italic; opacity: .65; white-space: nowrap;
    }

    #progWrap {
        width: 100%; height: 4px;
        background: """ + t['border'] + """; border-radius: 4px;
        margin-top: 5px; flex-basis: 100%;
    }
    #progBar {
        height: 4px; background: """ + t['accent'] + """;
        border-radius: 4px; width: 0%;
        transition: width .3s ease;
    }

    #reader {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 26px 36px;
        font-size: """ + str(font_size) + """px;
        line-height: """ + str(line_spacing) + """;
        letter-spacing: """ + str(letter_spacing) + """px;
        color: """ + t['text'] + """;
        word-spacing: 5px;
        background: """ + t['bg'] + """;
        position: relative;
    }

    .w { display: inline; padding: 1px 2px; border-radius: 3px; transition: background .15s; }
    .w-on { background: #FFD54F !important; color: #111 !important;
             border-radius: 4px; padding: 1px 5px; font-weight: 700; }
    .w-done { opacity: .38; }
    """

    js = """
    var DISPLAY_HTML = """ + safe_display + """;
    var WORD_COUNT = """ + str(word_count) + """;

    var reader = document.getElementById("reader");
    var audio = document.getElementById("audioPlayer");
    var wc = 0;
    var highlightTimer = null;
    var currentRate = 1.0;

    function wrapText(html) {
        return html.replace(/(>|^)([^<]+)(<|$)/g, function(m, b, t, a) {
            var tokens = t.split(/(\\s+)/);
            var r = "";
            for (var i = 0; i < tokens.length; i++) {
                var tok = tokens[i];
                if (/^\\s+$/.test(tok) || tok === "") r += tok;
                else { r += '<span class="w" id="w' + wc + '">' + tok + '</span>'; wc++; }
            }
            return b + r + a;
        });
    }

    reader.innerHTML = wrapText(DISPLAY_HTML);
    var totalSpans = wc;

    function setStatus(m) { document.getElementById("lblStatus").innerText = m; }

    function enableControls(playing) {
        document.getElementById("btnStart").disabled = playing;
        document.getElementById("btnPause").disabled = !playing;
        document.getElementById("btnStop").disabled  = !playing;
    }

    function resetControls() {
        document.getElementById("btnStart").disabled = false;
        document.getElementById("btnPause").disabled = true;
        document.getElementById("btnStop").disabled  = true;
        document.getElementById("btnPause").innerText = "⏸ Pause";
    }

    function clearHighlights() {
        for (var i = 0; i < totalSpans; i++) {
            var el = document.getElementById("w" + i);
            if (el) el.className = "w";
        }
        document.getElementById("progBar").style.width = "0%";
    }

    function scrollToWord(el) {
        var c = document.getElementById("reader");
        var st = el.offsetTop - (c.clientHeight / 2) + (el.offsetHeight / 2);
        c.scrollTo({ top: Math.max(0, st), behavior: "smooth" });
    }

    function highlightWord(idx) {
        if (idx < 0 || idx >= totalSpans) return;
        if (idx > 0) {
            var prev = document.getElementById("w" + (idx - 1));
            if (prev) { prev.classList.remove("w-on"); prev.classList.add("w-done"); }
        }
        var el = document.getElementById("w" + idx);
        if (el) { el.classList.add("w-on"); scrollToWord(el); }
        document.getElementById("progBar").style.width = ((idx / totalSpans) * 100).toFixed(1) + "%";
        setStatus("Word " + (idx + 1) + " / " + totalSpans);
    }

    function startHighlightSync() {
        if (highlightTimer) clearInterval(highlightTimer);

        var duration = audio.duration;
        if (!duration || duration === 0) {
            setStatus("Audio loaded — highlighting by estimate");
            duration = totalSpans * 0.4;
        }

        var msPerWord = (duration * 1000) / totalSpans;
        var wordIdx = 0;

        if (audio.currentTime > 0) {
            wordIdx = Math.floor((audio.currentTime / duration) * totalSpans);
        }

        highlightTimer = setInterval(function() {
            if (audio.paused || audio.ended) return;

            var progress = audio.currentTime / audio.duration;
            wordIdx = Math.floor(progress * totalSpans);

            if (wordIdx < totalSpans) {
                highlightWord(wordIdx);
            }

            if (audio.ended || wordIdx >= totalSpans - 1) {
                clearInterval(highlightTimer);
                highlightTimer = null;
                clearHighlights();
                document.getElementById("progBar").style.width = "100%";
                setStatus("✅ Finished");
                resetControls();
            }
        }, Math.max(50, msPerWord * 0.8));
    }

    audio.addEventListener('ended', function() {
        if (highlightTimer) { clearInterval(highlightTimer); highlightTimer = null; }
        clearHighlights();
        document.getElementById("progBar").style.width = "100%";
        setStatus("✅ Finished");
        resetControls();
    });

    function doStart() {
        clearHighlights();
        audio.currentTime = 0;
        audio.playbackRate = currentRate;
        audio.play().then(function() {
            enableControls(true);
            setStatus("Speaking...");
            highlightWord(0);
            startHighlightSync();
        }).catch(function(e) {
            setStatus("❌ Play failed: " + e.message);
        });
    }

    function doPause() {
        if (audio.paused) {
            audio.play();
            document.getElementById("btnPause").innerText = "⏸ Pause";
            setStatus("Speaking...");
            startHighlightSync();
        } else {
            audio.pause();
            if (highlightTimer) { clearInterval(highlightTimer); highlightTimer = null; }
            document.getElementById("btnPause").innerText = "▶ Resume";
            setStatus("⏸ Paused");
        }
    }

    function doStop() {
        audio.pause();
        audio.currentTime = 0;
        if (highlightTimer) { clearInterval(highlightTimer); highlightTimer = null; }
        clearHighlights();
        resetControls();
        setStatus("Stopped");
    }

    function setSpeed(v, btn) {
        currentRate = v;
        audio.playbackRate = v;
        var all = document.querySelectorAll('.speed-btn');
        all.forEach(function(b) { b.classList.remove('active'); });
        if (btn) btn.classList.add('active');
        setStatus("Speed: " + v.toFixed(1) + "x");
    }
    """

    html_content = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>""" + css + """</style>
</head>
<body>
<div id="bar">
    <button class="btn" id="btnStart" onclick="doStart()">▶ Start</button>
    <button class="btn" id="btnPause" onclick="doPause()" disabled>⏸ Pause</button>
    <button class="btn" id="btnStop"  onclick="doStop()"  disabled>⏹ Stop</button>

    <div class="speed-presets">
        <span style="font-size:10px;opacity:.5;">Speed:</span>
        <button class="speed-btn" onclick="setSpeed(0.5,this)">Very Slow</button>
        <button class="speed-btn" onclick="setSpeed(0.7,this)">Slow</button>
        <button class="speed-btn active" onclick="setSpeed(1.0,this)">Normal</button>
        <button class="speed-btn" onclick="setSpeed(1.3,this)">Fast</button>
        <button class="speed-btn" onclick="setSpeed(1.5,this)">Faster</button>
    </div>

    <span id="lblStatus">Ready — press Start</span>
    <div id="progWrap"><div id="progBar"></div></div>
</div>

<audio id="audioPlayer" src="data:audio/mp3;base64,""" + audio_b64 + """" preload="auto"></audio>

<div id="reader"></div>
<script>""" + js + """</script>
</body>
</html>"""

    components.html(html_content, height=TOTAL_HEIGHT, scrolling=False)


def _render_browser_speech(
    display_text, tts_text, font_family, font_size,
    line_spacing, letter_spacing, t, speech_lang
):
    """
    Browser SpeechSynthesis guided reader — for English only.
    No changes from original — browser speech needs no audio cache.
    """
    safe_tts     = json.dumps(tts_text)
    safe_display = json.dumps(display_text)

    TOTAL_HEIGHT = 700

    css = """
    html, body {
        height: """ + str(TOTAL_HEIGHT) + """px;
        overflow: hidden;
        margin: 0; padding: 0;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        background: """ + t['card'] + """;
        color: """ + t['text'] + """;
        font-family: '""" + font_family + """', Arial, sans-serif;
    }

    #bar {
        flex-shrink: 0;
        background: """ + t['card'] + """;
        border-bottom: 2px solid """ + t['border'] + """;
        padding: 10px 14px 6px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.10);
        z-index: 999;
    }

    .btn {
        padding: 7px 16px; border: none; border-radius: 8px;
        font-size: 13px; font-weight: 700; cursor: pointer;
        transition: all 0.18s;
    }
    .btn:hover { opacity: .85; }
    .btn:disabled { opacity: .35; cursor: not-allowed; }
    #btnStart { background: #4CAF50; color: #fff; }
    #btnPause { background: #FF9800; color: #fff; }
    #btnStop  { background: #f44336; color: #fff; }

    .speed-presets {
        display: flex; gap: 3px; align-items: center;
        margin-left: 4px;
    }
    .speed-btn {
        padding: 3px 8px; border: 1px solid """ + t['border'] + """;
        border-radius: 5px; font-size: 10px; font-weight: 600;
        cursor: pointer; background: transparent; color: """ + t['text'] + """;
        transition: all 0.15s;
    }
    .speed-btn:hover, .speed-btn.active {
        background: """ + t['accent'] + """; color: """ + t['badge_text'] + """;
        border-color: """ + t['accent'] + """;
    }

    #lblStatus {
        margin-left: auto; font-size: 11px;
        font-style: italic; opacity: .65; white-space: nowrap;
    }

    #progWrap {
        width: 100%; height: 4px;
        background: """ + t['border'] + """; border-radius: 4px;
        margin-top: 5px; flex-basis: 100%;
    }
    #progBar {
        height: 4px; background: """ + t['accent'] + """;
        border-radius: 4px; width: 0%;
        transition: width .22s ease;
    }

    #reader {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 26px 36px;
        font-size: """ + str(font_size) + """px;
        line-height: """ + str(line_spacing) + """;
        letter-spacing: """ + str(letter_spacing) + """px;
        color: """ + t['text'] + """;
        word-spacing: 5px;
        background: """ + t['bg'] + """;
        position: relative;
    }

    .w { display: inline; padding: 1px 2px; border-radius: 3px; transition: background .1s; }
    .w-on { background: #FFD54F !important; color: #111 !important;
             border-radius: 4px; padding: 1px 5px; font-weight: 700; }
    .w-done { opacity: .38; }
    """

    js = """
    speechSynthesis.cancel();

    var SPEECH_LANG = '""" + speech_lang + """';
    var TTS_TEXT     = """ + safe_tts + """;
    var DISPLAY_HTML = """ + safe_display + """;

    var words = TTS_TEXT.split(/\\s+/).filter(function(w) { return w.length > 0; });
    var N     = words.length;

    var charStarts = [];
    var cp = 0;
    for (var ci = 0; ci < N; ci++) {
        var found = TTS_TEXT.indexOf(words[ci], cp);
        charStarts.push(found >= 0 ? found : cp);
        cp = (found >= 0 ? found : cp) + words[ci].length + 1;
    }

    var reader = document.getElementById("reader");
    var wc = 0;

    function wrapText(html) {
        return html.replace(/(>|^)([^<]+)(<|$)/g, function(m, b, t, a) {
            var tokens = t.split(/(\\s+)/);
            var r = "";
            for (var i = 0; i < tokens.length; i++) {
                var tok = tokens[i];
                if (/^\\s+$/.test(tok) || tok === "") r += tok;
                else { r += '<span class="w" id="w' + wc + '">' + tok + '</span>'; wc++; }
            }
            return b + r + a;
        });
    }

    reader.innerHTML = wrapText(DISPLAY_HTML);

    var utt = null;
    var paused = false;
    var rate = 0.9;
    var curIdx = -1;
    var isSpeaking = false;

    function setStatus(m) { document.getElementById("lblStatus").innerText = m; }

    function enableControls(speaking) {
        document.getElementById("btnStart").disabled = speaking;
        document.getElementById("btnPause").disabled = !speaking;
        document.getElementById("btnStop").disabled  = !speaking;
    }

    function resetControls() {
        document.getElementById("btnStart").disabled = false;
        document.getElementById("btnPause").disabled = true;
        document.getElementById("btnStop").disabled  = true;
        document.getElementById("btnPause").innerText = "⏸ Pause";
        isSpeaking = false;
        paused = false;
    }

    function clearHighlights() {
        for (var i = 0; i < N; i++) {
            var el = document.getElementById("w" + i);
            if (el) el.className = "w";
        }
        document.getElementById("progBar").style.width = "0%";
        curIdx = -1;
    }

    function scrollToWord(el) {
        var c = document.getElementById("reader");
        var st = el.offsetTop - (c.clientHeight / 2) + (el.offsetHeight / 2);
        c.scrollTo({ top: Math.max(0, st), behavior: "smooth" });
    }

    function highlight(idx) {
        if (idx < 0 || idx >= N) return;
        if (curIdx >= 0 && curIdx < N) {
            var p = document.getElementById("w" + curIdx);
            if (p) { p.classList.remove("w-on"); p.classList.add("w-done"); }
        }
        var el = document.getElementById("w" + idx);
        if (el) { el.classList.add("w-on"); scrollToWord(el); }
        curIdx = idx;
        document.getElementById("progBar").style.width = ((idx/N)*100).toFixed(1) + "%";
        setStatus("Word " + (idx+1) + " / " + N);
    }

    function charToWord(c) {
        var lo = 0, hi = N-1, best = 0;
        while (lo <= hi) {
            var mid = (lo+hi) >> 1;
            if (charStarts[mid] <= c) { best = mid; lo = mid+1; }
            else hi = mid-1;
        }
        return best;
    }

    function createAndSpeak() {
        utt = new SpeechSynthesisUtterance(TTS_TEXT);
        utt.rate = rate;
        utt.lang = SPEECH_LANG;

        utt.onstart = function() {
            highlight(0);
        };

        utt.onboundary = function(e) {
            if (e.name !== "word") return;
            var idx = charToWord(e.charIndex);
            if (idx !== curIdx) { highlight(idx); }
        };

        utt.onend = function() {
            clearHighlights();
            document.getElementById("progBar").style.width = "100%";
            setStatus("✅ Finished");
            resetControls();
        };

        utt.onerror = function(e) {
            setStatus("❌ Error: " + e.error);
            resetControls();
        };

        speechSynthesis.speak(utt);
        isSpeaking = true;
    }

    function doStart() {
        speechSynthesis.cancel();
        setTimeout(function() {
            clearHighlights();
            paused = false;
            document.getElementById("btnPause").innerText = "⏸ Pause";
            enableControls(true);
            setStatus("Speaking...");
            createAndSpeak();
        }, 150);
    }

    function doPause() {
        if (!isSpeaking) return;
        if (!paused) {
            speechSynthesis.pause();
            paused = true;
            document.getElementById("btnPause").innerText = "▶ Resume";
            setStatus("⏸ Paused at word " + (curIdx+1));
        } else {
            speechSynthesis.resume();
            paused = false;
            document.getElementById("btnPause").innerText = "⏸ Pause";
            setStatus("Speaking...");
        }
    }

    function doStop() {
        speechSynthesis.cancel();
        clearHighlights();
        resetControls();
        setStatus("Stopped");
    }

    function setSpeed(v, btn) {
        rate = v;
        var all = document.querySelectorAll('.speed-btn');
        all.forEach(function(b) { b.classList.remove('active'); });
        if (btn) btn.classList.add('active');

        if (isSpeaking && !paused) {
            speechSynthesis.cancel();
            setTimeout(function() {
                clearHighlights();
                paused = false;
                document.getElementById("btnPause").innerText = "⏸ Pause";
                enableControls(true);
                setStatus("Speaking at " + rate.toFixed(1) + "x...");
                createAndSpeak();
            }, 150);
        } else {
            setStatus("Speed: " + rate.toFixed(1) + "x");
        }
    }

    window.addEventListener('beforeunload', function() {
        speechSynthesis.cancel();
    });
    """

    html_content = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>""" + css + """</style>
</head>
<body>
<div id="bar">
    <button class="btn" id="btnStart" onclick="doStart()">▶ Start</button>
    <button class="btn" id="btnPause" onclick="doPause()" disabled>⏸ Pause</button>
    <button class="btn" id="btnStop"  onclick="doStop()"  disabled>⏹ Stop</button>

    <div class="speed-presets">
        <span style="font-size:10px;opacity:.5;">Speed:</span>
        <button class="speed-btn" onclick="setSpeed(0.5,this)">Very Slow</button>
        <button class="speed-btn" onclick="setSpeed(0.7,this)">Slow</button>
        <button class="speed-btn active" onclick="setSpeed(0.9,this)">Normal</button>
        <button class="speed-btn" onclick="setSpeed(1.1,this)">Fast</button>
        <button class="speed-btn" onclick="setSpeed(1.3,this)">Faster</button>
    </div>

    <span id="lblStatus">Ready</span>
    <div id="progWrap"><div id="progBar"></div></div>
</div>
<div id="reader"></div>
<script>""" + js + """</script>
</body>
</html>"""

    components.html(html_content, height=TOTAL_HEIGHT, scrolling=False)