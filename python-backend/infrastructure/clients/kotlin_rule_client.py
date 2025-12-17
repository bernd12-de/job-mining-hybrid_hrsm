# infrastructure/clients/kotlin_rule_client.py

import requests
import os
from typing import Set, List, Dict
import json

# Die URL des Kotlin-Backends wird aus den Umgebungsvariablen gelesen
# (Z.B. KOTLIN_API_BASE_URL=http://kotlin-api:8080 oder http://localhost:8080)
KOTLIN_API_BASE_URL = os.environ.get("KOTLIN_API_BASE_URL", "http://localhost:8080")

class KotlinRuleClient:
    """
    Adapter (Client) für die Abfrage von Domänenregeln
    (Blacklist, Mappings) vom Kotlin DomainRuleService.
    """

    def __init__(self):
        self.base_url = KOTLIN_API_BASE_URL
        print(f"🔗 KotlinRuleClient initialisiert. Basis-URL: {self.base_url}")

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


