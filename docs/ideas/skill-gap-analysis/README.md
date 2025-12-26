# 📊 Skill-Gap-Analyse

**Status:** 🔵 KONZEPT

## Idee

Analysiere die Lücke zwischen gelehrten und geforderten Kompetenzen.

## Workflow

```
Hochschule:
  Modulhandbücher hochladen
    ↓
  System extrahiert Kompetenzen
    ↓
  Kompetenz-Portfolio erstellt

Arbeitsmarkt:
  Stellenanzeigen hochladen
    ↓
  System extrahiert geforderte Kompetenzen
    ↓
  Anforderungs-Profil erstellt

Analyse:
  Vergleiche Portfolio ↔ Anforderungen
    ↓
  Identifiziere Gaps
    ↓
  Generiere Empfehlungen
```

## Ausgaben

### 1. Gap-Report für Hochschulen
```
❌ Diese Skills werden nachgefragt, aber nicht gelehrt:
   - Docker/Kubernetes (78 Stellenanzeigen)
   - Prompt Engineering (45 Stellenanzeigen)
   - React.js (120 Stellenanzeigen)

✅ Diese Skills werden gelehrt und nachgefragt:
   - Python (200 Stellenanzeigen, 15 Module)
   - SQL (150 Stellenanzeigen, 8 Module)

⚠️ Diese Skills werden gelehrt, aber kaum nachgefragt:
   - COBOL (0 Stellenanzeigen, 2 Module)
```

### 2. Empfehlungen für Studenten
```
Dein Studiengang: Wirtschaftsinformatik DHBW Karlsruhe

Markt-Trends zeigen:
  → Cloud-Technologien werden stark nachgefragt
  → Empfohlene Zusatzkurse:
    - AWS Certified Cloud Practitioner
    - Docker & Kubernetes Basics

Bücher-Empfehlungen:
  - "Cloud Native Patterns" (passt zu deinem Profil)
```

## Visualisierungen

- Kompetenz-Matrix (gelehrt vs. gefordert)
- Trend-Analysen über Zeit
- Heatmaps nach Regionen/Branchen

## Beispiel-Code

Lege hier deine Implementierungen ab:
- `gap_analyzer.py` - Kern-Logik
- `visualization.py` - Charts/Diagramme
- `recommendation_engine.py` - Empfehlungs-Algorithmus

## Datenquellen

- Modulhandbücher (Upload)
- Stellenanzeigen (Upload oder Scraping)
- Externe APIs (optional): LinkedIn, Indeed
