from typing import BinaryIO, List
from models import AnalysisResultDTO, CompetenceDTO

class ITextExtractor(object):
    """Interface für die Dokumentenverarbeitung (PDF, DOCX)."""
    def extract_text(self, file_stream: BinaryIO, filename: str) -> str:
        raise NotImplementedError

class ICompetenceExtractor(object):
    """Interface für die NLP-gestützte Kompetenzextraktion."""
    def extract_competences(self, text: str) -> List[CompetenceDTO]:
        raise NotImplementedError

class IJobMiningWorkflowManager(object):
    """Interface zur Steuerung der gesamten Analyse-Pipeline."""
    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        raise NotImplementedError
