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
        self.location_patterns = r"(berlin|hamburg|münchen|koeln|köln|frankfurt|stuttgart|düsseldorf|duesseldorf|gummersbach|mainz|augsburg|leipzig|dortmund|essen|bremen|hannover|nürnberg|nuernberg|mannheim|karlsruhe|bochum)"

        # Abschnitte, die für Kompetenzen irrelevante Inhalte enthalten (Benefits, About us, Kontakt)
        self.EXCLUDE_SECTIONS = re.compile(
            r"(wir bieten|benefits|was wir bieten|what we offer|about us|über uns|ueber uns|why us|warum wir|unternehmen|kontakt|bewerbung)",
            re.IGNORECASE,
        )

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
        filtered_text = self._strip_irrelevant_sections(text)

        tasks_match = self.TASK_PATTERN.search(filtered_text)
        reqs_match = self.REQ_PATTERN.search(filtered_text)

        tasks_clean = tasks_match.group(1).strip() if tasks_match else ""
        reqs_clean = reqs_match.group(1).strip() if reqs_match else ""

        # Segmentierung validieren (Ebene 6)
        clean_segment = f"{tasks_clean} {reqs_clean}".strip()
        is_segmented = bool(tasks_clean or reqs_clean) and len(clean_segment) > 50

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
            "processing_text": clean_segment if is_segmented else filtered_text,
            "inferred_level": inferred_level,
            "source_domain": source_domain,
            "tasks_clean": tasks_clean,
            "requirements_clean": reqs_clean,
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
        if re.search(r"remote|homeoffice|home\s?office|flexibel arbeiten", text, re.IGNORECASE):
            return "Remote"

        matches = re.findall(self.location_patterns, text, re.IGNORECASE)
        if not matches:
            # Bundesländer oder Regionen als Fallback
            if re.search(r"bayern|nrw|baden-württemberg|baden wuerttemberg|sachsen", text, re.IGNORECASE):
                return "Deutschland"
            return "Deutschland"

        # Normalisiere Schreibweisen (z.B. koeln -> Köln)
        normalized = [m.replace('koeln', 'Köln').replace('duesseldorf', 'Düsseldorf').replace('nuernberg', 'Nürnberg') for m in matches]
        return max(set(normalized), key=normalized.count).title()

    def _extract_job_category(self, text: str) -> str:
        normalized_text = text.lower()
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, normalized_text):
                return category
        return "Sonstige Fachgebiete"

    def _strip_irrelevant_sections(self, text: str) -> str:
        """Entfernt Benefits/About/Kontakt-Abschnitte, damit Analyse nur fachliche Teile nutzt."""
        lines = text.splitlines()
        kept_lines = []
        skip_block = False

        heading_reset = re.compile(r"(aufgaben|tasks|tätigkeiten|profil|requirements|qualifikation)", re.IGNORECASE)

        for line in lines:
            if self.EXCLUDE_SECTIONS.search(line):
                skip_block = True
                continue

            # Neue relevante Überschrift beendet das Skipping
            if skip_block and heading_reset.search(line):
                skip_block = False

            if not skip_block:
                kept_lines.append(line)

        cleaned = "\n".join(kept_lines).strip()

        # Falls wir nichts behalten konnten, nutze den Originaltext als Fallback
        return cleaned if cleaned else text
