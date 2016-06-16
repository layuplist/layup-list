import re


def clean_text_to_raw_words(text):
    if text:
        return " ".join([
            w for w in re.sub("[^a-zA-Z ]", "", text).lower().split()
            if len(w) > 3])
    else:
        return ""
