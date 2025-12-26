# 🔬 Proof of Concept

**Status:** 🟡 POC

## Zweck

Dieser Ordner ist für **funktionierende Prototypen** gedacht.

Im Gegensatz zu reinen Konzepten (🔵) enthält dieser Ordner Code, der:
- ✅ Tatsächlich ausführbar ist
- ✅ Ein Feature demonstriert
- ✅ Als Grundlage für Produktiv-Code dienen kann

## Struktur

Jeder PoC sollte eigenständig sein:

```
proof-of-concept/
├── fuzzy-matching-test/
│   ├── README.md
│   ├── fuzzy_matcher.py
│   ├── test_data.csv
│   └── requirements.txt
├── esco-hierarchy-analysis/
│   ├── README.md
│   ├── hierarchy_analyzer.py
│   └── sample_output.json
└── ocr-pdf-extraction/
    ├── README.md
    ├── ocr_extractor.py
    └── test.pdf
```

## Guidelines

1. **Jeder PoC hat eigene README** mit:
   - Was macht der Code?
   - Wie führe ich ihn aus?
   - Was sind die Ergebnisse?

2. **Dependencies dokumentieren**:
   - `requirements.txt` für Python
   - Maven/Gradle Dependencies für Kotlin

3. **Test-Daten einbinden**:
   - Kleine Beispiel-Dateien
   - Keine sensiblen Daten!

4. **Ergebnisse zeigen**:
   - Screenshots oder Output-Beispiele
   - Zeige, dass es funktioniert

## Beispiel-PoCs

Ideen für Prototypen:
- Fuzzy Matching mit verschiedenen Algorithmen (Levenshtein, Jaro-Winkler)
- ESCO-Hierarchie-Navigation
- OCR für gescannte PDFs
- NLP-Pipeline mit spaCy
- Transformer-basiertes Matching
