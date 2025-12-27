# 🚀 NÄCHSTE SCHRITTE FÜR POSTERSESSION (14. Jan 2025)

**Status:** ✅ Zeitreihen-Analyse implementiert
**Branch:** claude/fix-kotlin-python-api-b6uDC
**Verbleibende Zeit:** 18 Tage

---

## ✅ WAS IST FERTIG?

### 1. **POC → Main Migration** ✅
- Clean Architecture (Python)
- 7-Ebenen-Modell (Kotlin + Python)
- Intelligente Pipeline V13.3
- Bidirektionale JPA-Relationen

### 2. **Zeitreihen-Analyse** ✅
- SQL-Migration-Script (`migration.sql`)
- DTOs für Trend-Daten (`TrendDTO.kt`)
- Repository-Queries (`JobPostingRepository.kt`, `CompetenceRepository.kt`)
- TrendAnalysisService (`TrendAnalysisService.kt`)
- Dashboard-Controller (`DashboardController.kt`)

### 3. **Datenbank-Views & Funktionen** ✅
- `v_yearly_skill_stats` - Aggregierte Skill-Statistik
- `v_top_skills_per_year` - Top-10-Skills pro Jahr
- `v_digitalization_rate_per_year` - Digitalisierungsrate
- `calculate_trend_score()` - Trend-Berechnung

---

## 🔴 KRITISCH: SOFORT ERLEDIGEN (Tag 1-3)

### **1. Datenbank-Schema migrieren**

```bash
# PostgreSQL-Datenbank aktualisieren
psql -U jobmining_user -d jobmining_db -f migration.sql
```

**Was wird hinzugefügt:**
- Neue Spalten in `competence`: `is_digital`, `is_discovery`, `level`, `role_context`, `source_domain`
- Neue Spalten in `job_posting`: `raw_text_hash` (UNIQUE), `is_segmented`
- 7 Performance-Indices
- 3 Views für Zeitreihen-Analyse
- 1 Funktion für Trend-Berechnung

**Verification:**
```sql
-- Check: Neue Spalten vorhanden?
\d competence
\d job_posting

-- Check: Views vorhanden?
\dv

-- Check: Funktionen vorhanden?
\df calculate_trend_score
```

---

### **2. Python-Dependencies installieren**

```bash
cd python-backend

# Dependencies installieren
pip install -r requirements.txt

# SpaCy-Modell herunterladen (WICHTIG!)
python -m spacy download de_core_news_md

# Playwright-Browser installieren (für Web-Scraping)
playwright install chromium

# Verification
python -c "import spacy; nlp = spacy.load('de_core_news_md'); print('✅ SpaCy OK')"
```

---

### **3. Kotlin-App neu kompilieren**

```bash
cd kotlin-api

# Clean Build
./gradlew clean build

# Bei Fehler: Dependency-Cache löschen
rm -rf ~/.gradle/caches

# App starten
./gradlew bootRun
```

**Expected Output:**
```
Tomcat started on port(s): 8080 (http)
Started KotlinApiApplication in X.XXX seconds
```

---

### **4. Python-Backend starten**

```bash
cd python-backend

# FastAPI starten
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In separatem Terminal: Health-Check
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "OK",
  "esco_skills_count": 35047
}
```

---

## 🟡 WICHTIG: DATEN SAMMELN (Tag 4-10)

### **5. Historische Stellenanzeigen sammeln (2015-2025)**

**Ziel:** Mindestens 50 Jobs pro Jahr = **550 Jobs gesamt**

**Quellen:**
1. **Archive.org (Wayback Machine)**
   ```
   https://web.archive.org/web/20150101*/stepstone.de
   https://web.archive.org/web/20160101*/indeed.de
   ```

2. **StepStone, Indeed, LinkedIn**
   - Ältere Anzeigen in Unternehmens-Archiven
   - Kontaktiere Recruiter

3. **Hochschul-Archive**
   - FH Gummersbach Career Service
   - TH Köln Alumni-Netzwerk

