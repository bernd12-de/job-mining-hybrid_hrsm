# domain/services/organization_service.py (NEU DOMAIN SERVICE)

import re
from typing import Dict, Optional
from infrastructure.clients.kotlin_rule_client import KotlinRuleClient

class OrganizationService:
    """
    Domain Service für die Branchen-Klassifizierung.
    Nutzt das DB-gestützte Regelwerk über den KotlinRuleClient.
    """

    def __init__(self, rule_client: KotlinRuleClient):
        # Lädt die Mappings beim Start einmalig in den Speicher
        self.industry_mappings: Dict[str, str] = rule_client.fetch_industry_mappings()

    def classify_industry(self, job_text: str, default_industry: str = "Sonstiges") -> str:
        """
        Klassifiziert die Branche anhand des gesamten Stellentextes mithilfe des Regelwerks.
        """
        text_lower = job_text.lower()

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


