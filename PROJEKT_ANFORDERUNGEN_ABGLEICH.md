# 📊 Projekt-Anforderungen Abgleich: Job Mining Masterprojekt

**Datum:** 2024-12-27
**Deadline Postersession:** 14. Januar 2025 (18 Tage!)
**Abgabe:** Mitte März 2025

---

## 🎯 FORSCHUNGSFRAGE

**Laut Exposé:**
> Wie verändern sich die in Stellenanzeigen geforderten Kompetenzen in UX-nahen Berufsbildern über die Zeit, und was lässt sich daraus über die digitale Transformation von Arbeit, Organisation und Qualifikation ableiten?

**Zielgruppen:**
- UX/UI Designer
- Product Owner
- Business Analysten

---

## ✅❌ IST vs. SOLL-Analyse

### 1. DATENQUELLEN

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| Mehrjähriges Stellenanzeigen-Archiv | ✅ Angenommen | Vorhanden (Quelle unklar) | Muss verifiziert werden |
| LinkedIn-Scraping (automatisiert) | ❌ FEHLT | Nicht implementiert | **KRITISCH für laufenden Betrieb** |
| Google Drive Integration | ❌ FEHLT | Nicht implementiert | |
| PDF/DOCX Upload | ✅ Vorhanden | `AdvancedTextExtractor` | Funktioniert |

### 2. DATENVERARBEITUNG

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| CRISP-DM Prozess | 🟡 Teilweise | Workflow vorhanden | Nicht dokumentiert |
| Python Pandas/NumPy | ✅ Vorhanden | requirements.txt | |
| Text-Extraktion (PDF/DOCX) | ✅ Vorhanden | pypdf, python-docx | |
| Datenbereinigung | ❌ FEHLT | Keine Cleaning-Pipeline | |
| Hash für Idempotenz | ✅ Vorhanden | `rawTextHash` | Einfacher Hash |

### 3. KOMPETENZ-EXTRAKTION

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| Wörterbuch-basierte Extraktion | ✅ Vorhanden | Keyword-Matching | Funktioniert |
| ESCO-Mapping | ✅ Vorhanden | 35.047 Skills geladen | **EXZELLENT** |
| ESCO-Hierarchie | ✅ Vorhanden | 1.574 Gruppen | |
| Custom Skills | ✅ Vorhanden | 4 Custom Skills | Sehr wenige! |
| **Wörterbuch-Automatisierung** | ❌ FEHLT | Statisches Keyword-Set | **KRITISCH** |
| Synonyme | ✅ Vorhanden | ESCO altLabels | |
| original_term korrekt | ❌ FEHLER | Immer preferred_label | Muss gefixt werden |

### 4. KI-INTEGRATION

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| **ChatGPT API** | ❌ FEHLT | Nicht implementiert | **SEHR WICHTIG laut Exposé** |
| Semantische Gruppierung | ❌ FEHLT | Keine Cluster-Bildung | |
| Kontextdeutung | ❌ FEHLT | Nur Keyword-Matching | |
| Trendnarration | ❌ FEHLT | Keine Text-Generierung | |

### 5. METADATEN-EXTRAKTION

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| Jobtitel | 🟡 Teilweise | Nur Filename | |
| Rolle (UX/PO/BA) | ❌ FEHLT | "Placeholder" | **KRITISCH** |
| Branche | ❌ FEHLT | "Placeholder" | **KRITISCH** |
| Region | ❌ FEHLT | "Placeholder" | **KRITISCH** |
| Datum | ❌ FEHLT | Hardcoded "2024-12-01" | **KRITISCH** |
| Firma | ❌ FEHLT | Nicht extrahiert | |
| Seniorität | ❌ FEHLT | Nicht extrahiert | |
| Sprache | ❌ FEHLT | Nicht extrahiert | |

### 6. ZEITANALYSE

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| **Zeitreihen-Analyse** | ❌ FEHLT | Kein Zeitvergleich | **KERN DES PROJEKTS!** |
| Trend-Berechnung | ❌ FEHLT | Keine Statistik | |
| Periode-Vergleiche | ❌ FEHLT | 2015-2018 vs. 2019-2025 | |
| Tool-Evolution | ❌ FEHLT | Axure→Figma Trend | Exposé-Beispiel! |

### 7. BRANCHEN/REGIONAL-ANALYSE

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| Branchen-Filter | ❌ FEHLT | Keine Segmentierung | IT, Finance, Public, E-Com |
| Regional-Vergleich | ❌ FEHLT | Keine Geo-Daten | Hamburg Hotspot? |
| Länder-Vergleich | ❌ FEHLT | Nur DE erwähnt | |