**Ordner-Struktur:**
```
python-backend/data/jobs/
├── 2015/
│   ├── job_2015_01_java_dev.pdf
│   ├── job_2015_02_ux_designer.pdf
│   └── ...
├── 2016/
├── ...
└── 2025/
```

---

### **6. Batch-Processing ausführen**

```bash
# Über Python-Backend
curl -X POST http://localhost:8000/batch-process

# Oder über Kotlin-API
curl -X POST http://localhost:8080/api/job-mining/batch
```

**Was passiert:**
1. Liest alle PDFs aus `python-backend/data/jobs/`
2. Extrahiert Metadaten (Datum, Ort, Rolle)
3. Segmentiert Text (Aufgaben vs. Anforderungen)
4. Extrahiert Kompetenzen (ESCO + Discovery)
5. Speichert in PostgreSQL mit Ebenen-Informationen
6. Idempotenz-Check verhindert Duplikate

---

## 🟢 OPTIONAL: TESTING & DASHBOARD (Tag 11-15)

### **7. Dashboard testen**

**Endpoints:**

1. **Komplettes Dashboard**
   ```bash
   curl "http://localhost:8080/api/dashboard?startYear=2015&endYear=2025"
   ```

2. **Jährliche Trends**
   ```bash
   curl "http://localhost:8080/api/dashboard/yearly-trends?startYear=2015&endYear=2025"
   ```

3. **Top steigende Skills**
   ```bash
   curl "http://localhost:8080/api/dashboard/rising-skills?startYear=2015&endYear=2025&limit=10"
   ```

4. **Top fallende Skills**
   ```bash
   curl "http://localhost:8080/api/dashboard/falling-skills?startYear=2015&endYear=2025&limit=10"
   ```

5. **Digitalisierungsrate**
   ```bash
   curl "http://localhost:8080/api/dashboard/digitalization?startYear=2015&endYear=2025"
   ```

6. **Level-Verteilung**
   ```bash
   curl "http://localhost:8080/api/dashboard/level-distribution?startYear=2015&endYear=2025"
   ```

7. **Verfügbare Jahre**
   ```bash
   curl "http://localhost:8080/api/dashboard/available-years"
   ```

---

### **8. Excel-Export für Poster**

```bash
# Dashboard-Daten exportieren
curl "http://localhost:8080/api/dashboard/export?startYear=2015&endYear=2025" \
  -o dashboard_2015_2025.json

# Mit Python in Excel konvertieren
python -c "
import json
import pandas as pd

with open('dashboard_2015_2025.json') as f:
    data = json.load(f)

# Yearly Trends → Excel
df = pd.DataFrame(data['yearlyTrends'])
df.to_excel('yearly_trends.xlsx', index=False)

# Top Rising Skills → Excel
df = pd.DataFrame(data['topRisingSkills'])
df.to_excel('rising_skills.xlsx', index=False)

print('✅ Excel-Export abgeschlossen')
"
```

---

## 📊 POSTER-VISUALISIERUNGEN (Tag 16-18)

### **9. Diagramme erstellen**

**Mit Excel/Python (Matplotlib):**

1. **Zeitreihen-Diagramm**
   - X-Achse: Jahre (2015-2025)
   - Y-Achse: Anzahl Jobs
   - Linien: Top-10-Skills

2. **Digitalisierungs-Trend**
   - X-Achse: Jahre
   - Y-Achse: % digitale Skills
   - Balkendiagramm

3. **7-Ebenen-Modell**
   - Gestapeltes Balkendiagramm
   - Farben: Ebene 1-5
   - Pro Jahr

4. **Top-10-Skills 2025 vs. 2015**
   - Horizontales Balkendiagramm
   - Vergleich

---

## 🎯 POSTERSESSION-CHECKLISTE

