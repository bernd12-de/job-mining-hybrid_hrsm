from typing import BinaryIO, List, Dict, Set
from models import AnalysisResultDTO, CompetenceDTO, Competence # <-- FIX: Importiert Competence aus models.py

# --- ICompetenceRepository WIRD HINZUGEFÜGT ---
class ICompetenceRepository(object):
    """Interface für die Hybrid-Kompetenz-Datenbank (ESCO + Custom)."""
    # Die Implementierung muss alle diese Methoden enthalten
    def get_all_skills(self) -> Set[str]:
        raise NotImplementedError
    def get_esco_only(self) -> Set[str]:
        raise NotImplementedError
    def get_custom_only(self) -> Set[str]:
        raise NotImplementedError
    def get_esco_mapping(self) -> Dict[str, str]:
        raise NotImplementedError
    def get_all_competences(self) -> List[Competence]: # Hinzugefügt für den Extractor
        raise NotImplementedError
# ------------------------------------------------

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
