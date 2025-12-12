from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from models import AnalysisResultDTO
from typing import BinaryIO

class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""

    # Dependency Injection der Service-Schnittstellen (DI-Prinzip)
    def __init__(self, text_extractor: ITextExtractor, competence_extractor: ICompetenceExtractor):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor

    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        # 1. Parsing (PDF/DOCX)
        raw_text = self.text_extractor.extract_text(file_stream, filename)

        # Generiere Hash
        raw_text_hash = str(hash(raw_text))

        # 2. Metadaten-Extraktion (TO DO: Rolle, Region, Datum)

        # 3. Kompetenz-Extraktion (Fuzzy Matching + ESCO Mapping)
        competences = self.competence_extractor.extract_competences(raw_text)

        # 4. Output
        return AnalysisResultDTO(
            title=filename,
            job_role="Placeholder",
            region="Placeholder",
            industry="Placeholder",
            posting_date="2024-12-01",
            raw_text_hash=raw_text_hash,
            raw_text=raw_text, # <--- WICHTIG: MUSS HIER ZURÜCKGEGEBEN WERDEN
            competences=competences
        )
