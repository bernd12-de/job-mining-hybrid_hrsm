from pydantic import BaseModel
from typing import List, Optional

class CompetenceDTO(BaseModel):
    original_term: str
    confidence_score: float = 0.0
    esco_label: str
    esco_uri: str
    esco_group_code: Optional[str] = None # Für die hierarchische Analyse (Phase 3)

# --- DOMAIN ENTITY WIRD HINZUGEFÜGT ---
class Competence(object):
    """Interne Repräsentation einer Kompetenz, angereichert mit Metadaten."""
    def __init__(self, preferred_label: str, esco_uri: str, synonyms: List[str] = None, group_code: str = None):
        self.preferred_label = preferred_label
        self.esco_uri = esco_uri
        self.group_code = group_code
        self.synonyms = synonyms if synonyms is not None else []
        self.keywords = [self.preferred_label.lower()] + [s.lower() for s in self.synonyms]
# ----------------------------------------

class AnalysisResultDTO(BaseModel):
    title: str
    job_role: str
    region: str
    industry: str
    posting_date: str
    raw_text_hash: str # Für Idempotenz-Prüfung im Kotlin-Backend
    raw_text: str
    competences: List[CompetenceDTO]
