import re
from string import punctuation

import contractions
import pandas as pd
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

LABELS = dict(zip(range(3), ["negative", "neutral", "positive"]))

stop = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

pats = [re.compile("<.*?>")]


def create_input_data(title: str, text: str) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "review_title_cleaned": title,
                "review_text_cleaned": text,
                "title_length": 0,
                "text_length": 0,
                "num_special_chars": 0,
            }
        ]
    )
    df["review_text_cleaned"] = df["review_title_cleaned"].map(clean_text)
    df["review_title_cleaned"] = df["review_text_cleaned"].map(clean_text)

    df["num_special_chars"] = df["review_text_cleaned"].apply(get_punct_count)

    df["review_text_cleaned"] = df["review_text_cleaned"].map(
        lambda text: clean_text(text, remove_stopwords_only=True)
    )
    df["review_title_cleaned"] = df["review_title_cleaned"].map(
        lambda text: clean_text(text, remove_stopwords_only=True)
    )

    df["title_length"] = df["review_title_cleaned"].apply(
        lambda title: len(title.split())
    )
    df["text_length"] = df["review_text_cleaned"].apply(lambda text: len(text.split()))

    return df


def get_punct_count(text):
    return len(re.findall(rf"[{punctuation}]", text))


def clean_text(text: str, remove_stopwords_only: bool = False) -> str:
    if not remove_stopwords_only:
        text = str(contractions.fix(text))
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        for pat in pats:
            text = re.sub(pat, "", text)
        words = [
            lemmatizer.lemmatize(i, j[0].lower())
            if j[0].lower() in ["a", "n", "v"]
            else lemmatizer.lemmatize(i)
            for i, j in pos_tag(word_tokenize(text))
        ]
        text = " ".join(words)

    if remove_stopwords_only:
        text = text.translate(str.maketrans("", "", punctuation))
        words = [
            word
            for word in word_tokenize(text)
            if (word.lower() not in stop or word.lower() in {"go", "do", "no", "not"})
        ]

    return text
