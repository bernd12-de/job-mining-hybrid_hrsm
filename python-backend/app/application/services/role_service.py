# domain/services/role_service.py (NEU DOMAIN SERVICE)

import json
import re
from pathlib import Path
from typing import Dict
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient

class RoleService:
    """
    Domain Service für die Klassifizierung der Berufsrolle.
    Nutzt das DB-gestützte Regelwerk (V4-Migration) über den KotlinRuleClient.
    """

    def __init__(self, rule_client: KotlinRuleClient):
        # Lädt die Mappings beim Start einmalig in den Speicher
        self.rule_client = rule_client  # Speichere Client für Recovery bei Fehlern
        try:
            primary = rule_client.fetch_role_mappings()
        except Exception:
            primary = {}

        self.role_mappings: Dict[str, str] = primary or {}
        self.fallback_role_mappings: Dict[str, str] = self._load_fallback_mappings()

        # Sicherheit: Garantiere, dass role_mappings nie leer ist
        if not self.role_mappings:
            self.role_mappings = self.fallback_role_mappings or {
                'Entwicklung': 'Developer|Engineer|Programmierer|Developer',
                'Management': 'Leiter|Head of|Manager|Lead|Management'
            }

        # ✅ BEST PRACTICE: Spezifische IT-Rollen Pattern-Matching
        self._setup_best_practice_patterns()

    def classify_role(self, job_text: str, job_title: str, default_role: str = "Unbekannt") -> str:
        """
        Klassifiziert die Rolle anhand des Jobtitels und des gesamten Stellentextes.

        ✅ BEST PRACTICE: Zwei-Stufen-Ansatz:
        1. Spezifische IT-Rollen (Frontend/Backend/Fullstack/DevOps)
        2. Fallback: DB-Regeln

        Returns:
            Spezifische Rolle (z.B. "Frontend Developer") oder Generic
        """
        search_target = f"{job_title} {job_text}".lower()

        # ✅ STUFE 1: Best Practice Pattern-Matching (spezifische IT-Rollen)
        best_practice_role = self._classify_with_best_practice(search_target)
        if best_practice_role != "Sonstige Rolle":
            return best_practice_role

        # STUFE 2: DB-Regeln (Legacy)
        direct = self._match_role_patterns(self.role_mappings, search_target)
        if direct:
            return direct

        # STUFE 3: Fallback-Mappings
        fallback = self._match_role_patterns(self.fallback_role_mappings, search_target)
        if fallback:
            return fallback

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

    def _match_role_patterns(self, patterns: Dict[str, str], search_target: str) -> str:
        for role, pattern in patterns.items():
            try:
                if re.search(pattern, search_target, re.IGNORECASE):
                    return role
            except re.error:
                print(f"⚠️ Warnung: Ungültiges Regex-Muster für Rolle '{role}': {pattern}")
                continue
        return ""

    def _load_fallback_mappings(self) -> Dict[str, str]:
        """Lädt lokale Fallback-Regeln aus data/fallback_rules/role_mappings_fallback.json."""
        try:
            base_dir = Path(__file__).resolve().parents[3]
            json_path = base_dir / "data" / "fallback_rules" / "role_mappings_fallback.json"
            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            print(f"⚠️ Konnte Fallback-Rollen nicht laden: {e}")
        return {}

    # ═══════════════════════════════════════════════════════════════════
    # BEST PRACTICE: Spezifische IT-Rollen Pattern-Matching
    # ═══════════════════════════════════════════════════════════════════

    def _setup_best_practice_patterns(self):
        """Setup spezifische IT-Rollen Patterns"""
        self.IT_ROLE_PATTERNS = {
            # Priorität 1: Fullstack (wenn beide Skills)
            "Fullstack Developer": [
                r"\bfullstack|full[\s-]?stack\b",
                r"\bfrontend.*backend|backend.*frontend\b",
                r"\bmern|mean|mevn\b",
            ],
            # Priorität 2: Frontend
            "Frontend Developer": [
                r"\bfrontend|front[\s-]?end\b",
                r"\breact|vue|angular|svelte\b",
                r"\bhtml|css|javascript.*frontend\b",
            ],
            # Priorität 3: Backend
            "Backend Developer": [
                r"\bbackend|back[\s-]?end\b",
                r"\bspring|django|flask|express\b",
                r"\bapi|rest|graphql|microservice\b",
                r"\bdatabase|sql|postgres\b",
            ],
            # Priorität 4: DevOps
            "DevOps Engineer": [
                r"\bdevops|sre\b",
                r"\bdocker|kubernetes|k8s\b",
                r"\bci/cd|jenkins|terraform\b",
            ],
            # Priorität 5: Mobile
            "Mobile Developer": [
                r"\bmobile|app[\s-]?developer\b",
                r"\bios|android|swift|kotlin\b",
                r"\breact[\s-]?native|flutter\b",
            ],
        }

    def _classify_with_best_practice(self, text: str) -> str:
        """
        Klassifiziert mit spezifischen IT-Rollen Patterns

        Returns:
            Spezifische Rolle oder "Sonstige Rolle"
        """
        for role, patterns in self.IT_ROLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return role

        # Fallback: Generic Software Engineer
        if re.search(r"\bsoftware|developer|engineer|entwickler\b", text, re.IGNORECASE):
            return "Software Engineer"

        return "Sonstige Rolle"

