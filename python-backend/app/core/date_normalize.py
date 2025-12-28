"""
Datumparser für Job-Anzeigen
Basiert auf: Best_Practice Code Lib/normalize.py

Features:
- DE/ISO-Datumserkennung (DD.MM.YYYY, YYYY-MM-DD, "November 2024")
- Jahr-Clamp (1970 – aktuelles Jahr)
- Fallback auf None bei ungültigen Daten
"""

import re
import datetime
from typing import Tuple, Optional

# Deutsche Monatsnamen → Nummer
MONTHS_DE = {
    "januar": 1, "jan": 1,
    "februar": 2, "feb": 2,
    "märz": 3, "maerz": 3, "mrz": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mai": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "oktober": 10, "okt": 10, "oct": 10,
    "november": 11, "nov": 11,
    "dezember": 12, "dez": 12, "dec": 12
}


def _clamp_year(y: int) -> int:
    """Clampt Jahr auf realistischen Bereich (1970 – heute)"""
    now_year = datetime.date.today().year
    if y > now_year:
        return now_year
    if y < 1970:
        return 1970
    return y


def parse_date(text: str, now_utc=None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parst Datum aus unstrukturiertem Text
    
    Args:
        text: Text mit Datum (z.B. "Veröffentlicht am 12.11.2025")
        now_utc: Ignoriert (Kompatibilität)
    
    Returns:
        Tuple (iso_date, format_type, precision)
        - iso_date: "YYYY-MM-DD" oder None
        - format_type: "iso" | "dmy" | "montext" | "year_fallback" | None
        - precision: "day" | "month" | "year" | None
    
    Examples:
        >>> parse_date("2025-12-27")
        ('2025-12-27', 'iso', 'day')
        
        >>> parse_date("27.12.2025")
        ('2025-12-27', 'dmy', 'day')
        
        >>> parse_date("November 2024")
        ('2024-11-01', 'montext', 'month')
        
        >>> parse_date("2024")
        ('2024-06-15', 'year_fallback', 'year')
    """
    s = (text or "").strip()
    if not s:
        return (None, None, None)
    
    # Normalisiere Eingabe
    t = s.lower().replace(",", " ").replace("·", " ").replace("•", " ")
    t = re.sub(r"\s+", " ", t)
    
    # 1) ISO-Format: YYYY-MM-DD
    m = re.search(r"\b(20\d{2}|19\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b", t)
    if m:
        y, mn, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = _clamp_year(y)
        return (f"{y:04d}-{mn:02d}-{d:02d}", "iso", "day")
    
    # 2) DE-Format: DD.MM.YYYY oder DD/MM/YYYY
    m = re.search(r"\b(0?[1-9]|[12]\d|3[01])[.\-/](0?[1-9]|1[0-2])[.\-/](\d{4})\b", t)
    if m:
        d, mn, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = _clamp_year(y)
        return (f"{y:04d}-{mn:02d}-{d:02d}", "dmy", "day")
    
    # 3) Textmonat + Jahr: "November 2024"
    m = re.search(r"\b([a-zäöü]{3,10})\s+(\d{4})\b", t)
    if m:
        mon_text = m.group(1).replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        mon = MONTHS_DE.get(mon_text)
        y = int(m.group(2))
        if mon:
            y = _clamp_year(y)
            return (f"{y:04d}-{mon:02d}-01", "montext", "month")
    
    # 4) Nur Jahr: "2024"
    m = re.search(r"\b(20\d{2}|19\d{2})\b", t)
    if m:
        y = _clamp_year(int(m.group(1)))
        # Fallback auf Jahresmitte
        return (f"{y:04d}-06-15", "year_fallback", "year")
    
    return (None, None, None)


def normalize_posting_date(text: str, fallback: str = None) -> str:
    """
    Parst Datum und gibt ISO-String zurück (mit Fallback)
    
    Args:
        text: Text mit Datum
        fallback: Fallback-Datum (default: heute)
    
    Returns:
        ISO-Datum "YYYY-MM-DD"
    """
    iso_date, _, _ = parse_date(text)
    if iso_date:
        return iso_date
    
    if fallback:
        return fallback
    
    # Default: heute
    return datetime.date.today().isoformat()
