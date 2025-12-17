# repositories/hybrid_competence_repository.py

import json
import os
import requests  # 🚨 FIX: Behebt 'Unresolved reference requests'
from typing import List, Dict, Set
from interfaces import ICompetenceRepository
from models import Competence

class HybridCompetenceRepository(ICompetenceRepository):
    # Pfad für Custom Skills bleibt erhalten
    CUSTOM_JSON_PATH = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'custom_skills_extended.json'
    )

    def __init__(self, rule_client):
        self._esco_labels: Set[str] = set()
        self._custom_labels: Set[str] = set()
        self._all_competences: List[Competence] = []
        self._esco_mapping: Dict[str, str] = {}
        self._blacklist: Set[str] = set()
        self.rule_client = rule_client

        # 1. Daten-Abgleich mit Kotlin (SSoT)
        self._load_data()

        # 2. Lokale Custom-Erweiterungen (für Phase 3)
        self._load_custom_skills()

        # 3. Blacklist befüllen
        self._load_dynamic_blacklist()

    def _load_data(self):
        """
        Holt die 31.655 Skills direkt von der Kotlin-API.
        Löst das Problem der Diskrepanz (18k vs 31k).
        """
        try:
            # Nutzt den neuen SSoT-Endpunkt in Kotlin
            endpoint = f"{self.rule_client.base_url}/api/v1/rules/esco-full"
            print(f"🔄 SSoT-Sync: Rufe 31.655 Begriffe von {endpoint} ab...")

            response = requests.get(endpoint, timeout=20)
            response.raise_for_status()
            esco_data = response.json()

            for item in esco_data:
                label = item['esco_label']
                uri = item['esco_uri']
                group = item.get('esco_group_code')

                # In Sets und Listen für den Extractor speichern
                self._esco_labels.add(label)
                self._esco_mapping[label.lower()] = label
                self._all_competences.append(Competence(
                    preferred_label=label,
                    esco_uri=uri,
                    group_code=group
                ))
            print(f"✅ SSoT-Erfolg: {len(self._all_competences)} Skills von Kotlin übernommen.")

        except Exception as e:
            print(f"❌ SSoT-Verbindungsfehler: {e}. Prüfe ob das Kotlin-Backend läuft!")

    def _load_dynamic_blacklist(self):
        """Lädt die Blacklist-Regeln aus der Kotlin-DB."""
        try:
            kotlin_rules = self.rule_client.fetch_blacklist()
            if kotlin_rules:
                self._blacklist.update(kotlin_rules)
                print(f"✅ {len(kotlin_rules)} Blacklist-Begriffe aus DB geladen.")
        except Exception as e:
            print(f"⚠️ Warnung: Konnte dynamische Blacklist nicht laden: {e}")

    def _load_custom_skills(self):
        """Lädt zusätzliche, nicht in ESCO enthaltene Skills aus lokaler JSON."""
        if os.path.exists(self.CUSTOM_JSON_PATH):
            try:
                with open(self.CUSTOM_JSON_PATH, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                    for item in custom_data:
                        label = item['preferredLabel']
                        self._custom_labels.add(label)
                        self._all_competences.append(Competence(
                            preferred_label=label,
                            esco_uri=item.get('escoUri', 'custom')
                        ))
            except Exception as e:
                print(f"⚠️ Fehler beim Laden der Custom-Skills: {e}")

    # --- Interface Methoden ---
    def get_all_skills(self) -> Set[str]:
        return self._esco_labels.union(self._custom_labels)

    def get_all_competences(self) -> List[Competence]:
        return self._all_competences

    def get_esco_mapping(self) -> Dict[str, str]:
        return self._esco_mapping

    def get_blacklist(self) -> Set[str]:
        return self._blacklist

    # In hybrid_competence_repository.py

    def get_esco_only(self) -> Set[str]:
        # Da wir SSoT nutzen, sind das alle unsere ESCO Labels
        return self._esco_labels

    def get_custom_only(self) -> Set[str]:
        # Das sind unsere lokalen Erweiterungen
        return self._custom_labels
