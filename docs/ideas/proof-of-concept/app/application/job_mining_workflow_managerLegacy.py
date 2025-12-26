import hashlib
import logging
from typing import List, Any

from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService
from app.domain.models import AnalysisResultDTO, CompetenceDTO
from app.core.constants import GLOBAL_BLACKLIST
from app.interfaces.interfaces import ITextExtractor, ICompetenceExtractor

logger = logging.getLogger(__name__)

class JobMiningWorkflowManager:
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""
    def __init__(self, text_extractor: ITextExtractor,
                 competence_extractor: ICompetenceExtractor,
                 organization_service: OrganizationService,
                 role_service: RoleService,
                 metadata_extractor):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service
        self.metadata_extractor = metadata_extractor

    def create_competence_dto(self, **kwargs) -> Any:
        """Zentrale Factory (SSoT). Erzwingt Typ-Sicherheit (int) und Blacklist-Filterung."""
        term = kwargs.get('original_term', '').lower()
        if term in GLOBAL_BLACKLIST:
            return None
        try:
            # Pydantic korrigiert hier z.B. String-Level zu Int
            return CompetenceDTO(**kwargs)
        except Exception as e:
            logger.error(f"Inkonsistenz bei DTO-Erstellung für '{term}': {e}")
            return None

    def _run_analysis_from_text(self, text: str, source_name: str) -> AnalysisResultDTO:
        # Ebene 7: Idempotenz via SHA-256
        raw_text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        # Ebene 6: Segmentierung
        meta = self.metadata_extractor.extract_all(text, source_name)
        industry = self.organization_service.classify_industry(text)
        job_role = self.role_service.classify_role(text, meta.get('job_title', ''))

        # Fokus auf Aufgaben/Profil falls vorhanden
        search_base = meta.get('processing_text') if meta.get('is_segmented') else text
        competences = self.competence_extractor.extract_competences(search_base, job_role)

        return AnalysisResultDTO(
            title=meta.get('job_title') or source_name,
            job_role=job_role,
            region=meta.get('location') or "Unbekannt",
            industry=industry,
            posting_date=meta.get('posting_date') or "2024-01-01",
            raw_text_hash=raw_text_hash,
            raw_text=text,
            is_segmented=meta.get('is_segmented', False),
            competences=competences
        )
