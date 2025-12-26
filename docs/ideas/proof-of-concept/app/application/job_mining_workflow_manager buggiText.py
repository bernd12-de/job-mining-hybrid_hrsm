import hashlib
import logging
from typing import BinaryIO, Optional, List
from pathlib import Path
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.core.normalize import parse_date
from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService

from app.domain.models import AnalysisResultDTO
from app.interfaces.interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor

logger = logging.getLogger(__name__)
class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""

    """
    Der Chef-Organisator.
    Orchestriert Text-Extraktion, NLP-Analyse und Ergebnis-Erstellung.
    """

    def __init__(self,
                 text_extractor: ITextExtractor,
                 competence_extractor: ICompetenceExtractor,
                 organization_service: OrganizationService,
                 role_service: RoleService,
                 metadata_extractor: MetadataExtractor  # <--- KORREKTUR 1: Name muss exakt stimmen!
                 ):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service

        # KORREKTUR 2: Wir nutzen die Instanz, die von außen reingereicht wird!
        # Nicht: self.meta_extractor = MetadataExtractor()
        self.metadata_extractor = metadata_extractor

     # =========================================================================
    # EINSTIEGSPUNKTE (Public Methods)
    # =========================================================================

    def _run_analysis_from_text(self, raw_text: str, source_name: str) -> AnalysisResultDTO:


        # 1. Hashing
        raw_text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. Metadaten-Extraktion (Zugriff jetzt über self.metadata_extractor)
        metadata = self.metadata_extractor.extract_all(raw_text, filename=source_name)

        # Text-Segmentierung (Intelligent)
        tasks_clean = metadata.get('tasks_clean', '')
        requirements_clean = metadata.get('requirements_clean', '')
        clean_text_for_esco = (tasks_clean + " " + requirements_clean).strip()

        # Fallback auf Rohtext, wenn Segmentierung fehlschlägt
        if len(clean_text_for_esco) < 50:
            clean_text_for_esco = raw_text

        # 3. Kompetenzen (sucht im sauberen Text)
        competences = self.competence_extractor.extract_competences(clean_text_for_esco)

        # 4. Kontext
        industry = self.organization_service.classify_industry(raw_text)
        job_role = self.role_service.classify_role(
            job_text=raw_text,
            job_title=metadata.get('job_title', source_name)
        )

        iso_date, _, _ = parse_date(raw_text)

        return AnalysisResultDTO(
            title=metadata.get('job_title') or source_name,
            job_role=job_role,
            region=metadata.get('location') or "Unbekannt",
            industry=industry,
            posting_date=iso_date or "2024-12-01",
            raw_text_hash=raw_text_hash,
            raw_text=raw_text,
            is_segmented=metadata.get('is_segmented', False),
            competences=competences
        )

    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        """Verarbeitet PDF/DOCX Dateien. Einstiegspunkt für die API."""
        raw_text = self.text_extractor.extract_text(file_stream, filename)
        cleaned_raw_text = raw_text.replace('\x00', '')
        return self._run_analysis_from_text(cleaned_raw_text, filename)

    def run_analysis_from_scraped_text(self, cleaned_text: str, source_name: str) -> AnalysisResultDTO:
        return self._run_analysis_from_text(cleaned_text, source_name)

    def process_local_directory(self) -> List[AnalysisResultDTO]:
        """Scannt lokalen Ordner."""
        results = []
        # Hinweis: Prüfe ob der Pfad in deinem Container wirklich data/job_ads oder data/jobs heißt
        job_dir = Path("data/jobs")
        if not job_dir.exists(): return []

        # Erweitert auf PDF und DOCX, falls du die auch lokal hast
        files = list(job_dir.glob("*.*"))
        for file_path in files:
            if file_path.suffix not in ['.pdf', '.docx', '.txt']: continue

            try:
                # Hier nutzen wir run_full_analysis für Files
                with open(file_path, "rb") as f:
                    analysis = self.run_full_analysis(f, file_path.name)
                    results.append(analysis)
            except Exception as e:
                print(f"❌ Fehler bei Datei {file_path.name}: {e}")
        return results
