# job_mining_workflow_manager.py (FINALE VERSION MIT DOMAIN SERVICES)

import hashlib
from typing import BinaryIO, Optional

# VOM VORHERIGEN CODE (MUSS VERFÜGBAR SEIN)
from metadata_extractor import MetadataExtractor
# ❌ ALTE/STATISCHE IMPORTS ENTFERNEN (müssen Sie in Ihrer Datei löschen)
# from organization_extractor import extract_branch
from normalize import parse_date
from domain.services.organization_service import OrganizationService
from domain.services.role_service import RoleService # NEU
# ----------------------------------------------

from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from models import AnalysisResultDTO


class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""
    # 🚨 KORRIGIERT: FÜGT DEN RoleService ZUR DI HINZU
    def __init__(self,
                 text_extractor: ITextExtractor,
                 competence_extractor: ICompetenceExtractor,
                 organization_service: OrganizationService,
                 role_service: RoleService # NEU: Role Service injizieren
                 ):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service # Speichert den Role Service
        # NEU: Initialisierung des Metadaten-Extraktors
        # DIESER EXTRAKTOR MUSS IM NÄCHSTEN SCHRITT AUCH REFRAKTORIERT WERDEN (Role Service)


    def _run_analysis_from_text(self, raw_text: str, source_name: str) -> AnalysisResultDTO:

        # 1. Hashing (unverändert)
        raw_text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. KOMPETENZ-EXTRAKTION (unverändert)
        competences = self.competence_extractor.extract_competences(raw_text)

        # 3. METADATEN-EXTRAKTION
        self.meta_extractor = MetadataExtractor()
        metadata = self.meta_extractor.extract_all(raw_text, filename=source_name)

        # Datums-Parsing und Normalisierung
        iso_date, _, _ = parse_date(raw_text)
        posting_date = iso_date or "2024-12-01"

        # 🚨 FIX 2: Nutzt den injizierten Organization Service anstelle der statischen Funktion
        # Übergibt den Rohtext für die Branchen-Klassifizierung
        industry = self.organization_service.classify_industry(raw_text)

        # 🚨 FIX 2: Rollen-Klassifizierung (DB-gestützt)
        job_role = self.role_service.classify_role(
            job_text=raw_text,
            job_title=metadata.get('job_title', source_name)
        )

        # 5. Output
        return AnalysisResultDTO(
            title=metadata.get('job_title') or source_name,
            job_role=job_role, # ✅ Jetzt DB-gestützt
            region=metadata.get('location') or "Unbekannt",
            industry=industry, # ✅ Jetzt DB-gestützt
            posting_date=posting_date,
            raw_text_hash=raw_text_hash,
            raw_text=raw_text,
            competences=competences
        )

    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        """Extrahiert Text aus einem Dateistream und führt dann die Analyse durch."""

        raw_text = self.text_extractor.extract_text(file_stream, filename)
        cleaned_raw_text = raw_text.replace('\x00', '')

        return self._run_analysis_from_text(cleaned_raw_text, filename)


    # NEU: Methode für den Scrape-Endpunkt, die den BEREINIGTEN Text entgegennimmt
    def run_analysis_from_scraped_text(self, cleaned_text: str, source_name: str) -> AnalysisResultDTO:
        """
        Startet die Analyse mit Text, der bereits von einem vorgelagerten Scraper
        (in api_endpoints.py) extrahiert und gereinigt wurde.
        """
        # Delegiert direkt an die interne Analyselogik
        return self._run_analysis_from_text(cleaned_text, source_name)
