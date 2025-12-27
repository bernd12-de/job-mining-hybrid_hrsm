from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import hashlib

class CompetenceDTO(BaseModel):
    # Die ID der Kompetenz wird in der Regel von der DB vergeben,
    # kann aber für Updates hier optional sein.
    id: Optional[int] = None

    original_term: str
    esco_label: Optional[str] = None
    esco_uri: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)

    # Ebene 1-5: Erzwingt Integer-Werte für Hibernate/Kotlin
    level: int = Field(default=2, ge=1, le=5)

    is_digital: bool = False      # Ebene 3
    is_discovery: bool = False    # Ebene 1
    source_domain: Optional[str] = "System"
    role_context: Optional[str] = None

    @field_validator('level', mode='before')
    @classmethod
    def transform_level(cls, v):
        """Korrigiert 'Ebene 4' zu 4, um Kotlin-Konstruktor-Fehler zu vermeiden."""
        if isinstance(v, str):
            import re
            digits = re.findall(r'\d+', v)
            return int(digits[0]) if digits else 2
        return v

class AnalysisResultDTO(BaseModel):
    # 🚨 ANPASSUNG 1: job_id als Optional[int] für BIGSERIAL Kompatibilität
    # Wir setzen es auf None, damit die DB die ID generiert.
    job_id: Optional[int] = None

    title: str
    job_role: str
    region: str
    industry: str
    posting_date: str
    raw_text: str
    raw_text_hash: str # SHA-256 Fingerabdruck
    is_segmented: bool = False
    competences: List[CompetenceDTO]

    @classmethod
    def create_with_hash(cls, **data):
        """Zentraler Konstruktor: Erzeugt den SHA-256 Hash automatisch."""
        if 'raw_text' in data and 'raw_text_hash' not in data:
            data['raw_text_hash'] = hashlib.sha256(data['raw_text'].encode('utf-8')).hexdigest()
        return cls(**data)
