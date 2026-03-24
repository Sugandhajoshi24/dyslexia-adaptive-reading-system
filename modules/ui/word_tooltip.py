"""
Word Definition Tooltip.

When a difficult word is clicked, shows its definition
using a free dictionary API.
Implemented via JavaScript fetch + CSS tooltip.
"""


def get_tooltip_css(theme_config):
    """
    Return CSS + JavaScript for word definition tooltips.
    Inject this into the page for interactive word definitions.
    """
    t = theme_config

    return f"""
    <style>
    .word-clickable {{
        cursor: pointer;
        position: relative;
        border-bottom: 1px dotted {t.get('accent', '#2196F3')};
    }}
    .word-clickable:hover {{
        opacity: 0.8;
    }}

    .word-tooltip {{
        position: fixed;
        background: {t.get('card', '#f7f7f7')};
        color: {t.get('text', '#1a1a1a')};
        border: 1px solid {t.get('border', '#e0e0e0')};
        border-radius: 12px;
        padding: 14px 18px;
        max-width: 320px;
        font-size: 14px;
        line-height: 1.5;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        z-index: 10000;
        display: none;
        font-family: Arial, sans-serif;
    }}
    .word-tooltip .tt-word {{
        font-weight: 700;
        font-size: 16px;
        color: {t.get('accent', '#2196F3')};
        margin-bottom: 6px;
    }}
    .word-tooltip .tt-pos {{
        font-style: italic;
        opacity: 0.6;
        font-size: 12px;
    }}
    .word-tooltip .tt-def {{
        margin-top: 4px;
    }}
    .word-tooltip .tt-close {{
        position: absolute;
        top: 6px; right: 10px;
        cursor: pointer;
        font-size: 16px;
        opacity: 0.5;
    }}
    .word-tooltip .tt-close:hover {{ opacity: 1; }}
    .word-tooltip .tt-loading {{
        opacity: 0.6;
        font-style: italic;
    }}
    </style>

    <div class="word-tooltip" id="wordTooltip">
        <span class="tt-close" onclick="closeTooltip()">✕</span>
        <div class="tt-word" id="ttWord"></div>
        <div class="tt-pos" id="ttPos"></div>
        <div class="tt-def" id="ttDef"></div>
    </div>

    <script>
    const tooltip = document.getElementById('wordTooltip');

    function closeTooltip() {{
        tooltip.style.display = 'none';
    }}

    document.addEventListener('click', function(e) {{
        if (!tooltip.contains(e.target) && !e.target.classList.contains('word-clickable')) {{
            closeTooltip();
        }}
    }});

    // Make highlighted words clickable
    document.addEventListener('DOMContentLoaded', function() {{
        setTimeout(makeWordsClickable, 500);
    }});

    function makeWordsClickable() {{
        // Find all highlighted spans (difficult words)
        const spans = document.querySelectorAll('[style*="background-color"]');
        spans.forEach(function(span) {{
            span.classList.add('word-clickable');
            span.addEventListener('click', function(e) {{
                e.stopPropagation();
                const word = this.innerText.replace(/[^a-zA-Z-]/g, '').replace(/-/g, '');
                showDefinition(word, e.clientX, e.clientY);
            }});
        }});
    }}

    function showDefinition(word, x, y) {{
        const ttWord = document.getElementById('ttWord');
        const ttPos = document.getElementById('ttPos');
        const ttDef = document.getElementById('ttDef');

        ttWord.innerText = word;
        ttPos.innerText = '';
        ttDef.innerHTML = '<span class="tt-loading">Loading definition...</span>';

        // Position tooltip
        tooltip.style.display = 'block';
        tooltip.style.left = Math.min(x, window.innerWidth - 340) + 'px';
        tooltip.style.top = (y + 20) + 'px';

        // Fetch from free dictionary API
        fetch('https://api.dictionaryapi.dev/api/v2/entries/en/' + word)
            .then(r => r.json())
            .then(data => {{
                if (Array.isArray(data) && data.length > 0) {{
                    const entry = data[0];
                    const meaning = entry.meanings[0];
                    const pos = meaning ? meaning.partOfSpeech : '';
                    const def = meaning && meaning.definitions[0]
                        ? meaning.definitions[0].definition
                        : 'No definition found.';

                    ttPos.innerText = pos;
                    ttDef.innerText = def;
                }} else {{
                    ttDef.innerText = 'Definition not found for this word.';
                }}
            }})
            .catch(() => {{
                ttDef.innerText = 'Could not load definition. Check your internet connection.';
            }});
    }}
    </script>
    """