# 📊 JOB MINING PROJEKT - VOLLSTÄNDIGER STATUS

**Masterarbeit:** Kompetenzen im Wandel - Analyse UX-naher Berufsfelder  
**Student:** [Dein Name]  
**Universität:** Universität Siegen  
**Stand:** 25.10.2025

---

## 🎯 EXPOSÉ - FORSCHUNGSFRAGE

### Hauptforschungsfrage:
> **Wie verändern sich die in Stellenanzeigen geforderten Kompetenzen in UX-nahen Berufsbildern über die Zeit, und was lässt sich daraus über die digitale Transformation von Arbeit, Organisation und Qualifikation ableiten?**

### Teilfragen:
1. Welche Kompetenzen werden aktuell in UX-nahen Stellenanzeigen gefordert?
2. Wie haben sich diese Anforderungen über die Zeit entwickelt?
3. Welche Unterschiede gibt es zwischen Branchen und Berufsrollen?
4. Was sagen diese Entwicklungen über die digitale Transformation aus?

### Untersuchungsgegenstand:
- **UX/UI Design** (Designer, Visual Designer, Interaction Designer)
- **Product Management** (Product Owner, Product Manager)
- **Business Analysis** (Business Analyst, Requirements Engineer)
- **Agile Coaching** (Scrum Master, Agile Coach)
- **UX Research** (UX Researcher, User Researcher)
- **Development (UX-nah)** (Frontend Developer mit UX-Fokus)

---

## 📚 THEORETISCHER RAHMEN

### Verwendete Theorien & Quellen:

| Theorie/Konzept | Quelle | Status | Verwendung im Code |
|-----------------|--------|--------|-------------------|
| **CRISP-DM Modell** | Chapman et al. (2000) | ✅ Vollständig | Gesamte Pipeline-Struktur |
| **ESCO Taxonomie** | EU (2025), Wilhelm-Weidner et al. (2025) | ✅ Implementiert | `competence_extraction.py` |
| **DigiBOKom** | Wiepcke (2023) | ⚠️ Teilweise | Könnte stärker integriert werden |
| **Text Mining** | Groß (2022), Zong et al. (2021), Wu (2024) | ✅ Implementiert | `data_preparation.py`, Extraction |
| **Digitale Transformation** | Barton et al. (2018) | ✅ Implementiert | Analyse-Phase, Agile Methods |
| **Agilität in Unternehmen** | Pfannstiel et al. (2021) | ✅ Implementiert | SAFe, Scrum-Erkennung |
| **Digital Design** | Beck (2024) | ✅ Implementiert | UX-Tools in Bibliothek |
| **Machine Learning** | McMahon (2023), Hirschle (2021) | ⏸️ Vorbereitet | Zeitreihenanalyse |

**Bewertung:** Theoretische Fundierung ist **solide und wissenschaftlich**! ✅

---

## ✅ WAS IST IMPLEMENTIERT?

### Pipeline-Übersicht (CRISP-DM):

```
Phase 1: Business Understanding ✅
└── Forschungsfrage definiert, Berufsfelder abgegrenzt

Phase 2: Data Understanding ✅
└── DataCollectionService
    ├── Lokale PDFs/Word-Dateien lesen
    └── Google Drive Integration (optional)

Phase 3: Data Preparation ✅
└── DataPreparationService
    ├── TextCleaner (Bereinigung)
    ├── DataNormalizer (Firmennamen, Standorte)
    ├── DataDeduplicator (Duplikate entfernen)
    └── DataValidator (Qualitätsprüfung)

Phase 4: Modeling ✅
└── CompetenceExtractionService
    ├── ESCO-Bibliothek (100+ Kompetenzen)
    ├── ContextExtractor (Firma, Standort, Anforderungen)
    └── Job-Kategorisierung (6 Kategorien)
└── AnalysisService
    ├── TimeSeriesAnalyzer (Trends)
    ├── BranchAnalyzer (Branchenvergleich)
    ├── RoleAnalyzer (Rollenvergleich)
    └── CompetenceClusterer (Clustering)

Phase 5: Evaluation ✅
└── QualityEvaluator
    ├── Datenqualität: 57.9%
    ├── Extraktionsgenauigkeit: 41.9%
    └── ESCO-Coverage: 100%

Phase 6: Deployment ⚠️ Teilweise
└── ReportingService ✅
    ├── CSV Export
    ├── JSON Export
    └── Statistik-Zusammenfassung
└── VisualizationService ❌ FEHLT
```

