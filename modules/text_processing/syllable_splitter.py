import pyphen
import re

dic = pyphen.Pyphen(lang="en")


def syllabify_difficult_words(text, difficult_words):

    words = text.split()
    processed_words = []

    for word in words:

        clean_word = re.sub(r'[^\w\-]', '', word)
        root = clean_word.lower()

        if root in difficult_words:

            syllables = dic.inserted(clean_word)

            word = word.replace(clean_word, syllables)

        processed_words.append(word)

    return " ".join(processed_words)