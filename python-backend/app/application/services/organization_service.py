# domain/services/organization_service.py (NEU DOMAIN SERVICE)

import re
from typing import Dict
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient

class OrganizationService:
    """
    Domain Service für die Branchen-Klassifizierung.
    Nutzt das DB-gestützte Regelwerk über den KotlinRuleClient.
    """

    def __init__(self, rule_client: KotlinRuleClient):
        # Lädt die Mappings beim Start einmalig in den Speicher
        # 🚨 DER FIX: Du musst den übergebenen Client an 'self' binden!
        self.rule_client = rule_client

        try:
            # Jetzt existiert 'self.rule_client' und dieser Aufruf funktioniert:
            #self.industry_mappings = self.rule_client.fetch_industry_mappings()
            self.industry_mappings: Dict[str, str] = rule_client.fetch_industry_mappings()
            self.industry_keywords = self._load_mappings()
            print(f"✅ {len(self.industry_mappings)} Branchen-Regeln geladen.")
            print(f"✅ {len(self.industry_keywords)} Branchen-Regeln geladen.")
        except Exception as e:
            print(f"⚠️ Fehler bei Branchen-Mappings: {e}")
            self.industry_mappings = {} # Fallback




    def detect_industry(self, text: str) -> str:
        backup = self.classify_industry(text, default_industry="Sonstiges")
        if backup != "Sonstiges":
            return backup
        return self.classify_industry_neu(text)



    def classify_industry(self, job_text: str, default_industry: str = "Sonstiges") -> str:
        """
        Klassifiziert die Branche anhand des gesamten Stellentextes mithilfe des Regelwerks.
        """
        text_lower = job_text.lower()
        scores = {}

        for industry, pattern in self.industry_mappings.items():
            try:
                # Führt die Regex-Suche durch
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return industry
            except re.error:
                # Sollte nicht passieren, aber sichert die Robustheit gegen fehlerhafte Regex
                print(f"⚠️ Warnung: Ungültiges Regex-Muster für Branche '{industry}': {pattern}")
                continue

        return default_industry

    def classify_industry_neu(self, text: str) -> str:
        """Prüft den Text gegen die geladenen Keywords."""
        text_lower = text.lower()
        scores = {}

        for industry, pattern in self.industry_keywords.items():
            # Pattern ist z.B. "Bank|Versicherung"
            # Wir machen daraus eine RegEx-Suche
            try:
                hits = len(re.findall(f"({pattern})", text_lower, re.IGNORECASE))
                if hits > 0:
                    scores[industry] = hits
            except:
                continue

        if not scores:
            return "Unbekannt"

        # Gewinner ist die Branche mit den meisten Treffern
        return max(scores, key=scores.get)

    def _load_mappings(self) -> Dict[str, str]:
        """Holt Mappings von Kotlin (via Client)."""
        try:
            # Erwartet: {'IT': 'Software|Computer', 'Finance': 'Bank|Versicherung'}
            mappings = self.rule_client.fetch_industry_mappings()
            if mappings:
                print(f"✅ {len(mappings)} Branchen-Regeln geladen.")
                return mappings
        except Exception as e:
            print(f"⚠️ Fehler bei Branchen-Mappings: {e}")

        # Notfall-Fallback (falls Client auch versagt)
        return {
            'IT & Software': 'Software|Entwicklung|Cloud|IT|Data',
            'Finanzen': 'Bank|Versicherung|Finance'
        }