---

## 📊 AKTUELLE ERGEBNISSE (43 Stellenanzeigen)

### Quantitative Übersicht:
```
Gesamt Stellenanzeigen: 43
Gesamt Kompetenzen: 132
Ø Kompetenzen pro Anzeige: 3.1  ⚠️ ZU NIEDRIG!

ESCO-Abdeckung: 100% ✅
Datenqualität: 57.9%
Extraktionsgenauigkeit: 41.9%
```

### Top 10 Kompetenzen:
```
1. Prototyping: 12x
2. User Research: 11x
3. Figma: 10x
4. HTML5: 8x
5. Scrum: 8x
6. Wireframing: 6x
7. Journey Mapping: 6x
8. User Interviews: 5x
9. Design Thinking: 5x
10. Sketch: 5x
```

### Standorte:
```
Hamburg: 17x (40%) ← Überraschend dominant!
München: 10x (23%)
Berlin: 8x (19%)
```

### Job-Kategorien:
```
UX/UI Design: 25x (58%)
UX Research: 12x (28%)
Product Management: 5x
Other: 8x
```

### Branchen:
```
Nur 1 Branche erkannt ⚠️ Problem!
47% "Unbekannt" bei Firmen
```

---

## ⚠️ HAUPTPROBLEME

### 🔴 Problem 1: Nur 3.1 Kompetenzen/Anzeige (KRITISCH!)

**Erwartung:** 8-12 Kompetenzen pro UX-Stelle  
**Realität:** 3.1  
**Ursache:** Bibliothek zu klein (100 statt 200+)

**Fehlende Kompetenzen (aus neuen Anzeigen erkannt):**

#### A) Product Management (komplett unterrepräsentiert):
```python
FEHLT:
- Product Roadmap
- Business Case  
- Stakeholder Management
- Product Vision
- Go-to-Market Strategy
- Requirements Engineering
- Lean Product Development
- Product Backlog
- Feature Priorisierung
- Business Model Canvas
```

#### B) SAFe / Enterprise Agile (fehlt fast komplett):
```python
FEHLT:
- Release Train Engineer (RTE)
- Program Increment Planning (PI Planning)
- Agile Release Train (ART)
- Solution Train
- Value Stream
- Inspect & Adapt
- System Demo
- Program Board
```

#### C) UX Research (erweitert):
```python
FEHLT:
- Participant Recruiting
- Screener (Research Tool)
- User Panel / Panel Management
- Contextual Inquiry
- Diary Study
- Remote Testing
- Participant Management
- Field Study
- Ethnographic Research
```

#### D) Digital Marketing (fehlt komplett):
```python
FEHLT:
- SEO (Search Engine Optimization)
- SEA (Search Engine Advertising)
- Conversion Rate Optimization (CRO)
- Web Analytics (allgemein)
- Content Marketing
- Social Media Marketing
- Performance Marketing
- Marketing Automation
- Affiliate Marketing
```

#### E) CMS & Plattformen:
```python
FEHLT:
- Contentful
- Strapi
- Headless CMS (allgemein)
- Storyblok
- Sanity
- WordPress
- Drupal
- Ghost
```

#### F) Business Tools:
```python
FEHLT:
- Excel / Microsoft Excel
- PowerPoint / Microsoft PowerPoint
- Word / Microsoft Word
- SAP / SAP ERP
- Salesforce
- CRM (allgemein)
- ERP (allgemein)
- Business Intelligence / BI
- Tableau
- Power BI
```

#### G) Entwicklung (erweitert):
```python
FEHLT:
- REST API
- GraphQL
- Microservices
- CI/CD
- Jenkins
- GitLab
- GitHub Actions
- Node.js
- Express.js
- MongoDB
```

