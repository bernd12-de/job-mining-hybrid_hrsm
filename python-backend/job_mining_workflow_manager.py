from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from models import AnalysisResultDTO
from typing import BinaryIO, Optional

class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""

    def __init__(self, text_extractor: ITextExtractor, competence_extractor: ICompetenceExtractor):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor

    def _run_analysis_from_text(self, raw_text: str, source_name: str) -> AnalysisResultDTO:
        """
        Interne, wiederverwendbare Methode, die Analyse-Schritte (Hashing, Extraktion, DTO-Erstellung)
        mit bereits extrahiertem Text durchführt.
        """

        # Generiere Hash vom bereinigten Text für Idempotenz
        raw_text_hash = str(hash(raw_text))

        # 1. Kompetenz-Extraktion (Fuzzy Matching + ESCO Mapping)
        competences = self.competence_extractor.extract_competences(raw_text)

        # 2. Output
        return AnalysisResultDTO(
            # source_name ist entweder Dateiname oder URL
            title=source_name,
            job_role="Placeholder",
            region="Placeholder",
            industry="Placeholder",
            posting_date="2024-12-01",
            raw_text_hash=raw_text_hash,
            raw_text=raw_text,
            competences=competences
        )

    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        """Extrahiert Text aus einem Dateistream und führt dann die Analyse durch."""

        # 1. Parsing (PDF/DOCX)
        raw_text = self.text_extractor.extract_text(file_stream, filename)

        # FIX: Null-Bytes entfernen (PostgreSQL UTF8-Fehler beheben)
        cleaned_raw_text = raw_text.replace('\x00', '')

        # 2. Wiederverwendung der Kern-Analyse
        return self._run_analysis_from_text(cleaned_raw_text, filename)
