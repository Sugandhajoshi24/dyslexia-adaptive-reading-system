"""
Reading Ruler — follows mouse cursor to help track current line.
Uses components.html for proper JS support in Streamlit.
"""

import streamlit.components.v1 as components


def inject_reading_ruler(theme_config):
    """
    Inject a reading ruler overlay using components.html.
    This ensures JavaScript works properly in Streamlit.
    """
    t = theme_config
    accent = t.get('accent', '#2196F3')

    html = f"""
    <div id="rulerOverlay" style="
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        pointer-events: none;
        z-index: 9998;
    ">
        <div id="rulerBar" style="
            position: absolute;
            left: 0;
            width: 100%;
            height: 40px;
            background: linear-gradient(
                to bottom,
                transparent 0%,
                rgba(128,128,128,0.08) 15%,
                rgba(128,128,128,0.08) 85%,
                transparent 100%
            );
            border-top: 2px solid {accent};
            border-bottom: 2px solid {accent};
            opacity: 0.7;
            display: none;
            pointer-events: none;
        "></div>
    </div>

    <script>
    // Ruler follows mouse in the PARENT window (Streamlit page)
    var bar = document.getElementById('rulerBar');

    // Listen on parent window for mouse events
    try {{
        window.parent.document.addEventListener('mousemove', function(e) {{
            if (bar) {{
                bar.style.display = 'block';
                bar.style.top = (e.clientY - 20) + 'px';
            }}
        }});
        window.parent.document.addEventListener('mouseleave', function() {{
            if (bar) bar.style.display = 'none';
        }});
    }} catch(err) {{
        // Fallback: listen on own document
        document.addEventListener('mousemove', function(e) {{
            if (bar) {{
                bar.style.display = 'block';
                bar.style.top = (e.clientY - 20) + 'px';
            }}
        }});
    }}
    </script>
    """

    components.html(html, height=0, scrolling=False)