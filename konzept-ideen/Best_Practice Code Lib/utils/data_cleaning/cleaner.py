import re, unicodedata
def clean_text(text):
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\wäöüÄÖÜß\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text
