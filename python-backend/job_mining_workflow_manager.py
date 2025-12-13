# job_mining_workflow_manager.py
import hashlib
from typing import BinaryIO, Optional

# VOM VORHERIGEN CODE (MUSS VERFÜGBAR SEIN)
from metadata_extractor import MetadataExtractor # ANNAHME: Enthält extrahierte Metadaten
from organization_extractor import extract_branch # ANNAHME: Enthält die Branchenlogik
from normalize import parse_date # ANNAHME: Enthält die Datums-Normalisierung
# ----------------------------------------------

from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from models import AnalysisResultDTO


class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""

    def __init__(self, text_extractor: ITextExtractor, competence_extractor: ICompetenceExtractor):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        # NEU: Initialisierung des Metadaten-Extraktors
        self.meta_extractor = MetadataExtractor()

    def _run_analysis_from_text(self, raw_text: str, source_name: str) -> AnalysisResultDTO:
        """
        Interne, wiederverwendbare Methode, die Analyse-Schritte durchführt
        und alle DTO-Felder befüllt.
        """

        # 1. Hashing (Mit hashlib für bessere Stabilität/Kollisionssicherheit)
        raw_text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. KOMPETENZ-EXTRAKTION (Nutzt den injizierten SpaCyExtractor)
        competences = self.competence_extractor.extract_competences(raw_text)

        # 3. METADATEN-EXTRAKTION
        # Ruft die umfassende Extraktion auf
        metadata = self.meta_extractor.extract_all(raw_text, filename=source_name)

        # Datums-Parsing und Normalisierung
        # Nutzt den normalize-Helfer, Fallback auf aktuellen Hash-Zeitpunkt, wenn keine Daten gefunden
        iso_date, _, _ = parse_date(raw_text)
        posting_date = iso_date or "2024-12-01"

        # 4. Output
        return AnalysisResultDTO(
            # Befüllt Titel aus Metadaten oder Source-Name
            title=metadata.get('job_title') or source_name,

            # Befüllt Metadaten-Felder
            job_role=metadata.get('job_category') or "Unbekannte Rolle",
            region=metadata.get('location') or "Unbekannt",
            industry=extract_branch(metadata.get('organization', '')), # Extrahiert Branch

            posting_date=posting_date,
            raw_text_hash=raw_text_hash,
            raw_text=raw_text,
            competences=competences
        )

    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        """Extrahiert Text aus einem Dateistream und führt dann die Analyse durch."""

        raw_text = self.text_extractor.extract_text(file_stream, filename)
        cleaned_raw_text = raw_text.replace('\x00', '')

        return self._run_analysis_from_text(cleaned_raw_text, filename)
