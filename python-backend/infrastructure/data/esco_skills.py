import pandas as pd
import os
from typing import Dict, List, Optional
import json # Neu: Für JSON-Caching

# --- A. Konfiguration des Datenpfads ---
ESCO_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'esco')
# NEU: Pfad zur Cache-Datei, um CSV-Parsing beim Hochfahren zu vermeiden
ESCO_CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'esco_labels_cache.json')

# --- B. Direkte Zuordnung ---
ESCO_MAPPING_DATA = {
    "sql": "Datenbanken verwalten",
    "datenanalyse": "Datenanalyse-Software benutzen",
    "user experience design": "Benutzererfahrung konzipieren",
    "prototypen": "Prototyping durchführen",
    "wireframes": "Wireframes und Mock-ups erstellen",
    "teamgeist": "Teamfähigkeit demonstrieren",
    "jira": "Project-Management-Software benutzen",
    "scrum": "SCRUM anwenden",
}

ESCO_TARGET_LABELS_CACHE: Optional[List[str]] = None
ESCO_MAPPING_CACHE: Optional[Dict[str, str]] = None


def _load_esco_labels_from_csv_to_cache() -> List[str]:
    """
    Diese Funktion parst die CSVs robust und schreibt das Ergebnis in den JSON-Cache.
    """
    all_labels = set()

    # 1. Dynamisches Scannen des ESCO-Ordners
    try:
        all_files = os.listdir(ESCO_DATA_PATH)
    except FileNotFoundError:
        print(f"❌ FEHLER: ESCO-Datenpfad nicht gefunden: {ESCO_DATA_PATH}")
        return []

    skill_files = [f for f in all_files if f.endswith('.csv') and ('skill' in f.lower() or 'collection' in f.lower()) and not f.startswith('occupation')]

    for filename in skill_files:
        full_path = os.path.join(ESCO_DATA_PATH, filename)

        try:
            df = None
            # Robustes Lesen: Erst Semikolon, dann Komma
            try:
                df = pd.read_csv(full_path, delimiter=';', encoding='utf-8')
                if df.shape[1] <= 2: raise ValueError
            except Exception:
                df = pd.read_csv(full_path, delimiter=',', encoding='utf-8')

            # --- ROBUSTE SPALTEN-ERKENNUNG ---
            preferred_term_cols = [col for col in df.columns if 'preferred term' in col.lower()]

            if preferred_term_cols:
                for col in preferred_term_cols:
                    all_labels.update(df[col].dropna().unique().tolist())

            if 'preferredLabel' in df.columns:
                all_labels.update(df['preferredLabel'].dropna().unique().tolist())

        except Exception as e:
            print(f"❌ FEHLER beim Parsen von {filename}: {e}")

    all_labels.update(ESCO_MAPPING_DATA.values())
    final_labels = sorted(list(all_labels))

    # Schreibe den Cache
    try:
        with open(ESCO_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_labels, f, ensure_ascii=False)
        print(f"*** ✅ ESCO-Cache erfolgreich erstellt: {len(final_labels)} Labels. ***")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben des ESCO-Cache: {e}")

    return final_labels


def _load_esco_labels_from_cache() -> List[str]:
    """
    Lade ESCO-Labels: Versucht zuerst den Cache, bei Fehler wird neu geparst.
    """
    global ESCO_TARGET_LABELS_CACHE
    if ESCO_TARGET_LABELS_CACHE is not None:
        return ESCO_TARGET_LABELS_CACHE

    # 1. Versuch: Lade aus JSON Cache
    if os.path.exists(ESCO_CACHE_PATH):
        try:
            with open(ESCO_CACHE_PATH, 'r', encoding='utf-8') as f:
                labels = json.load(f)
                ESCO_TARGET_LABELS_CACHE = labels
                print(f"*** ✅ ESCO-Cache geladen: {len(labels)} Labels. ***")
                return labels
        except Exception as e:
            print(f"⚠️ Warnung: Fehler beim Lesen des ESCO-Cache ({e}). Starte Neuaufbau.")
            # Fällt durch zu Schritt 2

    # 2. Versuch: Neuaufbau aus CSVs (nur wenn Cache nicht existiert oder fehlerhaft ist)
    print("⚠️ ESCO-Cache nicht gefunden/fehlerhaft. Starte Neuaufbau aus CSVs...")
    return _load_esco_labels_from_csv_to_cache()


def get_esco_target_labels() -> List[str]:
    """Gibt die Liste aller eindeutigen, offiziellen ESCO-Labels zurück."""
    return _load_esco_labels_from_cache()


def get_esco_mapping() -> Dict[str, str]:
    """Gibt das Mapping von Abkürzung/Synonym zu ESCO-Label zurück."""
    global ESCO_MAPPING_CACHE
    if ESCO_MAPPING_CACHE is None:
        ESCO_MAPPING_CACHE = ESCO_MAPPING_DATA
    return ESCO_MAPPING_CACHE
