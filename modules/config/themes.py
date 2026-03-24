"""
Complete theme definitions for the Dyslexia Adaptive Reader.
Replaces the simple 2-color system in theme_manager.py
with a full token-based theme system.
"""

THEMES = {
    "Light": {
        "bg": "#ffffff",
        "text": "#1a1a1a",
        "card": "#f7f7f7",
        "border": "#e0e0e0",
        "accent": "#2196F3",
        "muted": "rgba(0,0,0,0.38)",
        "active_sent": "#e8f4fd",
        "badge_bg": "#2196F3",
        "badge_text": "#fff",
        "panel_shadow": "0 4px 24px rgba(0,0,0,0.08)",
        "prog_text": "#1a1a1a",
        "prog_bg": "#f7f7f7",
    },
    "Sepia": {
        "bg": "#f5efe0",
        "text": "#3e2f1c",
        "card": "#fdf6e3",
        "border": "#d4b896",
        "accent": "#8B5E3C",
        "muted": "rgba(62,47,28,0.4)",
        "active_sent": "#f0e6cc",
        "badge_bg": "#8B5E3C",
        "badge_text": "#fff",
        "panel_shadow": "0 4px 24px rgba(100,60,20,0.10)",
        "prog_text": "#3e2f1c",
        "prog_bg": "#fdf6e3",
    },
    "Dark": {
        "bg": "#0f0f1a",
        "text": "#e0e0e0",
        "card": "#1a1a2e",
        "border": "#2a2a4a",
        "accent": "#4fc3f7",
        "muted": "rgba(224,224,224,0.32)",
        "active_sent": "#1a2a3a",
        "badge_bg": "#4fc3f7",
        "badge_text": "#000",
        "panel_shadow": "0 4px 24px rgba(0,0,0,0.40)",
        "prog_text": "#e0e0e0",
        "prog_bg": "#1a1a2e",
    },
    "High Contrast": {
        "bg": "#000000",
        "text": "#ffffff",
        "card": "#111111",
        "border": "#ffffff",
        "accent": "#ffff00",
        "muted": "rgba(255,255,255,0.38)",
        "active_sent": "#1a1a00",
        "badge_bg": "#ffff00",
        "badge_text": "#000",
        "panel_shadow": "0 4px 24px rgba(255,255,255,0.08)",
        "prog_text": "#ffffff",
        "prog_bg": "#111111",
    },
}


def get_theme_config(name):
    """Return full theme dict by name. Defaults to Light."""
    return THEMES.get(name, THEMES["Light"])


def get_theme_names():
    """Return list of available theme names."""
    return list(THEMES.keys())