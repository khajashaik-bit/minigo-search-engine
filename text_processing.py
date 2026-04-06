import re
STOPWORDS={"the","and","is","in","of","to","for","on","that","this","it","as","with","at","a","be"}
def clean_and_tokenize(text: str):
    text=text.lower()
    text=re.sub(r'[^a-z0-9\s]'," ",text)
    words=text.split()
    words=[w for w in words if w not in STOPWORDS]
    return words