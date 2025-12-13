# infrastructure/data/esco_skills.py (FINALE VERSION MIT ERWEITERTEN ESCO-QUELLEN)

import pandas as pd
import os
from typing import Dict, List

# --- A. Konfiguration der ESCO-Dateien ---
# Alle relevanten ESCO Skill Collections, die Labels enthalten
ESCO_SOURCE_FILES = [
    # Basis-Dateien
    "skillsHierarchy_de.csv",
    "researchSkillsCollection_de.csv",

    # NEUE QUELLEN FÜR HOHE ABDECKUNG:
    "digitalSkillsCollection_de.csv",   # Digitale Skills
    "digCompSkillsCollection_de.csv",   # Digitale Basis-Kompetenzen
    "greenSkillsCollection_de.csv",     # Green Skills (für Umweltthemen)
]

# FIX: Muss ZWEI Ebenen höher, um den 'data/esco' Ordner im Hauptverzeichnis zu finden
ESCO_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'esco')

# --- B. Direkte Zuordnung (Phase 1: Exakter Match) ---
# Für hochfrequente Abkürzungen/Synonyme (schnellste Zuordnung)
ESCO_MAPPING_DATA = {
    "sql": "Datenbanken verwalten",
    "datenanalyse": "Datenanalyse-Software benutzen",
    "user experience design": "Benutzererfahrung konzipieren",
    "prototypen": "Prototyping durchführen",
    "wireframes": "Wireframes und Mock-ups erstellen",
    "teamgeist": "Teamfähigkeit demonstrieren",
    "jira": "Project-Management-Software benutzen",
    "scrum": "Agile Methodiken anwenden"
}

def get_esco_mapping() -> Dict[str, str]:
    """Gibt die direkten Zuordnungen (Abkürzung -> ESCO-Label) zurück."""
    return {k: v for k, v in ESCO_MAPPING_DATA.items()}


# --- C. Dynamisches Laden der Target Labels (Cache) ---
ESCO_TARGET_LABELS_CACHE = None

def _load_esco_labels_from_csv() -> List[str]:
    """
    Lädt alle ESCO-Labels aus den konfigurierten CSVs.
    FIX: Robustere Spaltenauswahl für Hierarchie-Dateien.
    """
    global ESCO_TARGET_LABELS_CACHE
    if ESCO_TARGET_LABELS_CACHE is not None:
        return ESCO_TARGET_LABELS_CACHE

    all_labels = set()

    for filename in ESCO_SOURCE_FILES:
        full_path = os.path.join(ESCO_DATA_PATH, filename)

        try:
            # Lese die CSV
            df = pd.read_csv(full_path, delimiter=',')

            # --- ROBUSTER LADE-LOGIK FIX ---

            # 1. Haupt-Hierarchie-Datei: Alle Spalten, die 'preferred term' enthalten (Level 1, 2, 3)
            preferred_term_cols = [col for col in df.columns if 'preferred term' in col]

            if preferred_term_cols:
                # Dies erfasst alle Labels aus der Hierarchie-Datei (sollte 13k+ liefern)
                for col in preferred_term_cols:
                    all_labels.update(df[col].dropna().unique().tolist())

            # 2. Collections-Dateien: Nutzen 'preferredLabel' (sollte die restlichen ~2k liefern)
            elif 'preferredLabel' in df.columns:
                all_labels.update(df['preferredLabel'].dropna().unique().tolist())

            # --- ENDE ROBUST LADE-LOGIK FIX ---

        except FileNotFoundError:
            # Sollte jetzt nicht mehr erreicht werden
            pass
        except Exception as e:
            # Fängt Fehler beim Parsen ab
            print(f"❌ FEHLER beim Laden von {filename}: {e}")

    # Füge die manuellen Ziel-Labels hinzu und bereinige
    all_labels.update(ESCO_MAPPING_DATA.values())

    final_labels = sorted(list(all_labels))
    print(f"*** ESCO-Integration erfolgreich: {len(final_labels)} Labels aus CSVs geladen ***")

    ESCO_TARGET_LABELS_CACHE = final_labels
    return ESCO_TARGET_LABELS_CACHE


def get_esco_target_labels() -> List[str]:
    """Gibt die Liste aller eindeutigen, offiziellen ESCO-Labels zurück."""
    return _load_esco_labels_from_csv()


'''ESCO_TARGET_LABELS_CACHE = sorted(list(all_labels))
return ESCO_TARGET_LABELS_CACHE'''