### 8. VISUALISIERUNG

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| **Dashboard** | ❌ FEHLT | Nicht implementiert | **SEHR WICHTIG** |
| Wichtige Kennzahlen | ❌ FEHLT | Keine KPIs definiert | |
| Trend-Charts | ❌ FEHLT | Keine Visualisierung | |
| Heatmaps | ❌ FEHLT | Nicht geplant | |
| Export-Funktion | ❌ FEHLT | CSV? Excel? | |

### 9. WISSENSCHAFTLICHE DOKUMENTATION

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| Methodenbeschreibung | 🟡 Teilweise | Code vorhanden | Nicht dokumentiert |
| Validierung | ❌ FEHLT | Keine Tests | |
| Qualitätssicherung | ❌ FEHLT | Keine Metriken | |
| Literatur-Mapping | ❌ FEHLT | Keine Referenzen | |
| 20-30 Seiten Doku | ❌ FEHLT | Nur README | |

### 10. TECHNISCHE INFRASTRUKTUR

| Anforderung | Status | Aktueller Stand | Notizen |
|-------------|--------|-----------------|---------|
| Docker Setup | ❌ FEHLT | Dockerfiles fehlen | |
| API läuft | ✅ Python | FastAPI funktioniert | Port 8000 |
| Kotlin Backend | 🟡 Code | Build failed (offline) | |
| Datenbank | ✅ Config | PostgreSQL konfiguriert | |
| Logging | ❌ FEHLT | Keine Logs | |

---

## 🔴 KRITISCHE LÜCKEN (Priorität für Postersession)

### **MUST-HAVE (bis 14.01.2025):**

1. **Zeitanalyse-Funktion**
   - Gruppierung nach Jahr
   - Trend-Berechnung (Zunahme/Abnahme)
   - Periode-Vergleiche (2015-2018 vs. 2019-2025)

2. **Metadaten-Extraktion**
   - Jahr aus Filename oder PDF-Inhalt
   - Branche erkennen (Keywords: "Finance", "Public", "E-Commerce")
   - Region extrahieren (Städtenamen)

3. **Dashboard (minimal)**
   - Top 10 Skills über Zeit
   - Tool-Evolution (Axure → Figma)
   - Branchen-Verteilung

4. **ChatGPT Integration**
   - Semantische Cluster-Namen generieren
   - Trend-Interpretation
   - Anomalien erklären

5. **Erste Ergebnisse**
   - Mindestens 50-100 Anzeigen analysiert
   - 3-5 klare Trends identifiziert
   - Poster-Material generiert

### **SHOULD-HAVE (bis März 2025):**

6. **LinkedIn-Scraping**
   - Automatisierter Download
   - Monatlicher Update-Prozess

7. **Erweiterte Analyse**
   - Semantische Cluster (BERT/Word2Vec)
   - Skill-Kookkurrenzen
   - Vorhersage-Modelle

8. **Dokumentation**
   - Methodenbeschreibung
   - Validierung
   - 20-30 Seiten wissenschaftliche Arbeit

### **NICE-TO-HAVE:**

9. **Erweiterte Features**
   - Multi-Sprachen-Support
   - Internationale Vergleiche
   - Job-Recommendation Engine

---

## 📈 ERSTE ERGEBNISSE (aus Anforderungen-PDF)

**7 Stellenanzeigen bereits analysiert:**

### **Tool-Trends:**
```
2015-2018: Axure RP, Photoshop, TechSmith Morae
           ↓ DISRUPTION
2019-2025: Figma (71%), Design Systems, Agile UX
```

### **Top Skills:**
| Skill | Häufigkeit | Trend |
|-------|-----------|-------|
| Figma | 5/7 (71%) | ↗️ NEU |
| Prototyping | 6/7 (86%) | → STABIL |
| User Research | 5/7 (71%) | → STABIL |
| Workshops/Design Thinking | 3/7 (43%) | ↗️ ZUNEHMEND |
| Barrierefreiheit | 1/7 (14%) | ↗️ EMERGING |

### **Branchen-Unterschiede:**
- **IT/Tech:** Figma, IA, Styleguides
- **Finance:** Design Thinking, Innovation, Workshops
- **Public:** Barrierefreiheit, Prozesse
- **E-Commerce:** A/B-Testing, Analytics

### **Regional:**
- Hamburg = Hotspot (4/7 Anzeigen)

---

## 🎯 EMPFOHLENE ROADMAP

### **Phase 1: Postersession-Ready (bis 14.01.2025)**

**Woche 1 (bis 3.1.):**
- [ ] Metadaten-Extraktion implementieren (Jahr, Branche, Region)
- [ ] Zeitanalyse-Funktion (Gruppierung nach Jahr)
- [ ] 50-100 Anzeigen aus Archiv verarbeiten