#### H) Soft Skills (schwer zu matchen, aber versuchen):
```python
FEHLT:
- Change Management
- Konfliktmanagement
- Präsentation / Präsentationsfähigkeit
- Workshop-Moderation
- Coaching
- Mentoring
- Führung / Leadership
- Verhandlung
- Empathie
- Kritikfähigkeit
```

**→ GESAMT: ~80 fehlende Kompetenzen!**

---

### 🟡 Problem 2: 53% "Unbekannt" bei Firmen

**Ursache:** LinkedIn-PDFs haben andere Struktur als direkte Stellenanzeigen

**Fehlende Firmen in `known_companies`:**
```python
FEHLT:
'humanity': 'Humanity',
'contentful': 'Contentful',
'iteratec': 'iteratec GmbH',
'agvolution': 'Agvolution GmbH',
'gpi consulting': 'GPI Consulting',
'sevdesk': 'sevDesk',
'lbs bayern': 'LBS Bayern',
'springer fachmedien': 'Springer Fachmedien München',
'jobs for humanity': 'Jobs for Humanity',
# ... und viele mehr aus den PDFs
```

**Lösung:** `ContextExtractor` erweitern (Zeile ~165)

---

### 🟡 Problem 3: Gehalt wird nicht extrahiert

**Beispiel aus Anzeigen:**
```
"65.000 - 95.000€" (Agvolution)
"60.000 - 80.000€" (Instaffo)
```

**Was fehlt:**
- Regex-Pattern für Gehaltsspannen
- Speicherung in JobAd-Objekt

**Lösung:** ContextExtractor um `extract_salary()` erweitern

---

### 🟡 Problem 4: Keine Zeitreihen möglich

**Ursache:**
- PDFs enthalten keine Datumsangaben
- Oder Datum ist im Text versteckt

**Was fehlt:**
- Bessere Datumserkennung im Text
- ODER: Mehr Anzeigen mit Dateinamen-Convention sammeln

**Aktuell:**
```
Anzeigen mit Datum: ~15/43 (35%)
Anzeigen ohne Datum: ~28/43 (65%)
```

---

## 🔧 WO IM CODE OPTIMIEREN?

### 📄 services/competence_extraction.py

**Zeilen 100-450:** `_create_curated_library()`

**Was tun:**
```python
# 1. Erweitere die kuratierte Bibliothek um ~80 Kompetenzen
# 2. Füge neue Kategorien hinzu:
#    - Product Management Practice
#    - SAFe Practice
#    - Digital Marketing
#    - CMS Platform
#    - Business Tool
#    - Soft Skill

# BEISPIEL (Zeile ~250 einfügen):
'Product Roadmap': {
    'category': 'Product Management Practice',
    'type': 'method',
    'uri': 'esco:skill/product-roadmap',
    'alternative_labels': ['Roadmap', 'Product Roadmapping']
},
'Release Train Engineer': {
    'category': 'SAFe Role',
    'type': 'role',
    'uri': 'esco:skill/rte',
    'alternative_labels': ['RTE', 'Release Train Engineering']
},
# ... und so weiter für alle ~80 fehlenden
```

**Erwartete Verbesserung:**
- Von 100 auf **180-200 Kompetenzen**
- Von 3.1 auf **7-9 Kompetenzen/Anzeige**

---

### 📄 services/competence_extraction.py

**Zeilen 165-200:** `ContextExtractor.__init__()` → `self.known_companies`

**Was tun:**
```python
# Erweitere das Dictionary um ~30-40 neue Firmen:
self.known_companies = {
    # ... bestehende ...
    
    # NEUE aus den Anzeigen:
    'humanity': 'Humanity',
    'contentful': 'Contentful',
    'iteratec': 'iteratec GmbH',
    'luy': 'LUY',
    'agvolution': 'Agvolution GmbH',
    'gpi consulting': 'GPI Consulting',
    'sevdesk': 'sevDesk',
    'lbs bayern': 'LBS Bayern',
    'lbs bayerische': 'LBS Bayerische Landesbausparkasse',
    'springer fachmedien': 'Springer Fachmedien München GmbH',
    'springer nature': 'Springer Nature',
    'jobs for humanity': 'Jobs for Humanity',
    
    # ... weitere aus PDFs
}
```

