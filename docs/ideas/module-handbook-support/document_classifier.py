# 🔵 KONZEPT - Beispiel-Code für Dokumenttyp-Klassifizierung
# NICHT in Produktion verwenden!

"""
Automatische Erkennung des Dokumenttyps basierend auf Textinhalten.

Unterscheidet zwischen:
- Stellenanzeigen (JobPosting)
- Modulhandbüchern (ModuleHandbook)
- Fachbüchern (Textbook)
"""

from enum import Enum
from typing import Dict, List


class DocumentType(str, Enum):
    JOB_POSTING = "job_posting"
    MODULE_HANDBOOK = "module_handbook"
    TEXTBOOK = "textbook"
    UNKNOWN = "unknown"


class DocumentTypeClassifier:
    """
    Klassifiziert Dokumente basierend auf Keyword-Matching.

    TODO: In Produktion sollte ML-basierte Klassifikation verwendet werden
    (z.B. mit scikit-learn oder transformers)
    """

    def __init__(self):
        # Indikator-Keywords für jeden Dokumenttyp
        self.indicators: Dict[DocumentType, List[str]] = {
            DocumentType.MODULE_HANDBOOK: [
                "modulhandbuch", "ects", "studiengang", "semester",
                "lernziele", "prüfungsleistung", "workload",
                "voraussetzungen", "modulbeschreibung", "kompetenzen",
                "hochschule", "universität", "fachhochschule",
                "pflichtmodul", "wahlpflicht", "studienplan"
            ],

            DocumentType.JOB_POSTING: [
                "stellenanzeige", "bewerbung", "gehalt", "vollzeit",
                "teilzeit", "benefits", "wir suchen", "ihre aufgaben",
                "ihr profil", "das bieten wir", "arbeitszeit",
                "unbefristet", "befristet", "vertragsart"
            ],

            DocumentType.TEXTBOOK: [
                "isbn", "verlag", "auflage", "kapitel",
                "übungsaufgaben", "literaturverzeichnis",
                "vorwort", "inhaltsverzeichnis", "bibliografie",
                "copyright", "alle rechte vorbehalten",
                "printed in", "edition"
            ]
        }

    def classify(self, text: str, filename: str = "") -> DocumentType:
        """
        Klassifiziert ein Dokument basierend auf seinem Inhalt.

        Args:
            text: Der Dokumenttext
            filename: Optional - der Dateiname (für zusätzliche Hinweise)

        Returns:
            DocumentType enum
        """
        text_lower = text.lower()

        # Score-basierte Klassifikation
        scores: Dict[DocumentType, int] = {
            DocumentType.MODULE_HANDBOOK: 0,
            DocumentType.JOB_POSTING: 0,
            DocumentType.TEXTBOOK: 0
        }

        # Zähle Indikator-Treffer
        for doc_type, keywords in self.indicators.items():
            if doc_type == DocumentType.UNKNOWN:
                continue

            for keyword in keywords:
                if keyword in text_lower:
                    scores[doc_type] += 1

        # Dateiname-Bonus (falls vorhanden)
        filename_lower = filename.lower()
        if "modul" in filename_lower or "studien" in filename_lower:
            scores[DocumentType.MODULE_HANDBOOK] += 3
        elif "stellen" in filename_lower or "job" in filename_lower:
            scores[DocumentType.JOB_POSTING] += 3
        elif "buch" in filename_lower or "lehrbuch" in filename_lower:
            scores[DocumentType.TEXTBOOK] += 3

        # Bestimme den Typ mit dem höchsten Score
        max_score = max(scores.values())

        if max_score == 0:
            return DocumentType.UNKNOWN

        # Finde den Typ mit dem höchsten Score
        for doc_type, score in scores.items():
            if score == max_score:
                return doc_type

        return DocumentType.UNKNOWN

    def classify_with_confidence(self, text: str, filename: str = "") -> tuple[DocumentType, float]:
        """
        Klassifiziert mit Konfidenz-Score.

        Returns:
            Tuple aus (DocumentType, confidence_score zwischen 0.0 und 1.0)
        """
        doc_type = self.classify(text, filename)

        # TODO: Implementiere echte Konfidenz-Berechnung
        # Für Konzept: Vereinfachte Logik
        text_lower = text.lower()
        indicator_count = sum(
            1 for keyword in self.indicators.get(doc_type, [])
            if keyword in text_lower
        )

        # Normalisiere auf 0.0 - 1.0
        confidence = min(indicator_count / 5.0, 1.0)

        return doc_type, confidence


# BEISPIEL-VERWENDUNG (zum Testen)
if __name__ == "__main__":
    classifier = DocumentTypeClassifier()

    # Test 1: Modulhandbuch
    test_module = """
    Modulhandbuch Wirtschaftsinformatik

    Modulcode: WIN-INF-2023
    ECTS: 5
    Semester: 3. Semester
    Modultyp: Pflichtmodul

    Lernziele:
    Die Studierenden können...
    """

    result = classifier.classify(test_module)
    print(f"Test 1: {result}")  # Sollte MODULE_HANDBOOK sein

    # Test 2: Stellenanzeige
    test_job = """
    Wir suchen einen Software-Entwickler (m/w/d)

    Ihre Aufgaben:
    - Entwicklung von Backend-Services

    Ihr Profil:
    - Abgeschlossenes Studium

    Wir bieten:
    - Unbefristeter Vertrag
    - 30 Tage Urlaub
    """

    result = classifier.classify(test_job)
    print(f"Test 2: {result}")  # Sollte JOB_POSTING sein
