# services/splitter.py
from nltk.tokenize import sent_tokenize


def split_into_sentences(text: str) -> list[str]:
    sentences = sent_tokenize(text)
    # loại bỏ câu rỗng / toàn khoảng trắng
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences
