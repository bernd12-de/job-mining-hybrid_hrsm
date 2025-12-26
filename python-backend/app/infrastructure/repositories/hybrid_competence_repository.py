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

        # Indexes für schnelle Abfragen
        self.esco_data: Dict[str, Dict] = {}
        self.custom_domains: Dict[str, Dict] = {}
        self._fachbuch_skills: Set[str] = set()
        self._academia_skills: Set[str] = set()

        # Initial laden
        self._load_data()
        # Baue Index für schnellen Lookup
        self._build_esco_index()
        # Lade lokale Domänen (Ebene 4/5)
        self._load_local_domains_v2()
        # Sync für Legacy Sets (fachbuch / academia)
        self._sync_legacy_sets()
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

    # Backwards-compatibility: older callers expect get_all_labels()
    def get_all_labels(self) -> List[str]:
        return self.get_all_identifiable_labels()

    def get_level(self, term: str) -> int:
        """Determine level priority:
        5 = Academia (modulhandbuch), 4 = Fachbuch, 2/3 = ESCO, default = 2
        """
        if not term:
            return 2
        t = term.lower().strip()

        # 1) Academia (level 5)
        if t in self._academia_skills:
            return 5

        # 2) Fachbuch (level 4)
        if t in self._fachbuch_skills:
            return 4

        # 3) ESCO lookup
        if t in self.esco_data:
            try:
                return int(self.esco_data[t].get('level', 2))
            except Exception:
                return 2

        # 4) Heuristik: substring match against ESCO labels
        for k, v in self.esco_data.items():
            if t == k or t in k or k in t:
                try:
                    return int(v.get('level', 2))
                except Exception:
                    return 2

        # Fallback
        return 2

    def get_data_by_label(self, label: str) -> Dict:
        """Returns metadata dict for a given label if found in the repository."""
        if not label:
            return None

        label_l = label.lower().strip()
        # 1) direct index
        if label_l in self.esco_data:
            return self.esco_data[label_l]

        # 2) search _all_competences as fallback
        for comp in self._all_competences:
            try:
                if getattr(comp, 'preferred_label', '').lower() == label_l:
                    return {
                        'uri': getattr(comp, 'esco_uri', None),
                        'preferredLabel': getattr(comp, 'preferred_label', label),
                        'level': getattr(comp, 'level', 3),
                        'is_digital': getattr(comp, 'is_digital', False),
                        'source_domain': getattr(comp, 'source_domain', 'ESCO')
                    }
            except Exception:
                continue
        return None

    def _build_esco_index(self):
        """Builds `self.esco_data` dict from `self._all_competences` for fast lookups."""
        self.esco_data = {}
        for comp in self._all_competences:
            try:
                lbl = getattr(comp, 'preferred_label', None)
                if not lbl:
                    continue
                key = lbl.lower()
                self.esco_data[key] = {
                    'uri': getattr(comp, 'esco_uri', None),
                    'preferredLabel': lbl,
                    'level': getattr(comp, 'level', 2),
                    'is_digital': getattr(comp, 'is_digital', False),
                    'source_domain': getattr(comp, 'source_domain', 'ESCO')
                }
            except Exception:
                continue

    def _load_local_domains_v2(self):
        """Loads JSON domains from `data/job_domains` and populates `self.custom_domains`."""
        self.custom_domains = {}
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'job_domains')
        if not os.path.exists(base):
            return
        for fname in os.listdir(base):
            if not fname.endswith('.json'):
                continue
            path = os.path.join(base, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                domain_name = data.get('domain', os.path.splitext(fname)[0])
                self.custom_domains[domain_name] = data
            except Exception as e:
                print(f"⚠️ Fehler beim Laden der Domain {fname}: {e}")

    def _sync_legacy_sets(self):
        """Populate legacy sets for backward-compatible lookup (fachbuch / academia)."""
        self._fachbuch_skills = set()
        self._academia_skills = set()
        for domain, data in self.custom_domains.items():
            lvl = data.get('level', 2)
            for comp in data.get('competences', []):
                name = comp.get('name')
                if not name:
                    continue
                name_low = name.lower().strip()
                if lvl == 4:
                    self._fachbuch_skills.add(name_low)
                if lvl == 5:
                    self._academia_skills.add(name_low)

    def is_known(self, term: str) -> bool:
        """Check if a given term is known in ESCO or custom skills.
        This returns True for exact matches and for terms that are a meaningful
        substring of any known label (e.g. 'projektmanagement' -> 'Projektmanagement durchführen').
        """
        if not term:
            return False
        term_norm = term.lower().strip()
        # direct ESCO index
        if term_norm in self.esco_data:
            return True
        # custom domains names
        if term_norm in {n.lower() for n in self.custom_domains.keys()}:
            return True
        # heuristic substring match
        for lbl in self.get_all_skills():
            lbl_norm = lbl.lower()
            if term_norm == lbl_norm:
                return True
            if term_norm in lbl_norm:
                return True
        return False

    def is_blacklisted(self, term: str) -> bool:
        if not term:
            return False
        return term.lower().strip() in {t.lower() for t in self._blacklist}

    def is_digital_skill(self, term: str) -> bool:
        if not term:
            return False
        return self.esco_data.get(term.lower().strip(), {}).get('is_digital', False)
