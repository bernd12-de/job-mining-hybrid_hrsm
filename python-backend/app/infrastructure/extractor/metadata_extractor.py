import re
import os
from typing import Dict, Optional

# Import für Zeitreihen-Analyse (Ebene 7)
try:
    from app.core.normalize import parse_date
except ImportError:
    def parse_date(text): return ("2024-01-01", None, None)

class MetadataExtractor:
    """
    Kombiniert deine detaillierten Kategorien mit den
    notwendigen Feldern für die Kotlin-Datenklassen.
    """

    def __init__(self):
        # DEINE MUSTER (Vollständig übernommen)
        self.category_patterns = {
            "IT & Softwareentwicklung": r"(entwickler|developer|programmier|software|it|informatik|cloud|cyber\s?security)",
            "UX/UI Design": r"(ux\s?design|ui\s?design|user\s?experience|user\s?interface|designer|grafik|konzeption)",
            "Management & Beratung": r"(manager|consultant|berater|leitung|führungskraft|strategie|geschäftsführer)",
            "Finanzen & Controlling": r"(finanz|accounting|controlling|bilanz|wirtschaftsprüf|buchhalter|ifr)",
            "Assistenz & Office": r"(assistenz|sekretariat|büro|office|administration|sachbearbeiter)",
        }
        self.location_patterns = r"(berlin|hamburg|münchen|köln|frankfurt|stuttgart|düsseldorf|gummersbach|mainz|augsburg)"

        # DEINE SEKTIONS-MUSTER (Lookahead-Version für bessere Segmentierung)
        self.TASK_PATTERN = re.compile(
            r'(?:DEINE AUFGABEN|TÄTIGKEITEN|WAS DU BEI UNS MACHST|YOUR TASKS|RESPONSIBILITIES|TASKS|WHAT YOU WILL DO)[\s\r\n:.-]+(.*?)(?=(?:DEIN PROFIL|PROFIL|REQUIREMENTS|WIR BIETEN|WIR SUCHEN|BENEFITS|ABOUT US|$))',
            re.DOTALL | re.IGNORECASE)

        self.REQ_PATTERN = re.compile(
            r'(?:PROFIL|DEIN PROFIL|YOUR PROFILE|ANFORDERUNGEN|REQUIREMENTS|QUALIFICATIONS|VORAUSSETZUNGEN|SKILLSET)[\s\r\n:.-]+(.*?)(?=(?:DEINE AUFGABEN|TASKS|WIR BIETEN|WIR SUCHEN|BENEFITS|KONTAKT|$))',
            re.DOTALL | re.IGNORECASE)

    def extract_all(self, text: str, filename: str, filepath: str = "") -> Dict:
        """
        Gibt das Dictionary zurück, das exakt zum AnalysisResultDTO passt.
        """
        iso_date, _, _ = parse_date(text)
        tasks_match = self.TASK_PATTERN.search(text)
        reqs_match = self.REQ_PATTERN.search(text)

        # Segmentierung validieren (Ebene 6)
        clean_segment = ""
        if tasks_match: clean_segment += tasks_match.group(1).strip()
        if reqs_match: clean_segment += " " + reqs_match.group(1).strip()

        is_segmented = bool(tasks_match or reqs_match) and len(clean_segment) > 50

        # WICHTIG: Felder für die wissenschaftliche Validierung (Ebene 4/5)
        inferred_level = 2
        source_domain = "Stellenanzeige"
        if "fachbuecher" in filepath.lower():
            inferred_level = 4
            source_domain = f"Fachbuch: {filename}"
        elif "modulhandbuecher" in filepath.lower():
            inferred_level = 5
            source_domain = f"Academia: {filename}"

        # RETURN: Mappt exakt auf die Variablen in Kotlin
        return {
            "job_title": self._extract_title(text, filename),
            "job_role": self._extract_job_category(text), # Mappt auf AnalysisResultDTO.jobRole
            "region": self._extract_location(text),       # Mappt auf AnalysisResultDTO.region
            "industry": self._extract_organization(text), # Hier als Branche/Firma genutzt
            "posting_date": iso_date or "2024-01-01",
            "is_segmented": is_segmented,
            "processing_text": clean_segment if is_segmented else text,
            "inferred_level": inferred_level,
            "source_domain": source_domain,
            "raw_text": text
        }

    def _extract_title(self, text: str, filename: str) -> str:
        """Extrahiert den Jobtitel aus der ersten Zeile oder nutzt den Dateinamen."""
        lines = text.split('\n')
        if lines and lines[0].strip():
            title = re.sub(r'\(m/w/d\)|\[all genders\]|\(gn\)|\|\s?.*', '', lines[0], flags=re.IGNORECASE).strip()
            return title if len(title) > 5 else filename
        return filename

    def _extract_organization(self, text: str) -> str:
        match = re.search(r'([A-Z][a-zäöüß]+\s(AG|GmbH|Group|KG|Deutschland))', text[:1000])
        return match.group(0) if match else "Unbekannte Firma"

    def _extract_location(self, text: str) -> str:
        matches = re.findall(self.location_patterns, text, re.IGNORECASE)
        return max(set(matches), key=matches.count).capitalize() if matches else "Deutschland"

    def _extract_job_category(self, text: str) -> str:
        normalized_text = text.lower()
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, normalized_text):
                return category
        return "Sonstige Fachgebiete"
