from typing import BinaryIO, List, Dict, Set, Optional
from app.domain.models import AnalysisResultDTO, CompetenceDTO

class ICompetenceRepository(object):
    """Interface für die Hybrid-Kompetenz-Datenbank (ESCO + Fachbücher)."""
    def get_all_skills(self) -> Set[str]:
        raise NotImplementedError
    def get_esco_only(self) -> Set[str]:
        raise NotImplementedError
    def get_custom_only(self) -> Set[str]:
        raise NotImplementedError
    def get_esco_mapping(self) -> Dict[str, str]:
        raise NotImplementedError
    def get_all_competences(self) -> List[CompetenceDTO]:
        raise NotImplementedError
    # NEU für Ebene 3 & 4:
    def is_digital_skill(self, term: str) -> bool:
        raise NotImplementedError
    def get_fachbuch_labels(self) -> Set[str]:
        raise NotImplementedError

class ITextExtractor(object):
    """Interface für die Dokumentenverarbeitung (PDF, DOCX)."""
    def extract_text(self, file_stream: BinaryIO, filename: str) -> str:
        raise NotImplementedError

class ICompetenceExtractor(object):
    """Interface für die NLP-gestützte Kompetenzextraktion."""
    # FIX: Erlaubt die Übergabe der Rolle für den wissenschaftlichen Kontext
    def extract_competences(self, text: str, role: Optional[str] = None) -> List[CompetenceDTO]:
        raise NotImplementedError

class IJobMiningWorkflowManager(object):
    """Interface zur Steuerung der gesamten Analyse-Pipeline."""
    async def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        raise NotImplementedError

    def run_analysis_from_scraped_text(self, cleaned_text: str, source_name: str) -> AnalysisResultDTO:
        raise NotImplementedError
