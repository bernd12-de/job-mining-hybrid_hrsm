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
from app.infrastructure.extractor.discovery_logger import log_candidates

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

    # Kompatibilitäts-Alias: Einige Tests/Clients nutzen noch die interne Methode `_run_analysis_from_text`
    def _run_analysis_from_text(self, text: str, source_name: str) -> AnalysisResultDTO:
        return self.run_analysis_from_scraped_text(text, source_name)

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

        # Vorsegmentierter Text ohne Benefits/About-Blöcke
        prefiltered_text = meta.get('processing_text') or text

        # Fallback-Logik: Wenn Segmentierung fehlschlägt (z.B. < 50 Zeichen), nimm prefilter.
        if len(segmented_text) < 50:
            logger.info(f"Segmentierung für '{source_name}' zu kurz. Nutze vorgefilterten Text.")
            analysis_text = prefiltered_text if prefiltered_text else text
        else:
            analysis_text = segmented_text
        # -----------------------------------------------


        # Datum normalisieren (Fallback auf heute, falls MetadataExtractor nichts findet)
        posting_date = meta.get('posting_date') or "2024-12-01"

        # Schritt B: Kontext-Erkennung (Branche & Rolle)
        # Versuche zuerst die neuere detect_industry API, fallback auf classify_industry (Legacy) falls nötig
        industry = None
        try:
            if hasattr(self.organization_service, 'detect_industry'):
                industry = self.organization_service.detect_industry(text)
        except Exception:
            industry = None

        if not isinstance(industry, str):
            # Fallback
            industry = getattr(self.organization_service, 'classify_industry', lambda t: None)(text)

        role = self.role_service.classify_role(text, meta.get('job_title') or source_name)

        # Schritt C: NLP Extraktion (Ebene 1-5)
        # WICHTIG: Übergibt 'role' an den Extractor, wie im Interface gefixt.
        competences = self.competence_extractor.extract_competences(text=analysis_text, role=role)

        # Discovery: unbekannte Kandidaten sammeln (vereinfachte Heuristik)
        try:
            # Labels für Ausschluss (bekannte ESCO-Begriffe)
            known_labels = set()
            repo = getattr(self.competence_extractor, 'repository', None)
            if repo is not None and hasattr(repo, 'get_all_identifiable_labels'):
                known_labels = set(l.lower() for l in (repo.get_all_identifiable_labels() or []))

            # Tokenisierung: einfache Wort-Tokens
            import re
            tokens = re.findall(r"[A-Za-zÄÖÜäöüß][-A-Za-z0-9ÄÖÜäöüß]{2,}", analysis_text)
            freq = {}
            for t in tokens:
                tl = t.lower()
                # Filter: nicht bereits bekannte Labels (roh oder kompakt), nicht zu kurz
                if len(tl) < 4:
                    continue
                if tl in known_labels or tl.replace(' ', '') in known_labels:
                    continue
                # Ein paar triviale Stopwörter ausschließen
                if tl in {"und", "oder", "die", "der", "das", "ein", "eine"}:
                    continue
                freq[tl] = freq.get(tl, 0) + 1

            # Kandidaten nach Häufigkeit sortieren, Top-N
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
            candidates = [{"term": k, "role": role, "context": "segmented", "count": v} for k, v in top]
            if candidates:
                log_candidates(candidates)
        except Exception:
            # Discovery ist best-effort, Fehler hier sollen die Pipeline nicht stoppen
            pass

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

    def create_competence_dto(self, **kwargs):
        """Zentrale Factory-Methode für Extractors (z.B. Discovery).
        Prüft Blacklist und Validität bevor ein CompetenceDTO erzeugt wird.
        Gibt None zurück, wenn das DTO verworfen werden soll.
        """
        term = kwargs.get('original_term', '')
        try:
            # Versuche die Blacklist über das Repository zu prüfen, falls vorhanden
            repo = getattr(self.competence_extractor, 'repository', None)
            if repo is not None and hasattr(repo, 'is_blacklisted') and repo.is_blacklisted(term):
                return None
        except Exception:
            pass

        try:
            return AnalysisResultFactory.create_competence(
                original_term=kwargs.get('original_term'),
                esco_label=kwargs.get('esco_label'),
                esco_uri=kwargs.get('esco_uri'),
                level=kwargs.get('level', 1),
                esco_group_code=kwargs.get('esco_group_code'),
                is_digital=kwargs.get('is_digital', False),
                is_discovery=kwargs.get('is_discovery', False),
                role_context=kwargs.get('role_context'),
                confidence=kwargs.get('confidence_score', 0.7)
            )
        except Exception:
            return None
