# test_competence_extractor.py
import pytest
from unittest.mock import MagicMock, patch

# Annahme: Der Extractor liegt unter:
# python-backend.infrastructure.nlp
from infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor

# =========================================================
# 🛠️ Fixtures und Setup
# =========================================================

@pytest.fixture
def mock_esco_service():
    """Mock-Objekt für den ESCO-Service, der die Daten liefert."""
    mock = MagicMock()

    # Simuliere die Datenbasis, die der ESCO-Service laden würde:

    # 1. ESCO Label -> (URI, ID, Group)
    mock.get_esco_uri_and_id.side_effect = lambda label: {
        "Projektmanagement durchführen": ("http://esco/uri/1", "ID_1", "G_A"),
        "Datenbanken verwalten": ("http://esco/uri/2", "ID_2", "G_B"),
        "Kunden beraten": ("http://esco/uri/3", "ID_3", "G_C"),
        "UX-Testing durchführen": ("http://esco/uri/4", "ID_4", "G_D"),
        "Software entwickeln": ("http://esco/uri/5", "ID_5", "G_E"),
    }.get(label, (None, None, None)) # Rückgabe: None, None, None, falls Label unbekannt

    # 2. Custom Mappings (z.B. Jira -> Projektmanagement durchführen)
    mock.get_esco_mapping.return_value = {
        "jira": "Projektmanagement durchführen",
        "scrum": "SCRUM anwenden",
        "nosql": "Datenbanken verwalten",
        # Custom-Mapping, das NICHT in den offiziellen ESCO-Labels ist:
        "design thinking": "Design-Thinking-Methoden anwenden"
    }

    # 3. Alle Ziel-Labels (für den Phrase Matcher)
    mock.get_esco_target_labels.return_value = [
        "Projektmanagement durchführen",
        "Datenbanken verwalten",
        "Kunden beraten",
        "UX-Testing durchführen",
        "Software entwickeln",
        "SCRUM anwenden",
        "Design-Thinking-Methoden anwenden"
    ]

    return mock


@pytest.fixture
def mock_domain_rule_service():
    """Mock-Objekt für den Domain-Rule-Service (liefert Blacklist)."""
    mock = MagicMock()
    # Die Blacklist stammt aus der Kotlin-DB (Flyway V2)
    mock.get_active_blacklist_keys.return_value = [
        "kenntnisse",
        "fähigkeiten",
        "kommunikation",
        "erfahrung",
        "agil",
        "management",
    ]
    return mock


@pytest.fixture
# Stellt sicher, dass der Extractor die Mocks verwendet (Dependency Injection)
def extractor(mock_esco_service, mock_domain_rule_service):
    """Instanz des Extractor-Service mit gemockten Abhängigkeiten."""
    # Der Extractor muss initialisiert werden, um die Spacy-Pipeline zu laden.
    return SpaCyCompetenceExtractor(
        esco_service=mock_esco_service,
        domain_rule_service=mock_domain_rule_service
    )

# =========================================================
# 🧪 Testfälle
# =========================================================

class TestCompetenceExtractor:

    def test_01_direct_phrase_match(self, extractor):
        """Testet den High-Precision Pass 1: Direkter Phrase Match."""
        text = "Wir suchen Experten für Kundenberatung und Softwareentwicklung."

        results = extractor.extract_competences(text)
        labels = {r.esco_label for r in results}

        assert "Kunden beraten" in labels
        assert "Software entwickeln" in labels
        assert len(results) == 2

    def test_02_custom_mapping_pass(self, extractor):
        """Testet Pass 2: Das Custom Mapping von Abkürzungen (z.B. Jira)."""
        text = "Wir arbeiten agil und nutzen Jira für das Projektmanagement. Auch NoSQL ist wichtig."

        results = extractor.extract_competences(text)
        labels = {r.esco_label for r in results}

        # 'jira' sollte zu 'Projektmanagement durchführen' gemappt werden
        assert "Projektmanagement durchführen" in labels
        # 'NoSQL' sollte zu 'Datenbanken verwalten' gemappt werden
        assert "Datenbanken verwalten" in labels
        assert len(results) == 2

    def test_03_blacklist_filter(self, extractor):
        """Testet die Blacklist-Filterung gegen generische Begriffe."""
        # 'erfahrung' und 'management' sind auf der Blacklist
        text = "Du bringst Erfahrung in Projektmanagement mit und beherrschst Kommunikation."

        results = extractor.extract_competences(text)
        labels = {r.original_term for r in results}

        # Überprüfen, dass Blacklist-Begriffe nicht extrahiert wurden
        assert "erfahrung" not in labels
        assert "kommunikation" not in labels

        # Überprüfen, dass nur der gültige Begriff (Projektmanagement) extrahiert wird
        # HINWEIS: Dies testet, ob die Extractor-Logik 'Projektmanagement' als generischen Begriff erkennt und dann filtert.
        # Da 'Projektmanagement' selbst ein Blacklist-Begriff sein könnte, hängt der erwartete Output von der genauen Filterlogik ab.
        # Im Idealfall wird 'Projektmanagement' nicht als Blacklist-Begriff selbst, sondern nur als generierter Token gefiltert.
        assert len(results) == 1 # Angenommen, der Extractor findet nur den gültigen Skill (oder 0, falls er auch gefiltert wird)

    def test_04_idempotency_check(self, extractor):
        """Testet, ob identische Begriffe nicht mehrfach gefunden werden (Deduplizierung)."""
        text = "Wir suchen einen Entwickler für Datenbanken und Datenbanken."

        results = extractor.extract_competences(text)

        # Sollte nur einmal 'Datenbanken verwalten' finden
        assert len(results) == 1
        assert results[0].esco_label == "Datenbanken verwalten"

    def test_05_uri_and_id_integrity(self, extractor):
        """Testet, ob die ESCO-Daten (URI/ID) korrekt gemappt werden."""
        text = "Wir suchen Experten für UX-Testing."

        results = extractor.extract_competences(text)

        assert len(results) == 1
        result = results[0]

        # Prüft die korrekte Zuordnung aus dem Mock (Fixture)
        assert result.esco_label == "UX-Testing durchführen"
        assert result.esco_uri == "http://esco/uri/4"
        assert result.esco_group_code == "G_D"

# NEU: Tests für den Fuzzy Matcher (Pass 3) müssten hier noch folgen und das Spacy-Modell mocken oder den Fuzzy-Matcher separat testen.
