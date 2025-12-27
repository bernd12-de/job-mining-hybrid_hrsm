import json
import os
from typing import List, Set, Dict, Optional, Any
from rapidfuzz import process, fuzz
import app.infrastructure.clients.kotlin_rule_client as clients
from tqdm import tqdm

class HybridCompetenceRepository:
    def __init__(self,
                 kotlin_api_url: str = "http://localhost:8080",
                 fachbuch_path: str = None,
                 academia_path: str = None,
                 rule_client = None):

        # Client Setup (SSoT) - NEU
        if rule_client:
            self.rule_client = rule_client
        else:
            self.rule_client = clients.KotlinRuleClient()

        # Daten-Container - ALT (Wichtig für Extractor!)
        # Wir brauchen ein Dictionary, keine Liste!
        # WICHTIG: Wir nutzen 'esco_skills' als Haupt-Speicher (Dictionary)
        # Damit ist main.py glücklich.
        self.esco_skills: Dict[str, Dict] = {}
        #self.custom_domains: Dict[str, Any] = {} #ist jetzt property

        # Legacy Sets (für Kompatibilität)
        self._fachbuch_skills: Set[str] = set()
        self._academia_skills: Set[str] = set()

        # Legacy Sets für schnelle Checks (optional)
        self.all_competences_set: Set[str] = set()
        self.digital_competences_set: Set[str] = set()

        # Startet den Ladevorgang
        self.load_all_data()


    # --- 👇 DER RETTER: DAS IST DER "HELPER", DEN DU WOLLTEST ---
    @property
    def esco_data(self):
        """
        Safety-Shim: Wenn alter Code 'repository.esco_data' aufruft,
        leiten wir es automatisch auf 'repository.esco_skills' um.
        """
        return self.esco_skills

    @property
    def custom_domains(self):
        """Safety-Shim für alte Domain-Aufrufe."""
        # Kombiniert die beiden neuen Dicts zu einem für alte Aufrufer
        combined = {}
        combined.update(self._academia_skills)
        combined.update(self._fachbuch_skills)
        return combined
    # ------------------------------------------------------------

    def load_all_data(self):
        """Verbindet NEU (Client) mit ALT (Datenstruktur)."""
        print("🔄 Lade Wissensbasis...")

        # 1. Daten vom Client holen (Das ist eine LISTE)
        raw_skills_list = self.rule_client.get_esco_full()
        try:
            # 2. KONVERTIERUNG (List -> Dict)
            # 2. Dictionary resetten
            # Das hat gefehlt! Wir wandeln die Liste in ein Dictionary um.
            self.esco_skills = {}
            count = 0

            if raw_skills_list:
                # HIER IST DIE MAGIE: tqdm() um die Liste wickeln
                # desc="Indiziere Skills" ist der Text links
                # unit=" sk" zeigt "it/s" (Items pro Sekunde)
                # Wir versuchen tqdm für den Ladebalken zu nutzen
                try:
                    from tqdm import tqdm
                    iterator = tqdm(raw_skills_list, desc="🚀 Indiziere Skills (Repo)", unit=" sk", ncols=100)
                except ImportError:
                    iterator = raw_skills_list


                for item in iterator:
                    # Der Client liefert: label, uri, is_digital, level
                    label = item.get('label') or item.get('preferredLabel') or item.get('esco_label')
                    if label:
                        # Speichern im Dictionary (Key = lower case)
                        # Lowercase Label als Key für schnelle Suche
                        self.esco_skills[label.lower()] = {
                            "uri": item.get('uri') or item.get("esco_uri"),
                            "is_digital": item.get('is_digital', False),
                            "level": item.get('level', 2),
                            "original_label": label
                        }
                        count += 1
                print(f"✅ {count} Skills erfolgreich in Such-Index (esco_skills) geladen.")
                print(f"✅ Such-Index mit {len(self.esco_skills)} Einträgen bereit.")
            else:
                print("⚠️ Warnung: Keine Daten vom RuleClient erhalten.")

            # 3. Lokale Erweiterungen laden
            self._load_local_domains_v2()

            # 4. Legacy Sets füllen
            self._sync_legacy_sets()

        except Exception as e:
            print(f"❌ Kritischer Fehler beim Laden der Daten: {e}")
            self.esco_skills = {} # Fallback auf leer, damit nichts crasht


    def _load_local_domains_v2(self):
        """Liest data/job_domains und füllt custom_domains."""
        path = "data/job_domains"
        JOB_DOMAINS_DIR = path
        # Sicherstellen, dass Verzeichnis existiert
        if not os.path.exists(JOB_DOMAINS_DIR):
            return

        if os.path.exists(path):
            for f in os.listdir(path):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(path, f), 'r', encoding='utf-8') as jf:
                            data = json.load(jf)
                            for comp in data.get("competences", []):
                                self.custom_domains[comp["name"]] = comp
                    except Exception as e:
                        print(f"⚠️ Fehler in {f}: {e}")

    def _sync_legacy_sets(self):
        for name, comp in self.custom_domains.items():
            lvl = comp.get("level")
            if lvl == 4: self._fachbuch_skills.add(name.lower())
            if lvl == 5: self._academia_skills.add(name.lower())

    # --- WICHTIG: Die Schnittstelle für den Extractor ---

    def get_all_identifiable_labels(self) -> List[str]:
        """Hier gab es den Absturz. Jetzt ist es ein Dict, also geht .keys() wieder!"""
        return list(self.esco_data.keys()) + list(self.custom_domains.keys())

    def get_data_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        """Fuzzy Suche im Dictionary."""
        choices = list(self.esco_data.keys())
        if not choices: return None
        match = process.extractOne(label.lower(), choices, scorer=fuzz.token_set_ratio)
        if match and match[1] >= 95:
            return self.esco_data[match[0]]
        return None

    def get_level(self, term: str) -> int:
        t = term.lower()
        if t in self.esco_data: return self.esco_data[t]["level"]
        if t in self._academia_skills: return 5
        if t in self._fachbuch_skills: return 4
        return 1

    def is_digital_skill(self, term: str) -> bool:
        return self.esco_data.get(term.lower(), {}).get('is_digital', False)

    # Diese Methode muss in der Klasse existieren:
    def _load_dynamic_blacklist(self):
        """Lädt Blacklist via Client (mit Fallback)."""
        try:
            # Der Client kümmert sich um API-Call und Fallback-Datei
            blacklisted_terms = self.rule_client.fetch_blacklist()
            if blacklisted_terms:
                self._blacklist.update(blacklisted_terms)
                print(f"✅ Blacklist geladen: {len(self._blacklist)} Begriffe.")
            else:
                print("⚠️ Warnung: Leere Blacklist vom Client erhalten.")
        except Exception as e:
            print(f"❌ Fehler beim Laden der Blacklist: {e}")

    # Interface Methode (wird vom Extractor genutzt)
    def get_blacklist(self) -> Set[str]:
        return self._blacklist
