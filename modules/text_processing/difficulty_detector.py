import pyphen
import re

dic = pyphen.Pyphen(lang="en")


def detect_difficult_words(text):

    words = re.findall(r'\b[a-zA-Z]+\b', text)

    difficult_words = set()

    for word in words:

        syllables = dic.inserted(word).split("-")

        if len(word) >= 9 or len(syllables) >= 3:
            difficult_words.add(word.lower())

    return difficult_words



def highlight_difficult_words(text, difficult_words):

    words = text.split()

    highlighted_words = []

    for word in words:

        # remove punctuation
        clean_word = re.sub(r'[^\w\-]', '', word)

        # remove syllable hyphens for matching
        root_word = clean_word.replace("-", "").lower()

        if root_word in difficult_words:

            highlighted_words.append(
                f"<span style='background-color:rgba(255,180,180,0.35)'>{word}</span>"
            )

        else:
            highlighted_words.append(word)

    return " ".join(highlighted_words)