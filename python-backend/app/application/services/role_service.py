# domain/services/role_service.py (NEU DOMAIN SERVICE)

import re
from typing import Dict
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient

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

    def _load_mappings(self) -> Dict[str, str]:
        try:
            mappings = self.rule_client.fetch_role_mappings()
            if mappings:
                print(f"✅ {len(mappings)} Rollen-Regeln geladen.")
                return mappings
        except Exception as e:
            print(f"⚠️ Fehler bei Rollen-Mappings: {e}")

        return {
            'Software-Entwicklung': 'Entwickler|Developer|Engineer|Programmierer',
            'Management': 'Leiter|Head of|Manager|Lead'
        }

    def classify_roleNEU(self, job_text: str, job_title: str) -> str:
        """Klassifiziert basierend auf Titel (hoch gewichtet) und Text."""
        full_text = (job_title + " " + job_text).lower()

        best_role = "Unbekannt"
        max_score = 0

        for role, pattern in self.role_mappings.items():
            score = len(re.findall(f"({pattern})", full_text, re.IGNORECASE))

            # Bonus, wenn das Keyword im Titel steht
            if re.search(f"({pattern})", job_title.lower(), re.IGNORECASE):
                score *= 2

            if score > max_score:
                max_score = score
                best_role = role

        return best_role