**Woche 2 (bis 10.1.):**
- [ ] ChatGPT API Integration (Cluster-Namen, Interpretationen)
- [ ] Mini-Dashboard (Streamlit oder Dash)
- [ ] Top-Trends identifizieren

**Woche 3 (bis 14.1.):**
- [ ] Poster erstellen (Trends visualisieren)
- [ ] Präsentation vorbereiten
- [ ] **POSTERSESSION**

### **Phase 2: Vollständige Analyse (Jan-Feb 2025)**

**Januar:**
- [ ] LinkedIn-Scraping implementieren
- [ ] Wörterbuch-Automatisierung
- [ ] Erweiterte Statistik (Korrelationen, Signifikanz)

**Februar:**
- [ ] Semantische Cluster (NLP)
- [ ] Branchen-/Regional-Vergleiche
- [ ] Validierung der Ergebnisse

### **Phase 3: Abgabe (März 2025)**

**März:**
- [ ] Wissenschaftliche Dokumentation (20-30 Seiten)
- [ ] Code-Dokumentation
- [ ] Finaler Report
- [ ] **ABGABE**

---

## 💡 VERBESSERUNGSVORSCHLÄGE

### **Aktueller Code:**

**Stärken:**
- ✅ ESCO-Integration ist exzellent (35.000 Skills)
- ✅ PDF/DOCX-Parsing funktioniert
- ✅ Keyword-Matching ist solide
- ✅ Architektur ist sauber (DDD, Interfaces)

**Schwächen:**
- ❌ Keine Zeitanalyse (KERN DES PROJEKTS!)
- ❌ Keine Metadaten-Extraktion
- ❌ Keine Visualisierung
- ❌ Keine ChatGPT-Integration
- ❌ Placeholder-Werte überall

### **Schnellste Wins:**

1. **Zeitanalyse** (2 Tage)
   ```python
   def extract_year_from_filename(filename):
       # "Stellenanzeige_2023_UX_Designer.pdf" → 2023
       match = re.search(r'20\d{2}', filename)
       return int(match.group()) if match else None

   def analyze_trends(df):
       # Gruppiere nach Jahr
       yearly = df.groupby('year')['competences'].apply(
           lambda x: Counter([c for comp_list in x for c in comp_list])
       )
       return yearly
   ```

2. **ChatGPT API** (1 Tag)
   ```python
   import openai

   def generate_cluster_name(skills):
       prompt = f"Nenne einen prägnanten Namen für diese Skill-Gruppe: {skills}"
       response = openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content
   ```

3. **Mini-Dashboard** (2 Tage mit Streamlit)
   ```python
   import streamlit as st

   st.title("Job Mining Dashboard")

   # Top Skills über Zeit
   st.line_chart(trend_data)

   # Branchen-Vergleich
   st.bar_chart(branch_data)
   ```

---

## 📚 LITERATUR-MAPPING (aus Exposé)

**Theoretische Basis:**
- Barton et al. (2018) - Digitalisierung in Unternehmen
- Beck (2024) - Digital Design
- Pfannstiel et al. (2021) - Agilität in Unternehmen
- Schleiter & Zech (2020) - Digitale Kompetenzen
- Wilhelm-Weidner et al. (2025) - ESCO in Bildung
- Wiepcke (2023) - DigiBOKom Kompetenzrahmen

**Methodisch:**
- Zong et al. (2021) - Text Data Mining
- McMahon (2023) - Machine Learning Engineering
- Campesato (2024) - Python + ChatGPT
- Wu (2024) - Data Mining with Python

---

## ⚠️ RISIKEN

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Zu wenig Zeit bis Poster | HOCH | HOCH | Fokus auf Minimal-Dashboard |
| LinkedIn-Scraping komplex | MITTEL | MITTEL | Zuerst Archiv nutzen |
| ChatGPT API Kosten | NIEDRIG | NIEDRIG | Budget planen |
| Datenqualität | MITTEL | HOCH | Validierung einbauen |
| Keine klaren Trends | NIEDRIG | HOCH | Mehr Daten sammeln |

---

## 🎯 ERFOLGS-KRITERIEN

**Postersession (14.01.):**
- ✅ 3-5 klare Trends nachgewiesen (z.B. Figma-Durchbruch)
- ✅ Dashboard zeigt Zeitanalyse
- ✅ Mindestens 50 Anzeigen analysiert
- ✅ Branchen-Unterschiede sichtbar

**Abgabe (März):**
- ✅ 20-30 Seiten wissenschaftliche Arbeit
- ✅ Vollständige Methoden-Dokumentation
- ✅ Code auf GitHub
- ✅ Dashboard deployed
- ✅ Validierte Ergebnisse

---

**Erstellt:** 2024-12-27
**Für:** Masterprojekt Job Mining
**Deadline:** 14. Januar 2025 (Postersession), März 2025 (Abgabe)