### **Must-Have (bis 14. Jan):**
- [ ] Datenbank-Schema migriert
- [ ] Python-Dependencies installiert (inkl. SpaCy)
- [ ] Kotlin-App kompiliert und läuft
- [ ] Python-Backend läuft
- [ ] Mindestens 300 Jobs gesammelt (50/Jahr × 6 Jahre)
- [ ] Batch-Processing erfolgreich ausgeführt
- [ ] Dashboard-Endpoints funktionieren
- [ ] Mindestens 3 Visualisierungen erstellt
- [ ] README aktualisiert

### **Nice-to-Have:**
- [ ] 550 Jobs gesammelt (50/Jahr × 11 Jahre)
- [ ] Excel-Export funktioniert
- [ ] Alle 7 Ebenen im Dashboard sichtbar
- [ ] Poster gedruckt

---

## 🚨 TROUBLESHOOTING

### **Problem: Datenbank-Migration schlägt fehl**

**Lösung:**
```sql
-- Prüfe, ob Spalten bereits existieren
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'competence';

-- Falls ja, überspringe ALTER TABLE-Statements
```

---

### **Problem: SpaCy-Modell nicht gefunden**

**Lösung:**
```bash
# Manuell herunterladen
python -m spacy download de_core_news_md

# Alternative: Kleineres Modell
python -m spacy download de_core_news_sm

# In main.py ändern:
nlp = spacy.load("de_core_news_sm")
```

---

### **Problem: Keine Jobs in Datenbank**

**Lösung:**
```bash
# Prüfe, ob Jobs geladen wurden
psql -U jobmining_user -d jobmining_db -c "SELECT COUNT(*) FROM job_posting;"

# Falls 0: Batch-Processing erneut ausführen
curl -X POST http://localhost:8000/batch-process

# Logs prüfen
docker logs python-backend
```

---

### **Problem: Dashboard zeigt keine Daten**

**Lösung:**
```sql
-- Prüfe verfügbare Jahre
SELECT DISTINCT EXTRACT(YEAR FROM posting_date) FROM job_posting;

-- Falls keine: Batch-Processing ausführen

-- Falls vorhanden: Prüfe Competences
SELECT COUNT(*) FROM competence;
```

---

## 📚 DOKUMENTATION FÜR THESIS

### **Architektur-Begründungen:**
- `POC_VS_MAIN_ANALYSE.md` - Feature-Vergleich
- `GEMINI_ARCHITEKTUR_ERKENNTNISSE.md` - Design-Entscheidungen
- `MIGRATION_ABGESCHLOSSEN.md` - Migration-Dokumentation

### **Code-Referenz:**
- `migration.sql` - Datenbank-Schema
- `TrendDTO.kt` - DTOs
- `TrendAnalysisService.kt` - Business-Logik
- `DashboardController.kt` - REST-API

### **Methodik:**
- Intelligente Pipeline V13.3 (Sektions-Filter, Rollen-Brille, NLP-Parsing)
- 7-Ebenen-Modell (Discovery → Idempotenz)
- CRISP-DM-Prozess
- Domain-Driven Design

---

## 🎓 ZUSAMMENFASSUNG

### **Status:**
- ✅ Code: 100% fertig
- ⏳ Daten: 0% (müssen gesammelt werden)
- ⏳ Tests: 20% (Dashboard-Endpoints vorhanden)
- ⏳ Visualisierungen: 0% (müssen erstellt werden)

### **Nächster Schritt:**
**SOFORT: Datenbank-Schema migrieren + Dependencies installieren!**

```bash
# 1. Datenbank
psql -U jobmining_user -d jobmining_db -f migration.sql

# 2. Python
cd python-backend && pip install -r requirements.txt && python -m spacy download de_core_news_md

# 3. Kotlin
cd kotlin-api && ./gradlew clean build && ./gradlew bootRun
```

**Danach: Historische Stellenanzeigen sammeln!**

---

**Erstellt von:** Claude
**Für:** Bernd
**Projekt:** job-mining-kotlin-python
**Deadline:** 14. Januar 2025 (Postersession)
