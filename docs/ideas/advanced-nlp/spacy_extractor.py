import spacy
from spacy.matcher import PhraseMatcher

# Blacklist gegen "Rauschen"
import spacy
from spacy.matcher import PhraseMatcher
import sys

# Deine Blacklist gegen "sinnfreie" Begriffe
BLACKLIST = {"erfahrung", "kenntnisse", "bereich", "aufgaben", "team", "sowie"}

def run_extraction(text, labels):
    nlp = spacy.load("de_core_news_lg")
    matcher = PhraseMatcher(nlp.vocab)
    # ... Matcher-Setup ...
    doc = nlp(text)
    matches = matcher(doc)

    clean_results = set()
    for match_id, start, end in matches:
        term = doc[start:end].text
        if term.lower() not in BLACKLIST:
            clean_results.add(term)

    # Rückgabe an Kotlin
    for r in clean_results: print(r)

if __name__ == "__main__":
    run_extraction(sys.argv[1], sys.argv[2:])
