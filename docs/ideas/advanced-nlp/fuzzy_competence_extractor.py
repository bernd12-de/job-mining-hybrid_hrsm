from interfaces import ICompetenceExtractor
from models import CompetenceDTO
from typing import List
from repositories.hybrid_competence_repository import HybridCompetenceRepository, Competence
from typing import List, Dict, Optional
import spacy
# from sklearn.feature_extraction.text import TfidfVectorizer # Später für komplexere Matches
# from fuzzywuzzy import fuzz # Später für Fuzzy Matching

class FuzzyCompetenceExtractor(ICompetenceExtractor):
    """
    Implementierung des ICompetenceExtractor.
    Führt das Keyword-Matching gegen die Hybrid ESCO-Datenbank durch.
    """

    def __init__(self, repository: HybridCompetenceRepository):
        self.repository = repository
        # Vorbereitung der Keywords für schnelle Suche (flache Map)
        self.keyword_map = self._build_keyword_map()

        # Optionale NLP-Initialisierung für Lemmatisierung in Phase 3
        # try:
        #     self.nlp = spacy.load("de_core_news_sm")
        # except:
        #     print("⚠️ Spacy-Modell nicht gefunden. Nur reines Keyword-Matching.")
        self.nlp = None

    def _build_keyword_map(self) -> Dict[str, Competence]:
        """Erstellt eine Map aller Keywords (Preferred Label + Synonyms) zur schnellen Suche."""
        keyword_map = {}
        for comp in self.repository.get_all_competences():
            for keyword in comp.keywords:
                keyword_map[keyword] = comp
        return keyword_map

    def extract_competences(self, text: str) -> List[CompetenceDTO]:
        """Führt das Matching durch und gibt die DTOs zurück."""
        text_lower = text.lower()
        found_competences: Dict[str, Competence] = {}

        # 1. Direktes Keyword-Matching (MVP-Logik)
        for keyword, competence in self.keyword_map.items():
            if keyword in text_lower:
                # Nutze die ESCO URI als eindeutigen Schlüssel, um Duplikate zu vermeiden
                found_competences[competence.esco_uri] = competence

        # 2. Mappen auf das externe DTO-Format
        result_dtos: List[CompetenceDTO] = []
        for competence in found_competences.values():
            result_dtos.append(CompetenceDTO(
                original_term=competence.preferred_label, # Vereinfacht, sollte später der gefundene Term sein
                confidence_score=1.0, # Direktes Match hat 100% Konfidenz
                esco_label=competence.preferred_label,
                esco_uri=competence.esco_uri,
                esco_group_code=competence.group_code
            ))

        return result_dtos
