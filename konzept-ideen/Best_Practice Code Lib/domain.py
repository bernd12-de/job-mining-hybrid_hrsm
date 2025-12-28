from __future__ import annotations
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime
class Precision(str, Enum):
    day='day'; month='month'; year='year'; unknown='unknown'
class Confidence(BaseModel):
    value: float = 0.0
    rationale: Optional[str] = None
class SkillRef(BaseModel):
    name: str
    esco_id: Optional[str] = None
    confidence: Confidence = Field(default_factory=Confidence)
    source: str = 'rule'
class Sections(BaseModel):
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    about: Optional[str] = None
    other: Optional[str] = None
class Tags(BaseModel):
    tools: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
class Provenance(BaseModel):
    source_path: str
    collected_at: datetime
    country: Optional[str] = None
    stage_params: Dict[str, str] = Field(default_factory=dict)
class JobPosting(BaseModel):
    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: str
    posting_date: Optional[datetime] = None
    posting_date_precision: Precision = Precision.unknown
    language: Optional[str] = None
    remote: Optional[bool] = None
    skills: List[SkillRef] = Field(default_factory=list)
    sections: Sections = Field(default_factory=Sections)
    tags: Tags = Field(default_factory=Tags)
    version: str = '1.0'
    provenance: Provenance
