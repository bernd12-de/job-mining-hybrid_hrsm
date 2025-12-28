# normalize.py

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

# --------------------------------------------------------------------
# A. DATUMS-NORMALISIERUNG
# --------------------------------------------------------------------

def parse_date(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Versucht, ein Veröffentlichungsdatum aus dem Rohtext zu extrahieren (z.B. 'vor 4 Tagen').

    Gibt ein Tupel zurück: (ISO_Datum [YYYY-MM-DD], Gefundener_Term, Jahr)
    Wenn kein Datum gefunden wird, werden None-Werte zurückgegeben.
    """

    normalized_text = text.lower()

    # 1. Muster für "Vor X Tagen/Wochen/Monaten/Jahren" (StepStone, LinkedIn)
    # Sucht nach "vor {Zahl} {Einheit}"
    time_delta_match = re.search(
        r'vor\s+(\d+)\s*(tag|woche|monat|jahr)en?',
        normalized_text,
        re.IGNORECASE
    )

    if time_delta_match:
        value = int(time_delta_match.group(1))
        unit = time_delta_match.group(2)
        today = datetime.now()

        # Berechne das ungefähre Posting-Datum
        if unit.startswith('tag'):
            posting_date = today - timedelta(days=value)
        elif unit.startswith('woche'):
            posting_date = today - timedelta(weeks=value)
        elif unit.startswith('monat'):
            posting_date = today - timedelta(days=30 * value) # Vereinfacht
        elif unit.startswith('jahr'):
            posting_date = today - timedelta(days=365 * value) # Vereinfacht
        else:
            return None, None, None # Sollte nicht passieren

        # Gebe das Datum im ISO-Format zurück
        iso_date = posting_date.strftime("%Y-%m-%d")
        year = posting_date.strftime("%Y")
        found_term = time_delta_match.group(0)

        return iso_date, found_term, year

    # 2. Muster für explizite Datumsangaben (z.B. 25.06.2024 oder 25. Juni 2024)
    # Hier müsste erweiterte Logik stehen, aber für diesen MVP wird der Delta-Match priorisiert.

    # 3. Muster für "Heute", "Gestern"
    if 'heute' in normalized_text:
        iso_date = datetime.now().strftime("%Y-%m-%d")
        return iso_date, 'heute', iso_date.split('-')[0]

    if 'gestern' in normalized_text:
        yesterday = datetime.now() - timedelta(days=1)
        iso_date = yesterday.strftime("%Y-%m-%d")
        return iso_date, 'gestern', iso_date.split('-')[0]

    return None, None, None

# --------------------------------------------------------------------
# B. TEXT-BEREINIGUNG UND NORMALISIERUNG (Optionale Funktionen)
# --------------------------------------------------------------------

def clean_and_normalize_text(text: str) -> str:
    """
    Führt grundlegende Bereinigungs- und Normalisierungsschritte durch:
    - Kleinbuchstaben
    - Entfernt doppelte Leerzeichen und Zeilenumbrüche
    - Entfernt spezifische Steuerzeichen (z.B. \x00, was bereits im Workflow Manager geschieht)
    """

    # Text in Kleinbuchstaben umwandeln
    text = text.lower()

    # Entferne typische Steuerzeichen aus OCR/Parsing-Fehlern
    text = text.replace('\x00', '').replace('\u200b', '')

    # Entferne überflüssige Whitespace und Zeilenumbrüche (kann bei NLP hilfreich sein)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def normalize_competence_term(term: str) -> str:
    """
    Normalisiert einen einzelnen Kompetenzbegriff (z.B. für das Caching oder Mapping).
    """
    return term.lower().strip()
