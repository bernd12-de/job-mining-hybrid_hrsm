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

# Der Pfad, in dem die Dateien im Unterordner 'esco/' liegen sollen
ESCO_DATA_PATH = os.path.join(os.path.dirname(__file__), 'esco')

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
    Lädt alle relevanten ESCO-Labels aus allen Quell-CSVs in den Cache.
    """
    global ESCO_TARGET_LABELS_CACHE
    if ESCO_TARGET_LABELS_CACHE is not None:
        return ESCO_TARGET_LABELS_CACHE

    all_labels = set()

    for filename in ESCO_SOURCE_FILES:
        # Pfad: .../python-backend/infrastructure/data/esco/DATEINAME.csv
        file_path = os.path.join(ESCO_DATA_PATH, filename)

        try:
            # Versuche Semikolon-Trenner (ESCO-Standard)
            try:
                df = pd.read_csv(file_path, delimiter=';')
            except Exception:
                df = pd.read_csv(file_path, delimiter=',')

            # Extrahiere Labels basierend auf dem Dateityp
            if 'Level 3 preferred term' in df.columns:
                # Hierarchie-Datei: Nutze spezifische Level 3/2 Begriffe
                label_cols = ['Level 3 preferred term', 'Level 2 preferred term']
                for col in label_cols:
                    if col in df.columns:
                        all_labels.update(df[col].dropna().unique().tolist())
            elif 'preferredLabel' in df.columns:
                # Collections-Dateien: Nutze das Haupt-Label
                all_labels.update(df['preferredLabel'].dropna().unique().tolist())

        except FileNotFoundError:
            # DIESER LOG MUSS JETZT FEHLEN!
            print(f"⚠️ FEHLER: ESCO-Datei nicht gefunden: {filename}")
        except Exception as e:
            print(f"FEHLER beim Laden von {filename}: {e}")

    # Füge die manuellen Ziel-Labels hinzu und bereinige
    all_labels.update(ESCO_MAPPING_DATA.values())


    # NEUER ZÄHLER FÜR SICHERHEIT:
    final_labels = sorted(list(all_labels))
    print(f"*** ESCO-Integration erfolgreich: {len(final_labels)} Labels aus CSVs geladen ***")

    ESCO_TARGET_LABELS_CACHE = final_labels
    return ESCO_TARGET_LABELS_CACHE




def get_esco_target_labels() -> List[str]:
    """Gibt die Liste aller eindeutigen, offiziellen ESCO-Labels zurück."""
    return _load_esco_labels_from_csv()


'''ESCO_TARGET_LABELS_CACHE = sorted(list(all_labels))
return ESCO_TARGET_LABELS_CACHE'''
