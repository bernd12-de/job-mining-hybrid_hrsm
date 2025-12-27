import hashlib
import uuid
import logging
from typing import List, Dict, Any, Optional
from app.domain.models import AnalysisResultDTO, CompetenceDTO
from app.core.constants import GLOBAL_BLACKLIST

logger = logging.getLogger(__name__)

class AnalysisResultFactory:
    """
    Zentrale Factory zur Erstellung und Validierung von Analyseergebnissen.

    Verantwortlichkeiten:
    - SHA-256 Hashing (Ebene 7): Erzeugt einen eindeutigen Fingerabdruck des Textes.
    - SSoT-Filter: Prüft alle Kompetenzen gegen die globale Blacklist.
    - Daten-Konsistenz: Normalisiert Metadaten und erzwingt Typ-Sicherheit.
    """

    @staticmethod
    def create_result(
            raw_text: str,
            source_name: str,
            detected_role: str,
            detected_industry: str,
            raw_competences: List[Any],
            metadata: Dict[str, Any]
    ) -> AnalysisResultDTO:
        """
        Baut ein konsistentes AnalysisResultDTO.
        """
        # 1. Idempotenz-Check (Hash erzeugen)
        text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. Blacklist-Filterung (SSoT)
        sanitized_skills = []
        seen = set()

        for item in raw_competences:
            # Extrahiere Label (Egal ob String oder Objekt-Dict)
            term = item if isinstance(item, str) else item.get('original_term', '')
            term_clean = term.strip()
            term_lower = term_clean.lower()

            # Filter-Logik
            if term_lower and term_lower not in GLOBAL_BLACKLIST and term_lower not in seen:
                sanitized_skills.append(term_clean)
                seen.add(term_lower)

        # 3. DTO-Zusammenbau (Mapping auf deine Kotlin-Struktur)
        return AnalysisResultDTO(
            job_id=str,
            title=metadata.get('job_title') or source_name,
            detected_role=detected_role,
            detected_industry=detected_industry,
            publication_date=metadata.get('posting_date') or "2024-12-01",
            location=metadata.get('location') or "Unbekannt",
            region=metadata.get('region'),
            raw_text_hash=text_hash,
            raw_text=raw_text[:500] + "...", # Payload-Schonung
            skills=sanitized_skills,          # Die bereinigte Liste
            segmented_text=[]                 # Platzhalter für Ebene 6
        )