**Erwartete Verbesserung:**
- Von 53% auf **< 20% "Unbekannt"**

---

### 📄 services/competence_extraction.py

**Zeilen ~350:** Neue Methode hinzufügen: `extract_salary()`

**Was tun:**
```python
def extract_salary(self, text: str) -> Optional[tuple]:
    """Extrahiert Gehaltsangaben"""
    
    # Pattern für deutsche Gehälter
    patterns = [
        r'(\d{2,3}\.?\d{3})\s*-\s*(\d{2,3}\.?\d{3})\s*€',  # 65.000 - 95.000€
        r'(\d{2,3}),?(\d{3})K?\s*-\s*(\d{2,3}),?(\d{3})K?', # 65K - 95K
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Extrahiere min/max
            return (min_salary, max_salary)
    
    return None
```

---

### 📄 models/job_ad.py

**Zeile ~35:** Neue Felder hinzufügen

**Was tun:**
```python
@dataclass
class JobAd:
    # ... bestehende Felder ...
    
    # NEU:
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "EUR"
```

---

## 📈 ERWARTETE VERBESSERUNGEN

### Nach Optimierung:

| Metrik | Vorher | Nachher | Verbesserung |
|--------|--------|---------|--------------|
| **Ø Kompetenzen/Anzeige** | 3.1 | 7-9 | +130% ✅ |
| **Unbekannte Firmen** | 53% | < 20% | -62% ✅ |
| **Extraktionsgenauigkeit** | 41.9% | 70-80% | +80% ✅ |
| **Bibliotheksgröße** | 100 | 180-200 | +90% ✅ |
| **Gehalt extrahiert** | 0% | ~30% | +30% ✅ |

---

## 🎯 PRIORITÄTEN FÜR NÄCHSTE OPTIMIERUNG

### 🔴 PRIO 1 (KRITISCH):
**Kompetenz-Bibliothek erweitern**
- Datei: `services/competence_extraction.py`
- Zeilen: 100-450
- Aufwand: 1-2h
- Impact: **HOCH** (von 3.1 auf 7-9 Kompetenzen)

### 🟡 PRIO 2 (WICHTIG):
**Firmen-Erkennung verbessern**
- Datei: `services/competence_extraction.py`
- Zeilen: 165-200
- Aufwand: 30 Min
- Impact: **MITTEL** (von 53% auf 20% Unbekannt)

### 🟢 PRIO 3 (NICE-TO-HAVE):
**Gehalt-Extraktion hinzufügen**
- Dateien: `competence_extraction.py` + `job_ad.py`
- Aufwand: 1h
- Impact: **NIEDRIG** (nicht für Forschungsfrage kritisch)

### 🟢 PRIO 4 (SPÄTER):
**Visualisierung erstellen**
- Datei: NEU `services/visualization.py`
- Aufwand: 2-3h
- Impact: **MITTEL** (für Masterarbeit schön, aber nicht kritisch)

---

## 📚 FÜR DIE MASTERARBEIT - CHECKLISTE

### Methodisch:
- [x] CRISP-DM Modell vollständig implementiert
- [x] ESCO-konform (100% Coverage)
- [x] Text Mining nach Stand der Technik (Groß, Wu, Zong)
- [ ] Stichproben-Validierung (manual check von 10-20 Anzeigen)
- [ ] Visualisierung (Plots, Dashboard)
- [ ] Inter-Rater-Reliability (falls Zweitmeinung möglich)

### Inhaltlich:
- [x] Forschungsfrage klar formuliert
- [x] Theoretischer Rahmen solide (7 Quellen)
- [x] UX-nahe Berufe klar definiert (6 Kategorien)
- [ ] Zeitreihe funktioniert (braucht mehr Daten mit Datum!)
- [x] Branchen-/Rollenvergleich funktioniert
- [ ] Interpretation digitale Transformation (teilweise, ausbaubar)

### Datenbasis:
- [x] Datensammlung automatisiert
- [x] Export strukturiert (CSV, JSON, TXT)
- [ ] **Genug Daten: 43 zu wenig! Ziel: 150-200**
- [ ] **Zeitraum abgedeckt: fehlt noch! Ziel: 2-3 Jahre**
- [x] Qualitätsmetriken dokumentiert

