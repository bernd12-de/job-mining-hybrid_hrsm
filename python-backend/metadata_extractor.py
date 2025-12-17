# metadata_extractor.py

import re
from typing import Dict, List, Optional, Tuple

# Import der Hilfsfunktionen, die Sie wahrscheinlich in einer 'normalize.py' haben
from normalize import parse_date

class MetadataExtractor:
    """
    Extrahiert grundlegende Job-Metadaten (Titel, Ort, Firma, Datum)
    unter Verwendung von Heuristiken und Regex-Mustern.
    """

    def __init__(self):
        # Einfache Regex-Muster zur Identifikation gängiger Job-Bereiche
        self.category_patterns = {
            "IT & Softwareentwicklung": r"(entwickler|developer|programmier|software|it|informatik|cloud|cyber\s?security)",
            "UX/UI Design": r"(ux\s?design|ui\s?design|user\s?experience|user\s?interface|designer|grafik|konzeption)",
            "Management & Beratung": r"(manager|consultant|berater|leitung|führungskraft|strategie|geschäftsführer)",
            "Finanzen & Controlling": r"(finanz|accounting|controlling|bilanz|wirtschaftsprüf|buchhalter|ifr)",
            "Assistenz & Office": r"(assistenz|sekretariat|büro|office|administration|sachbearbeiter)",
        }
        # Muster für die wahrscheinlichsten Orte (Annahme: Gängige Großstädte)
        self.location_patterns = r"(berlin|hamburg|münchen|köln|frankfurt|stuttgart|düsseldorf|gummersbach|mainz|augsburg)"

    def _extract_title(self, text: str, filename: str) -> str:
        """Versucht, den Jobtitel zu extrahieren, meist aus der ersten Zeile."""
        # Sucht in den ersten 5 Zeilen (typischerweise der Header)
        lines = text.split('\n')
        if len(lines) > 0 and lines[0].strip():
            # Die erste Zeile ist oft der Titel, bereinigt um gängige Zusätze
            title = lines[0].strip()
            title = re.sub(r'\(m/w/d\)|\[all genders\]|\(gn\)|\|\s?.*', '', title, flags=re.IGNORECASE).strip()
            return title if len(title) > 10 else filename
        return filename

    def _extract_organization(self, text: str) -> str:
        """Versucht, den Firmennamen aus den ersten Abschnitten zu extrahieren."""
        # Sucht nach Namen in den ersten 1000 Zeichen (oft nah am Job-Titel)
        match = re.search(r'([A-Z][a-zäöüß]+\s(AG|GmbH|GmbH\s&\sCo\.\sKG|e\.V\.|Group|Deutschland))', text[:1000])
        return match.group(0) if match else "Unbekannte Firma"

    def _extract_location(self, text: str) -> str:
        """Extrahiert bekannte Orte aus dem Rohtext."""
        # Sucht nach Orten im ganzen Dokument
        matches = re.findall(self.location_patterns, text, re.IGNORECASE)
        # Gibt den ersten gefundenen, normalisierten Ort zurück
        return max(set(matches), key=matches.count).capitalize() if matches else "Unbekannt"

    def _extract_job_category(self, text: str) -> str:
        """Klassifiziert die Rolle anhand von Schlüsselbegriffen im Text."""
        normalized_text = text.lower()

        # Gehe die vordefinierten Muster durch und stoppe beim ersten Match
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, normalized_text):
                return category

        return "Sonstige Fachgebiete"

    # Muster zur Isolation der Aufgaben-Sektion
    TASK_SECTION_PATTERN = re.compile(r'(?:DEINE AUFGABEN|TÄTIGKEITEN|WAS DU BEI UNS MACHST|YOUR TASKS)[\s\r\n:.]+(.*?)(?=\n\s*(?:DEIN PROFIL|PROFIL|WIR BIETEN|KONTAKT|STANDORT|GEHALT|WEITERE INFOS|$))', re.DOTALL | re.IGNORECASE | re.MULTILINE)

    # Muster zur Isolation der Profil/Anforderungs-Sektion
    REQUIREMENTS_SECTION_PATTERN = re.compile(r'(?:PROFIL|DEIN PROFIL|YOUR PROFILE|ANFORDERUNGEN|VORAUSSETZUNGEN|MUST-HAVES|NICE-TO-HAVE)[\s\r\n:.]+(.*?)(?=\n\s*(?:DEINE AUFGABEN|WIR BIETEN|KONTAKT|STANDORT|GEHALT|WEITERE INFOS|$))', re.DOTALL | re.IGNORECASE | re.MULTILINE)


    def extract_all(self, text: str, filename: str) -> Dict[str, str]:
        """Führt alle Extraktionen aus und gibt ein konsolidiertes Dictionary zurück."""

        # Datums-Parsing (nutzt parse_date aus normalize.py)
        # Wenn parse_date verfügbar ist, liefert es ein ISO-Format oder None
        iso_date, _, _ = parse_date(text)
        tasks_match = self.TASK_SECTION_PATTERN.search(text)
        requirements_match = self.REQUIREMENTS_SECTION_PATTERN.search(text)

        return {
            "job_title": self._extract_title(text, filename),
            "organization": self._extract_organization(text),
            "location": self._extract_location(text),
            "job_category": self._extract_job_category(text),
            "posting_date": iso_date, # Wird im Workflow Manager weiter verarbeitet
            "raw_text": text,
            # KERN-FIX: Füge saubere Segmente hinzu
            "tasks_clean": tasks_match.group(1).strip() if tasks_match else "",
            "requirements_clean": requirements_match.group(1).strip() if requirements_match else "",
        }
