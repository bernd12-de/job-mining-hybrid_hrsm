import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Any

from spacy.util import is_package

from app.domain.models import CompetenceDTO


class SpaCyCompetenceExtractor:
    def __init__(self, repository, manager, nlp_model=None):
        MODEL_NAME = "de_core_news_md"

        # Sicherheits-Check mit automatischem Install-Versuch
        if nlp_model is None:
            if not is_package(MODEL_NAME):
                print(f"⚠️ spaCy-Modell '{MODEL_NAME}' fehlt. Starte automatischen Download...")
                try:
                    spacy.cli.download(MODEL_NAME)
                    print(f"✅ Modell '{MODEL_NAME}' erfolgreich installiert.")
                except Exception as e:
                    print(f"❌ Automatischer Download von '{MODEL_NAME}' fehlgeschlagen: {e}")
                    print(f"⚠️ FALLBACK: Verwende leeres SpaCy-Modell (NLP-Features deaktiviert)")
                    print(f"💡 Zum Aktivieren später ausführen: python -m spacy download {MODEL_NAME}")
                    # Erstelle ein leeres deutsches Modell als Fallback
                    self.nlp = spacy.blank("de")
                    self.repository = repository
                    self.manager = manager
                    self.matcher = None  # Kein Matcher ohne Modell
                    return

            # Modell laden
            try:
                self.nlp = spacy.load(MODEL_NAME)
            except Exception as e:
                print(f"❌ Fehler beim Laden von '{MODEL_NAME}': {e}")
                print(f"⚠️ FALLBACK: Verwende leeres SpaCy-Modell (NLP-Features deaktiviert)")
                self.nlp = spacy.blank("de")
                self.repository = repository
                self.manager = manager
                self.matcher = None
                return
        else:
            self.nlp = nlp_model
            print("modell könnte leer sein")

        self.repository = repository

        self.manager = manager
        # FIX: Wir rufen eine Methode auf, die uns ALLE Labels gibt,
        # egal ob sie 'custom_domains' oder 'fachbuch_skills' heißen.
        labels = self.repository.get_all_identifiable_labels()
        #self.nlp = nlp_model or spacy.load("de_core_news_md")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # SSoT Patterns (Ebene 2, 4, 5)
        #labels = list(self.repository.esco_data.keys()) + list(self.repository.custom_domains.keys())
        if labels:
           patterns = list(self.nlp.pipe(labels))
           self.matcher.add("KNOWLEDGE_BASE", patterns)

    def extract_competences(self, text_or_doc: str, role: str) -> List[CompetenceDTO]: #kein Any Rückgabe
        # Fallback wenn kein Matcher verfügbar
        if self.matcher is None:
            print("⚠️ SpaCy-Matcher nicht verfügbar (Modell fehlt) - Keine Kompetenzen extrahiert")
            return []

        #doc = self.nlp(text)
        doc = text_or_doc if isinstance(text_or_doc, spacy.tokens.Doc) else self.nlp(text_or_doc)
        # ... restlicher Code bleibt gleich
        matches = self.matcher(doc)
        results = []
        seen = set()
        print("extract_comptence in spacy")
        for _, start, end in matches:
            term = doc[start:end].text
            if term.lower() in seen: continue
            seen.add(term.lower())

            # Delegation an zentrale Factory
            dto = self.manager.create_competence_dto(
                original_term=term,
                esco_label=term, # Normalisierung via Factory/Repo
                esco_uri=f"custom/{term.lower()}",
                level=self.repository.get_level(term),
                is_digital=self.repository.is_digital_skill(term),
                role_context=role
            )
            if dto: results.append(dto)
        return results
