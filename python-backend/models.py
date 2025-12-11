from pydantic import BaseModel
from typing import List, Optional

class CompetenceDTO(BaseModel):
    original_term: str
    confidence_score: float = 0.0
    esco_label: str
    esco_uri: str
    esco_group_code: Optional[str] = None # Für die hierarchische Analyse (Phase 3)

class AnalysisResultDTO(BaseModel):
    title: str
    job_role: str
    region: str
    industry: str
    posting_date: str
    raw_text_hash: str # Für Idempotenz-Prüfung im Kotlin-Backend
    competences: List[CompetenceDTO]
