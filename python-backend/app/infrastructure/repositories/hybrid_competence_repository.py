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

    def __init__(self, rule_client: KotlinRuleClient = None, fachbuch_path: str = None, academia_path: str = None):
        # Backwards-Compatibility: Manche Tests/Clients übergeben 'fachbuch_path' & 'academia_path'
        self._esco_labels: Set[str] = set()
        self._custom_labels: Set[str] = set()
        self._all_competences: List[Competence] = []
        self._esco_mapping: Dict[str, str] = {}
        self._blacklist: Set[str] = set()

        # Falls nur positional args verwendet wurden (legacy), akzeptieren wir das auch
        if isinstance(rule_client, str) and fachbuch_path is None:
            # Ein simpler Fallback: erstes Argument war wahrscheinlich pfad, kein RuleClient
            fachbuch_path = rule_client
            rule_client = None

        self.rule_client = rule_client
        self.fachbuch_path = fachbuch_path
        self.academia_path = academia_path

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
            print(f"   -> HTTP-Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as e:
                    print(f"   ⚠️ Fehler beim Parsen der JSON-Antwort: {e}")
                    return

                print(f"   -> Response-Type: {type(data)}; Länge: {len(data) if hasattr(data, '__len__') else 'unknown'}")

                if not data:
                    print("⚠️ Kotlin API antwortet mit leerer Liste.")
                    return

                # Debug: Was schickt Kotlin wirklich?
                first = data[0] if isinstance(data, list) and len(data) > 0 else {}
                print(f"👀 DEBUG KEYS: {list(first.keys())}")
                print(f"👀 DEBUG SAMPLE: {first}")

                count = 0
                for item in data:
                    # FIX: .get() verhindert den Crash ('preferredLabel')
                    lbl = (
                        item.get('preferredLabel') or
                        item.get('preferred_label') or
                        item.get('original_term') or
                        item.get('esco_label') or
                        item.get('term') or
                        item.get('label')
                    )

                    uri = (
                        item.get('escoUri') or
                        item.get('esco_uri') or
                        item.get('uri') or
                        item.get('conceptUri') or
                        f"unknown/{count}"
                    )

                    if lbl:
                        lbl = lbl.strip()
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
            # Fallback: Versuche lokale ESCO CSV-Dateien zu laden
            try:
                print("⚠️ Versuche lokale ESCO CSV-Dateien zu laden...")
                self._load_data_from_local_esco()
            except Exception as le:
                print(f"❌ Lokales Laden fehlgeschlagen: {le}")

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

    def _load_data_from_local_esco(self):
        """Lädt ESCO-Daten aus lokalen CSV-Dateien im Ordner `data/esco` als Fallback.
        Erwartet Spalten: preferredLabel, conceptUri oder conceptUri/skillType
        """
        esco_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'esco')
        skills_file = os.path.join(esco_folder, 'skills_de.csv')
        if not os.path.exists(skills_file):
            print("⚠️ Lokale ESCO-Datei nicht gefunden: skills_de.csv")
            return

        added = 0
        import csv
        with open(skills_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lbl = row.get('preferredLabel') or row.get('preferred_label') or row.get('preferredlabel')
                uri = row.get('conceptUri') or row.get('concept_uri') or row.get('concepturi')
                if lbl:
                    self._esco_labels.add(lbl)
                    self._all_competences.append(Competence(preferred_label=lbl, esco_uri=uri or f"local/{added}"))
                    added += 1
        print(f"✅ Lokaler ESCO-Fallback: {added} Begriffe geladen.")

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
