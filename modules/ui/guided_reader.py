import json
import streamlit.components.v1 as components


def render_speech_sync(
    display_text,
    tts_text,
    font_family="Arial",
    font_size=20,
    theme="Light",
    line_spacing=1.8,
    letter_spacing=1.0,
    theme_config=None,
    speech_lang="en-US"
):
    if theme_config is None:
        theme_config = {
            "bg": "#ffffff", "text": "#1a1a1a", "card": "#f9f9f9",
            "border": "#e0e0e0", "accent": "#2196F3", "badge_text": "#fff"
        }
    t = theme_config

    safe_tts     = json.dumps(tts_text)
    safe_display = json.dumps(display_text)

    TOTAL_HEIGHT = 700

    html = _build_html(
        safe_tts, safe_display, t, font_family, font_size,
        line_spacing, letter_spacing, TOTAL_HEIGHT, speech_lang
    )

    components.html(html, height=TOTAL_HEIGHT, scrolling=False)


def _build_html(safe_tts, safe_display, t, font_family, font_size,
                line_spacing, letter_spacing, total_height, speech_lang):

    css = """
    html, body {
        height: """ + str(total_height) + """px;
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
    var curIdx = 0;
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
        curIdx = 0;
    }

    function scrollToWord(el) {
        var c = document.getElementById("reader");
        var st = el.offsetTop - (c.clientHeight / 2) + (el.offsetHeight / 2);
        c.scrollTo({ top: Math.max(0, st), behavior: "smooth" });
    }

    function highlight(idx) {
        if (idx < 0 || idx >= N) return;
        if (idx > 0) {
            var p = document.getElementById("w" + (idx-1));
            if (p) { p.classList.remove("w-on"); p.classList.add("w-done"); }
        }
        var el = document.getElementById("w" + idx);
        if (el) { el.classList.add("w-on"); scrollToWord(el); }
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

        utt.onboundary = function(e) {
            if (e.name !== "word") return;
            var idx = charToWord(e.charIndex);
            if (idx !== curIdx) { curIdx = idx; highlight(idx); }
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

    html = """<!DOCTYPE html>
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

    return html