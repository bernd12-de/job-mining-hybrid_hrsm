# infrastructure/clients/kotlin_rule_client.py
import pandas as pd
import requests
import os
from typing import Set, List, Dict
import json
from app.core.constants import DEFAULT_KOTLIN_URL

# Die URL des Kotlin-Backends wird aus den Umgebungsvariablen gelesen
# (Z.B. KOTLIN_API_BASE_URL=http://kotlin-api:8080 oder http://localhost:8080)
#KOTLIN_API_BASE_URL = os.environ.get("KOTLIN_API_BASE_URL", "http://localhost:8080")


# ZENTRALISIERUNG: Wir nutzen die Konstante aus deiner constants.py
# Falls der Import fehlschlägt (z.B. bei Einzeltests), nutzen wir einen lokalen Fallback.
try:
    from app.core.constants import DEFAULT_KOTLIN_URL
except ImportError:
    DEFAULT_KOTLIN_URL = os.environ.get("KOTLIN_API_URL", "http://localhost:8080")

class KotlinRuleClient:
    """
    Adapter (Client) für die Abfrage von Domänenregeln
    (Blacklist, Mappings) vom Kotlin DomainRuleService.
    """

    def __init__(self, base_url=None):
        # 1. URL-Logik: Parameter > Environment (via Constant) > Hardcoded Default
        self.base_url = base_url if base_url else DEFAULT_KOTLIN_URL

        self.fallback_path = "data/fallback_rules"
        self.esco_source = "data/esco"
        print(f"🔗 KotlinRuleClient initialisiert. Basis-URL: {self.base_url}")

        # Sicherstellen, dass der Fallback-Ordner existiert
        os.makedirs(self.fallback_path, exist_ok=True)
        print(f"🔗 KotlinRuleClient initialisiert. Basis-URL: {self.base_url}")

    def get_esco_full(self):
        """Holt ESCO-Skills und übersetzt 'esco_label' -> 'label'."""
        endpoint = f"{self.base_url}/api/v1/rules/esco-full"

        try:
            print(f"🔄 Lade ESCO-Daten von: {endpoint}")
            # Versuche Kotlin zu erreichen (Timeout nach 2 Sek, damit es nicht hängt)
            #alt url response = requests.get(f"{self.base_url}/esco-full", timeout=2)
            # Timeout auf 15s erhöht für große Datenmengen im Docker
            response = requests.get(endpoint, timeout=15)
            response.raise_for_status()

            raw_data = response.json()

            # 2. DATA MAPPING: Kotlin sendet 'esco_label', Python braucht 'label'
            normalized_data = []
            for item in raw_data:
                normalized_data.append({
                    "label": item.get("esco_label") or item.get("label"),
                    "uri": item.get("esco_uri") or item.get("uri"),
                    "is_digital": item.get("is_digital", False),
                    "level": item.get("level", 2)
                })

            print(f"✅ {len(normalized_data)} Skills geladen & normalisiert.")
            return normalized_data

        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            target = os.path.join(self.fallback_path, "esco_fallback.json")
            # Falls die JSON fehlt, baue sie jetzt aus den CSVs in data/esco
            if not os.path.exists(target):
                self._generate_fallback_from_csv(target)

            print("⚠️ STANDALONE: Kotlin offline. Lade ESCO-Daten aus lokalem Fallback.")
            return self._load_fallback("esco_fallback.json")

    def fetch_blacklist(self) -> Set[str]:
        """Holt die Blacklist."""
        endpoint = f"{self.base_url}/api/v1/rules/blacklist"
        # alt path = os.path.join(self.fallback_path, filename)
        filename = "blacklist_fallback.json"

        try:
            response = requests.get(endpoint, timeout=9)
            response.raise_for_status()
            data = response.json()
            # Cache update
            self._save_to_json(filename, data)
            return set(data)
        except Exception as e:
            print(f"❌ API-Fehler bei Blacklist: {e}")
            # Nutzt _get_static_fallback_blacklist_as_list zur Generierung der Datei, falls sie fehlt
            data = self._load_or_create_fallback(filename, generation_method=self._get_static_fallback_blacklist_as_list)
            return set(data) if data else set()

    def _generate_fallback_from_csv(self, target_path):
        """Konvertiert die großen CSVs in ein kleines, schnelles JSON."""
        print(f"🔄 Generiere Fallback aus CSV in {self.esco_source}...")
        os.makedirs(self.fallback_path, exist_ok=True)
        fallback_dict = {}

        csv_file = os.path.join(self.esco_source, "skills.csv")
        if os.path.exists(csv_file):
            # Wir lesen nur die nötigen Spalten, um Speicher zu sparen
            df = pd.read_csv(csv_file, usecols=['preferredLabel', 'conceptUri'])
            for _, row in df.iterrows():
                label = str(row['preferredLabel']).lower()
                fallback_dict[label] = row['conceptUri']

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(fallback_dict, f, ensure_ascii=False)

    def fetch_blacklist(self) -> Set[str]:
        """
        Ruft den Kotlin-Endpunkt ab und gibt die aktive Blacklist als Set zurück.
        """
        endpoint = f"{self.base_url}/api/v1/rules/blacklist"

        try:
            response = requests.get(endpoint, timeout=5) # 5 Sekunden Timeout
            response.raise_for_status() # Löst HTTPError für 4xx/5xx Statusse aus

            # Kotlin gibt eine JSON-Liste von Strings zurück
            blacklist_list: List[str] = response.json()

            # Konvertierung in ein Set für schnellen Lookup im Extractor
            return set(blacklist_list)

        except requests.exceptions.Timeout:
            print(f"❌ Fehler: Timeout beim Abruf der Blacklist von {endpoint}")
            # KRITISCHE ENTSCHEIDUNG: Bei einem Fehler MUSS die Blacklist
            # ausfallen, um Rauschen zu vermeiden. Wir laden die statische Fallback-Liste.
            return self._get_static_fallback_blacklist()

        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abruf der Blacklist von Kotlin: {e}")
            # Kritischer Ausfall: Lade Fallback
            return self._get_static_fallback_blacklist()

    # In kotlin_rule_client.py ergänzen
    def fetch_full_esco(self) -> List[Dict]:
        endpoint = f"{self.base_url}/api/v1/rules/esco-full"
        response = requests.get(endpoint, timeout=30)
        return response.json()

    def fetch_role_mappings(self) -> Dict[str, str]:
        """
        Ruft die DB-gestützten Rollen-Mappings vom Kotlin-Endpunkt ab.
        """
        endpoint = f"{self.base_url}/api/v1/rules/role-mappings"

        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()

            mappings: Dict[str, str] = response.json()
            return mappings

        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abruf der Rollen-Mappings von Kotlin: {e}")
            # KRITISCHE ENTSCHEIDUNG: Fallback für Rollen-Mappings
            return self._get_static_fallback_role_mappings()

    def _get_static_fallback_blacklist(self) -> Set[str]:
        """
        Statischer Fallback: Falls die DB/API nicht erreichbar ist, nutzen wir die
        bekannte Version, um Rauschen zu vermeiden. (Resilienz-Fallback)
        """
        print("⚠️ FALLBACK AKTIVIERT: Blacklist wird statisch geladen (DB/API nicht erreichbar).")
        return {
            "kenntnisse", "fähigkeiten", "kommunikation", "deutsch", "englisch",
            "r", "bau", "ski", "sport", "medien", "wissenschaft", "erfahrung",
            "agil", "strategie", "prozess", "management", "analyse", "projektleitung",
            "kunden", "lösung", "team", "technik", "bereich", "verantwortung übernehmen",
            "beratung", "dienstleistungen", "informatik", "digitalisierung",
            "prägen", "datenschutz", "ethik", "gesundheit", "kommunizieren", "agiles"
        }

    # NEU: Resilienz-Fallback für Branchen-Mappings
    def _get_static_fallback_industry_mappings(self) -> Dict[str, str]:
        print("⚠️ FALLBACK AKTIVIERT: Branchen-Mappings werden statisch geladen.")
        # Diese statischen Mappings ersetzen die Logik aus organization_extractor.py
        return {
            'Informationstechnologie & Software': 'IT|Software|Entwicklung|DevOps|Cloud|Informatik|Digitalisierung',
            'Finanzen & Versicherungen': 'Finanz|Bank|Versicherung|Aktie|Treasury|Bilanz',
            'Automobil & Maschinenbau': 'Automobil|Maschinenbau|Fertigung|Produktion|Anlage|Konstruktion',
            'Gesundheit & Soziales': 'Klinik|Pflege|Sozial|Heim|Therapie|Krankenhaus',
            'Handel & Logistik': 'Handel|Logistik|Einzelhandel|Lager|Supply Chain',
            'Unbekannt/Generell': 'Marketing|Vertrieb|Verwaltung|Assistenz'
        }

    # NEU: Resilienz-Fallback für Rollen-Mappings
    def _get_static_fallback_role_mappings(self) -> Dict[str, str]:
        print("⚠️ FALLBACK AKTIVIERT: Rollen-Mappings werden statisch geladen.")
        return {
            'Software-Entwicklung': 'Entwickler|Developer|Programmierer|Coding|Frontend|Backend',
            'Data & Analytics': 'Data Scientist|Analyst|BI|Statistik',
            'Projektmanagement': 'Projektleiter|Scrum Master|Product Owner',
            'Führungskraft/Management': 'Leiter|Manager|Head of',
            'Unbekannt/Generell': 'Assistent|Kauffrau|Admin'
        }

    def fetch_industry_mappings(self) -> Dict[str, str]:
        """
        Ruft die DB-gestützten Branchen-Mappings vom Kotlin-Endpunkt ab.
        (Entspricht der V3-Migration)
        """
        # Der Endpunkt muss zu dem RuleType passen, der in V3 eingefügt wurde
        endpoint = f"{self.base_url}/api/v1/rules/industry-mappings"

        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()

            mappings: Dict[str, str] = response.json()
            return mappings

        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim Abruf der Branchen-Mappings von Kotlin: {e}")
            # KRITISCHE ENTSCHEIDUNG: Fallback für Branchen-Mappings
            return self._get_static_fallback_industry_mappings() # Die Fallback-Methode existiert bereits


