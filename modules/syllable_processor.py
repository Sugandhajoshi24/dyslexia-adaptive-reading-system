import pyphen

dic = pyphen.Pyphen(lang='en')

def syllabify_text(text):
    words = text.split()
    result = []

    for word in words:
        syllable_word = dic.inserted(word)
        result.append(syllable_word)

    return " ".join(result)