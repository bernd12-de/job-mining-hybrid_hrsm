# Basiert auf dem Best-Practice Code Lib/repositories/hybrid_competence_repository.py

import pandas as pd
import json
import os
from typing import List, Dict, Optional

# --- 1. Interne DDD-Entität ---

# Interne DDD-Entität
class Competence(object):
    """Interne Repräsentation einer Kompetenz, angereichert mit Metadaten."""
    def __init__(self, preferred_label: str, esco_uri: str, synonyms: List[str] = None, group_code: str = None):
        self.preferred_label = preferred_label
        self.esco_uri = esco_uri
        self.group_code = group_code
        self.synonyms = synonyms if synonyms is not None else []
        # Erstellt das Keyword-Set (für Fuzzy Matching)
        self.keywords = [self.preferred_label.lower()] + [s.lower() for s in self.synonyms]

class ICompetenceRepository(object):
    def get_all_competences(self) -> List[Competence]:
        raise NotImplementedError

# --- 2. Hybrid Repository Implementierung (ESCO-Logik) ---
class HybridCompetenceRepository(ICompetenceRepository):
    # Definiert die Standardpfade zur Datenhaltung (muss mit Docker-Mounts übereinstimmen)
    def __init__(self, data_path: str = "data/esco", custom_json_path: str = "data/custom_skills_extended.json"):
        self.data_path = data_path
        self.custom_json_path = custom_json_path
        self._competences: List[Competence] = []
        self._group_map: Dict[str, str] = {} # Speichert ESCO URI -> Group Code
        self._load_data()

    def _load_groups_data(self):
        """
        Lädt ESCO Skill Groups (skillGroups_de.csv).
        Erstellt die Mappe für die spätere Anreicherung der Skills (ESCO URI -> Group Code).
        """
        groups_path = os.path.join(self.data_path, "skillGroups_de.csv") #
        try:
            # Lade nur URI und Code
            df_groups = pd.read_csv(groups_path, encoding='utf-8', usecols=['conceptUri', 'code'])
            # Erstelle ein Dictionary: {conceptUri: code}
            self._group_map = df_groups.set_index('conceptUri')['code'].to_dict()
            print(f"✅ ESCO Skill Groups geladen: {len(self._group_map)} Einträge.")
        except FileNotFoundError:
            print(f"⚠️ FEHLER: {groups_path} nicht gefunden. Hierarchische Gruppierung ist deaktiviert.")
        except Exception as e:
            print(f"❌ Fehler beim Laden von Skill Groups: {e}")

    def _load_esco_data(self) -> List[Competence]:
        """
        Lädt die offiziellen ESCO-Kompetenzen (skills_de.csv).
        Reichert die Kompetenzen mit dem zuvor geladenen Gruppencode an.
        """
        skills_path = os.path.join(self.data_path, "skills_de.csv") #
        esco_list = []
        try:
            # Lade nur die relevanten Spalten
            df_esco = pd.read_csv(skills_path, encoding='utf-8', usecols=['preferredLabel', 'conceptUri', 'altLabels'])

            for index, row in df_esco.iterrows():
                uri = row['conceptUri']
                label = row['preferredLabel']

                if pd.isna(uri) or pd.isna(label):
                    continue

                # Hole den Gruppencode über die URI aus der Mappe
                group_code = self._group_map.get(uri)

                # AltLabels (Synonyme) aus dem pipe-separierten String extrahieren
                alt_labels_str = str(row['altLabels'])
                synonyms = [s.strip() for s in alt_labels_str.split('|') if s.strip()] if pd.notna(row['altLabels']) else []

                # Erstelle das Domain-Objekt
                esco_list.append(Competence(
                    preferred_label=label,
                    esco_uri=uri,
                    synonyms=synonyms,
                    group_code=group_code
                ))
            print(f"✅ ESCO-Skills geladen: {len(esco_list)} Einträge.")
            return esco_list
        except FileNotFoundError:
            print(f"⚠️ FEHLER: {skills_path} nicht gefunden. ESCO-Basis fehlt.")
            return []
        except Exception as e:
            print(f"❌ Fehler beim Laden der ESCO-Daten: {e}")
            return []

    def _load_custom_data(self) -> List[Competence]:
        """
          Lädt benutzerdefinierte (Future) Skills aus der JSON (custom_skills_extended.json).
          Diese sind KRITISCH für eine hohe Extraktionsrate von modernen Begriffen.
          """
        custom_path = self.custom_json_path #
        custom_list = []
        try:
            with open(custom_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                # Custom Skills haben keinen ESCO Group Code
                custom_list.append(Competence(
                    preferred_label=item['preferredLabel'],
                    esco_uri=item['escoUri'],
                    synonyms=item.get('synonyms', []),
                    group_code=None
                ))
            print(f"✅ Custom Skills geladen: {len(custom_list)} Einträge.")
            return custom_list
        except FileNotFoundError:
            print(f"⚠️ FEHLER: Custom Skills JSON nicht gefunden unter: {custom_path}. Verwende nur ESCO.")
            return []
        except Exception as e:
            print(f"❌ Fehler beim Laden der Custom Skills: {e}")
            return []

    def _load_data(self):
        """Führt das Laden beider Quellen zusammen."""
        self._load_groups_data()
        self._competences.extend(self._load_esco_data())
        self._competences.extend(self._load_custom_data())
        print(f"--- 🧠 Hybrid-Wissensbasis ist bereit: {len(self._competences)} Gesamt-Kompetenzen. ---")

    def get_all_competences(self) -> List[Competence]:
        return self._competences
