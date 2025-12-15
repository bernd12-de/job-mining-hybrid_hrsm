# domain/services/role_service.py (NEU DOMAIN SERVICE)

import re
from typing import Dict, Optional
from infrastructure.clients.kotlin_rule_client import KotlinRuleClient

class RoleService:
    """
    Domain Service für die Klassifizierung der Berufsrolle.
    Nutzt das DB-gestützte Regelwerk (V4-Migration) über den KotlinRuleClient.
    """

    def __init__(self, rule_client: KotlinRuleClient):
        # Lädt die Mappings beim Start einmalig in den Speicher
        self.role_mappings: Dict[str, str] = rule_client.fetch_role_mappings()

    def classify_role(self, job_text: str, job_title: str, default_role: str = "Unbekannt") -> str:
        """
        Klassifiziert die Rolle anhand des Jobtitels und des gesamten Stellentextes.
        Die Suche wird zuerst im Titel und dann im Text durchgeführt, um Präzision zu erhöhen.
        """
        search_target = f"{job_title.lower()} {job_text.lower()}"

        for role, pattern in self.role_mappings.items():
            try:
                # Führt die Regex-Suche über Titel und Text durch
                if re.search(pattern, search_target, re.IGNORECASE):
                    return role
            except re.error:
                print(f"⚠️ Warnung: Ungültiges Regex-Muster für Rolle '{role}': {pattern}")
                continue

        return default_role
