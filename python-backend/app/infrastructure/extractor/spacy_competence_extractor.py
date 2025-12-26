import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Optional
from spacy.util import is_package
from app.domain.models import CompetenceDTO
# NEU: Importiere die Factory statt den Manager
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.interfaces.interfaces import ICompetenceExtractor

class SpaCyCompetenceExtractor(ICompetenceExtractor):

    def __init__(self, repository, nlp_model=None):
        # KEIN self.manager mehr!
        MODEL_NAME = "de_core_news_md"

        if nlp_model:
            self.nlp = nlp_model
        else:
            if not is_package(MODEL_NAME):
                spacy.cli.download(MODEL_NAME)
            self.nlp = spacy.load(MODEL_NAME)

        self.repository = repository
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Patterns aus dem Repository laden (SSoT)
        labels = self.repository.get_all_identifiable_labels()
        if labels:
            # Beschleunigung: pipe() für viele Patterns
            patterns = list(self.nlp.tokenizer.pipe(labels))
            self.matcher.add("KNOWLEDGE_BASE", patterns)
            print(f"✅ spaCy Extractor geladen mit {len(labels)} Begriffen.")
        else:
            print("⚠️ spaCy Extractor Warnung: Repository ist leer!")

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        if not text: return []

        doc = self.nlp(text[:100000]) # Limit protection
        matches = self.matcher(doc)
        results = []
        seen = set()

        for _, start, end in matches:
            term = doc[start:end].text
            term_lower = term.lower()

            if term_lower in seen: continue
            seen.add(term_lower)

            # NEU: Aufruf der Factory (Statisch) - Kein Manager nötig
            dto = AnalysisResultFactory.create_competence(
                original_term=term,
                esco_label=term, # Ggf. Mapping via Repo nutzen wenn vorhanden
                esco_uri=f"custom/{term_lower}", # Placeholder
                level=self.repository.get_level(term),
                is_digital=self.repository.is_digital_skill(term),
                role_context=role
            )
            results.append(dto)

        return results
