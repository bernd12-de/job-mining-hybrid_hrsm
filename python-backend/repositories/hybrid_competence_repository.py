import json
import os
from typing import List, Dict, Set

from infrastructure.data.esco_skills import get_esco_target_labels, get_esco_mapping
from interfaces import ICompetenceRepository # Importiert ICompetenceRepository
from models import Competence # FIX: Importiert Competence aus models.py


# --- Hybrid Repository Implementierung ---
class HybridCompetenceRepository(ICompetenceRepository):

    # Pfad für Custom Skills (angenommen: relativ zu repositories/)
    CUSTOM_JSON_PATH = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'custom_skills_extended.json'
    )

    def __init__(self):
        self._esco_labels: Set[str] = set()
        self._custom_labels: Set[str] = set()
        self._all_competences: List[Competence] = []
        self._esco_mapping: Dict[str, str] = get_esco_mapping()

        self._load_data()

        # LOGGING (Bestätigt, dass die NEUEN CSVs geladen wurden)
        esco_count = len(self._esco_labels)
        custom_count = len(self._custom_labels)
        total_count = len(self._all_competences)

        print(f"✅ ESCO Skills geladen: {esco_count} Einträge.")
        print(f"✅ Custom Skills geladen: {custom_count} Einträge.")
        print(f"--- 🧠 Hybrid-Wissensbasis ist bereit: {total_count} Gesamt-Kompetenzen. ---")


    def _load_data(self):
        """Lädt alle Daten und befüllt die internen Strukturen."""

        # --- ESCO LADEN (FIX FÜR DATENQUALITÄT) ---
        esco_labels = get_esco_target_labels()
        self._esco_labels.update(esco_labels)

        for label in esco_labels:
            self._all_competences.append(Competence(preferred_label=label, esco_uri=f"esco/skill/TEMP_{label}"))


        # --- Custom Skills Laden ---
        try:
            with open(self.CUSTOM_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                comp = Competence(
                    preferred_label=item['preferredLabel'],
                    esco_uri=item['escoUri'],
                    synonyms=item.get('synonyms', []),
                    group_code=None
                )
                self._custom_labels.add(comp.preferred_label)
                self._all_competences.append(comp)

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"❌ Fehler beim Laden der Custom Skills: {e}")


    # --- Methoden des ICompetenceRepository Interfaces ---
    def get_all_skills(self) -> Set[str]:
        return self._esco_labels.union(self._custom_labels)

    def get_all_competences(self) -> List[Competence]:
        return self._all_competences

    def get_esco_only(self) -> Set[str]:
        return self._esco_labels

    def get_custom_only(self) -> Set[str]:
        return self._custom_labels

    def get_esco_mapping(self) -> Dict[str, str]:
        return self._esco_mapping
