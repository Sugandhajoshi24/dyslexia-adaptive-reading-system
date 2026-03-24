def get_theme(theme):

    if theme == "Sepia":
        return "#f4ecd8", "#5b4636"

    elif theme == "Dark":
        return "#1e1e1e", "#ffffff"

    elif theme == "High Contrast":
        return "#000000", "#ffff00"

    else:
        return "transparent", "inherit"