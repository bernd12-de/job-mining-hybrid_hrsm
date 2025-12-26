import logging
from typing import BinaryIO, Optional

# Core & Domain
from app.core.normalize import parse_date
from app.domain.models import AnalysisResultDTO

# Interfaces
from app.interfaces.interfaces import (
    IJobMiningWorkflowManager,
    ITextExtractor,
    ICompetenceExtractor
)

# Services & Factory
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)

class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """
    Der Manager ist nur noch der Orchestrator für EINE Datei.
    Er weiß nichts von Ordnern (Batch) oder HTTP-Requests.
    """

    def __init__(self,
                 text_extractor: ITextExtractor,
                 competence_extractor: ICompetenceExtractor,
                 organization_service,
                 role_service,
                 metadata_extractor: MetadataExtractor):

        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service
        self.metadata_extractor = metadata_extractor

    async def run_full_analysis(self, file_object: BinaryIO, filename: str) -> AnalysisResultDTO:
        """
        Einstiegspunkt 1: Dateibasierte Analyse (PDF, DOCX via Upload oder Batch).
        Wird von api_endpoints.py (Upload) UND JobDirectoryProcessor (Batch) genutzt.
        """
        # 1. Text extrahieren (Delegation an AdvancedTextExtractor)
        text = self.text_extractor.extract_text(file_object, filename)

        if not text:
            # Fehler werfen oder leeres Result zurückgeben (hier: Fehler für sauberes Logging)
            logger.error(f"AdvancedTextExtractor lieferte leeren Text für '{filename}'.")
            raise ValueError(f"AdvancedTextExtractor konnte keinen Text aus {filename} lesen.")

        # 2. Cleaning (WICHTIG: Null-Bytes entfernen, sonst DB-Fehler oder 'kein Text')
        cleaned_raw_text = text.replace('\x00', '')

        return self._execute_pipeline(cleaned_raw_text, source_name=filename)

    def run_analysis_from_scraped_text(self, text: str, source_name: str) -> AnalysisResultDTO:
        """
        Einstiegspunkt 2: Textbasierte Analyse (Web Scraper).
        """
        # Auch hier Cleaning sicherheitshalber
        cleaned_text = text.replace('\x00', '')
        return self._execute_pipeline(cleaned_text, source_name=source_name)

    def _execute_pipeline(self, text: str, source_name: str) -> AnalysisResultDTO:
        """
        Die KERN-LOGIK (SSoT).
        Hier läuft der CRISP-DM Prozess für ein einzelnes Dokument durch.
        """

        # Schritt A: Metadaten & Datum (Ebene 6)
        meta = self.metadata_extractor.extract_all(text, filename=source_name)

        # --- 💎 GOLD: Smarte Segmentierung integriert ---
        tasks = meta.get('tasks_clean', '')
        reqs = meta.get('requirements_clean', '')
        # Baue "Konzentrat" für die KI
        segmented_text = (tasks + " " + reqs).strip()

        # Fallback-Logik: Wenn Segmentierung fehlschlägt (z.B. < 50 Zeichen), nimm alles.
        if len(segmented_text) < 50:
            logger.info(f"Segmentierung für '{source_name}' zu kurz. Nutze Volltext.")
            analysis_text = text
        else:
            analysis_text = segmented_text
        # -----------------------------------------------


        # Datum normalisieren (Fallback auf heute, falls MetadataExtractor nichts findet)
        posting_date = meta.get('posting_date') or "2024-12-01"

        # Schritt B: Kontext-Erkennung (Branche & Rolle)
        industry = self.organization_service.detect_industry(text)
        role = self.role_service.classify_role(text, meta.get('job_title') or source_name)

        # Schritt C: NLP Extraktion (Ebene 1-5)
        # WICHTIG: Übergibt 'role' an den Extractor, wie im Interface gefixt.
        competences = self.competence_extractor.extract_competences(text=text, role=role)

        # Schritt D: DTO Bauen (Ebene 7)
        # Nutzt die Factory, um Zirkelbezüge zu vermeiden.
        return AnalysisResultFactory.create_result(
            title=meta.get('job_title') or source_name,
            job_role=role,
            industry=industry,
            region=meta.get('region', "Unbekannt"),
            posting_date=posting_date,
            raw_text=text,
            is_segmented=meta.get('is_segmented', False),
            competences=competences
        )
