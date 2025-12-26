# 🎓 Modulhandbuch-Support

**Status:** 🔵 KONZEPT

## Idee

Erweitere das System um die Analyse von Modulhandbüchern von Universitäten und Fachhochschulen.

## Ziele

1. Automatische Erkennung von Modulhandbüchern (vs. Stellenanzeigen)
2. Extraktion von Metadaten (ECTS, Semester, Modulcode, etc.)
3. Kompetenz-Mapping aus Lernzielen und Modulinhalten
4. Skill-Gap-Analyse zwischen Lehre und Arbeitsmarkt

## Beispiel-Code

Siehe Dateien in diesem Verzeichnis:
- `ModuleHandbook.kt` - Kotlin Entity (Beispiel)
- `document_classifier.py` - Python Classifier (Beispiel)
- `module_metadata_extractor.py` - Metadaten-Extraktion (Beispiel)

## Nächste Schritte

- [ ] Sammlung von Beispiel-Modulhandbüchern
- [ ] Analyse der Dokumentstruktur
- [ ] Prototyp der Metadaten-Extraktion
- [ ] Integration in bestehende Architektur

## Offene Fragen

1. Wie unterscheiden wir Modulhandbücher von anderen PDFs?
2. Welche Hochschulen haben welche Formate?
3. Wie extrahieren wir Lernziele automatisch?
