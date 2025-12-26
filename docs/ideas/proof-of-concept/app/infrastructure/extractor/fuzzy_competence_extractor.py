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

    def __init__(self, repository, threshold: int = 90):
        self.repository = repository
        self.threshold = threshold
        # Wir laden alle bekannten Labels (ESCO + Fachbücher + Uni) als Referenz
        self.reference_labels = self.repository.get_all_labels()

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        """
        Scannt den Text nach Ähnlichkeiten zu bekannten Kompetenzen.
        """
        found_dtos = []
        # Wir zerlegen den Text in Chunks/N-Gramme oder nutzen eine Keyword-Vorauswahl
        # Hier nutzen wir eine effiziente Suche über die Wortliste
        words = text.split()

        # Um Performance-Probleme zu vermeiden, begrenzen wir die Fuzzy-Suche
        # auf Substantive oder extrahierte Kandidaten (optional via NLP)

        unique_matches = {}

        for word in set(words):
            if len(word) < 5: continue # Zu kurze Wörter ignorieren

            # Suche nach dem ähnlichsten Begriff in der gesamten Wissensbasis
            match = process.extractOne(
                word,
                self.reference_labels,
                scorer=fuzz.WRatio
            )

            if match and match[1] >= self.threshold:
                matched_label = match[0]
                confidence = match[1] / 100.0

                # Holen der Metadaten (URI, Level) aus dem Repository
                data = self.repository.get_data_by_label(matched_label)

                if data:
                    uri = data.get("uri")
                    if uri not in unique_matches: #noch die create comptence dto nutzen
                        unique_matches[uri] = CompetenceDTO(
                            original_term=word,
                            esco_label=data.get("preferredLabel", matched_label),
                            esco_uri=uri,
                            confidence_score=confidence,
                            level=data.get("level", 2), # Bezieht Level 4/5 aus den JSONs
                            is_digital=data.get("is_digital", False),
                            source_domain=data.get("source_domain", "Fuzzy-Match"),
                            role_context=role
                        )

        return list(unique_matches.values())

    def get_extractor_info(self) -> str:
        return f"FuzzyCompetenceExtractor (Threshold: {self.threshold}%)"
