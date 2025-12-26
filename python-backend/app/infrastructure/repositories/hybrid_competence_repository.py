import json
import os
import requests
from typing import List, Dict, Set

# Imports
from app.interfaces.interfaces import ICompetenceRepository
from app.domain.models import Competence
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient

class HybridCompetenceRepository(ICompetenceRepository):
    # Pfad relativ zum Projekt-Root
    CUSTOM_JSON_PATH = "data/custom_skills_extended.json"

    def __init__(self, rule_client: KotlinRuleClient):
        self._esco_labels: Set[str] = set()
        self._custom_labels: Set[str] = set()
        self._all_competences: List[Competence] = []
        self._esco_mapping: Dict[str, str] = {}
        self._blacklist: Set[str] = set()

        self.rule_client = rule_client

        # Initial laden
        self._load_data()
        self._load_custom_skills()
        self._load_dynamic_blacklist()

    def _load_data(self):
        """Holt Daten von Kotlin. FIX: Tolerant gegen fehlende Keys."""
        try:
            # URL holen oder Default
            base_url = getattr(self.rule_client, 'base_url', 'http://kotlin-api:8080')
            endpoint = f"{base_url}/api/v1/rules/esco-full"

            print(f"📡 Lade ESCO-Daten von {endpoint}...")
            response = requests.get(endpoint, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if not data:
                    print("⚠️ Kotlin API antwortet mit leerer Liste.")
                    return

                # Debug: Was schickt Kotlin wirklich?
                first = data[0] if isinstance(data, list) and len(data) > 0 else {}
                # print(f"👀 DEBUG KEYS: {list(first.keys())}")

                count = 0
                for item in data:
                    # FIX: .get() verhindert den Crash ('preferredLabel')
                    lbl = item.get('preferredLabel') or item.get('preferred_label') or item.get('term') or item.get('label')
                    uri = item.get('escoUri') or item.get('esco_uri') or item.get('uri') or f"unknown/{count}"

                    if lbl:
                        self._esco_labels.add(lbl)
                        self._all_competences.append(Competence(
                            preferred_label=lbl,
                            esco_uri=uri
                        ))
                        count += 1

                print(f"✅ {count} Skills erfolgreich von Kotlin geladen.")
            else:
                print(f"⚠️ Kotlin API Fehler: {response.status_code}")

        except Exception as e:
            print(f"❌ Fehler beim Laden der ESCO-Daten: {e}")

    def _load_custom_skills(self):
        if os.path.exists(self.CUSTOM_JSON_PATH):
            try:
                with open(self.CUSTOM_JSON_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        # FIX: Auch hier .get() nutzen
                        lbl = item.get('preferredLabel') or item.get('label')
                        if lbl:
                            self._custom_labels.add(lbl)
                            self._all_competences.append(Competence(
                                preferred_label=lbl,
                                esco_uri=item.get('escoUri', 'custom')
                            ))
            except Exception as e:
                print(f"⚠️ Custom Skills Fehler: {e}")

    def _load_dynamic_blacklist(self):
        try:
            self._blacklist = self.rule_client.fetch_blacklist()
        except:
            self._blacklist = set()

    # Interface Implementierung
    def get_all_skills(self) -> Set[str]:
        return self._esco_labels.union(self._custom_labels)

    def get_all_competences(self) -> List[Competence]:
        return self._all_competences

    def get_esco_mapping(self) -> Dict[str, str]:
        return self._esco_mapping

    def get_all_identifiable_labels(self) -> List[str]:
        return list(self.get_all_skills())

    def get_level(self, term: str) -> int:
        return 3

    def is_digital_skill(self, term: str) -> bool:
        return False
