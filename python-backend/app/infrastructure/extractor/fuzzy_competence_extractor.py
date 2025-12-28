# app/infrastructure/extractor/fuzzy_competence_extractor.py

import logging
from typing import List, Dict
from rapidfuzz import process, fuzz
from app.interfaces.interfaces import ICompetenceExtractor
from app.domain.models import CompetenceDTO

logger = logging.getLogger(__name__)

class FuzzyCompetenceExtractor(ICompetenceExtractor):
    """
    Pass 2 der Pipeline: Fängt Begriffe ab, die durch exaktes Matching
    verpasst wurden (Fuzzy Matching & Mapping-Tabellen).
    """

    def __init__(self, repository, threshold: int = 82):  # ✅ Industrie-Standard
        self.repository = repository
        self.threshold = threshold
        # Wir laden alle bekannten Labels (ESCO + Fachbücher + Uni) als Referenz
        self.reference_labels = self.repository.get_all_labels()

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        """
        Scannt den Text nach Ähnlichkeiten zu bekannten Kompetenzen.
        PERFORMANCE-OPTIMIERT: Text/Wort/Label-Limits + schnellerer Scorer
        """
        found_dtos = []
        
        # ✅ FIX 1: Text-Limit (verhindert Freeze bei großen PDFs)
        limited_text = text[:10000] if len(text) > 10000 else text
        words = limited_text.split()

        # ✅ FIX 2: Wort-Limit (max 500 unique words für Fuzzy-Matching)
        unique_words = list(set(words))[:500]
        
        # ✅ FIX 3: Label-Limit (nur erste 5000 Labels, sortiert nach Wichtigkeit)
        limited_labels = self.reference_labels[:5000]

        unique_matches = {}

        for word in unique_words:
            # ✅ FIX 4: Minimale Wortlänge von 2 (statt 5) - erlaubt "R", "C", "Go"
            if len(word) < 2: continue

            # ✅ FIX 5: Schnellerer Scorer (ratio statt WRatio)
            match = process.extractOne(
                word,
                limited_labels,
                scorer=fuzz.ratio
            )

            if match and match[1] >= self.threshold:
                matched_label = match[0]
                confidence = match[1] / 100.0

                # Holen der Metadaten (URI, Level) aus dem Repository
                data = self.repository.get_data_by_label(matched_label)

                if data:
                    uri = data.get("uri")
                    if uri not in unique_matches: #noch die create comptence dto nutzen
                        # is_digital Default-Schutz: Nutze False statt None
                        is_digital_value = data.get("is_digital") or False
                        unique_matches[uri] = CompetenceDTO(
                            original_term=word,
                            esco_label=data.get("preferredLabel", matched_label),
                            esco_uri=uri,
                            confidence_score=confidence,
                            level=data.get("level", 2), # Bezieht Level 4/5 aus den JSONs
                            is_digital=is_digital_value,
                            source_domain=data.get("source_domain", "Fuzzy-Match"),
                            role_context=role
                        )

        return list(unique_matches.values())

    def get_extractor_info(self) -> str:
        return f"FuzzyCompetenceExtractor (Threshold: {self.threshold}%)"