### Für Note 1.0-1.3:
- [ ] 150+ Stellenanzeigen
- [ ] Zeitreihe über mindestens 2 Jahre
- [ ] Visualisierung (mind. 5 aussagekräftige Plots)
- [ ] Validierung (Stichprobe + Begründung)
- [ ] Qualitative Ergänzung (3-5 Experteninterviews)

---

## 🚀 NÄCHSTE SCHRITTE

### Sofort (diese Woche):
1. ✅ **Kompetenz-Bibliothek erweitern** (Prio 1)
    - services/competence_extraction.py bearbeiten
    - ~80 Kompetenzen hinzufügen
    - Neu durchlaufen lassen
    - Ergebnisse vergleichen

2. ✅ **Firmen-Erkennung verbessern** (Prio 2)
    - known_companies erweitern
    - Neu durchlaufen
    - Statistik prüfen

### Diese Woche:
3. ⏳ **Gehalt-Extraktion** (Prio 3, optional)
4. ⏳ **Mehr Daten sammeln** (50-100 weitere Anzeigen)

### Nächste 2 Wochen:
5. ⏳ **Visualisierung** (Prio 4)
6. ⏳ **Validierung** (Stichprobe)

### Nächste 4 Wochen:
7. ⏳ **150+ Anzeigen** sammeln mit Zeitstempel
8. ⏳ **Experteninterviews** (optional, aber sehr gut für MA)

---

## 📁 PROJEKT-STRUKTUR

```
job_mining_project/
├── main.py                          ✅ Funktioniert
├── requirements.txt                 ✅ Vollständig
├── README.md                        ✅ Dokumentiert
│
├── models/
│   ├── job_ad.py                   ✅ OK (evtl. Gehalt-Felder hinzufügen)
│   └── analysis_results.py         ✅ OK
│
├── services/
│   ├── data_collection.py          ✅ Funktioniert
│   ├── data_preparation.py         ✅ Funktioniert
│   ├── competence_extraction.py    ⚠️ OPTIMIEREN (Prio 1+2)
│   ├── analysis.py                 ✅ Funktioniert
│   ├── reporting.py                ✅ Funktioniert
│   └── visualization.py            ❌ FEHLT (Prio 4)
│
├── utils/
│   ├── logger.py                   ✅ OK
│   └── config.py                   ✅ OK
│
├── data/
│   ├── raw/job_ads/                ✅ 43 PDFs (mehr sammeln!)
│   ├── processed/
│   │   ├── analysis/
│   │   ├── reports/                ✅ CSV, JSON, TXT vorhanden
│   │   └── visualizations/         ❌ Leer
│   └── competence_library.csv      ✅ Auto-generiert (wird erweitert)
│
└── logs/                           ✅ Logging funktioniert
```

---

## 💾 VERWENDUNG DIESES DOKUMENTS

**Für den nächsten Chat:**
1. Lade diese Datei hoch
2. Lade zusätzlich hoch:
    - `services/competence_extraction.py`
    - `data/competence_library.csv`
    - `data/processed/reports/statistiken.txt`
    - 3-5 Beispiel-PDFs der neuen Anzeigen

3. Erste Nachricht:
```
Ich optimiere mein Job Mining Projekt (siehe PROJECT_STATUS.md).

PROBLEM: Nur 3.1 Kompetenzen/Anzeige (sollte 8-12 sein)
URSACHE: Bibliothek zu klein (100 statt 200+)

AUFGABE: Erweitere competence_extraction.py um ~80 fehlende 
Kompetenzen (siehe Abschnitt "HAUPTPROBLEME" im Status-Dokument).

Zeig mir den erweiterten Code für _create_curated_library().
```

---

## 📞 KONTAKT & RESSOURCEN

**Betreuer:** [Name eintragen]  
**Email:** [Email eintragen]

**Repository:** [GitHub URL wenn vorhanden]  
**Literatur:** Siehe Abschnitt "Theoretischer Rahmen"

**Zuletzt aktualisiert:** 25.10.2025, 16:30 Uhr

---

**Status:** 🟡 In Optimierung | Nächster Meilenstein: Bibliothek erweitern
