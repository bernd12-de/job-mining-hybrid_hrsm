# 📊 POC vs. MAIN PROJECT - Architektur-Analyse

**Datum:** 2024-12-27
**Branch:** claude/fix-kotlin-python-api-b6uDC
**Analysiert:** docs/ideas/proof-of-concept/ vs. kotlin-api/ & python-backend/

---

## 🎯 EXECUTIVE SUMMARY

### ⚠️ KRITISCHER BEFUND:

**Der Proof-of-Concept (POC) ist WESENTLICH fortgeschrittener als das Hauptprojekt!**

- ✅ POC hat vollständige Clean Architecture
- ✅ POC hat alle 7 Ebenen (Discovery → Idempotenz) implementiert
- ✅ POC hat Metadaten-Extraktion, Segmentierung, Skill-Levels
- ✅ POC hat umfangreiche Tests (13 Test-Dateien)
- ❌ Hauptprojekt hat nur API-Grundgerüst (DTOs, Services, Controller)

### 📅 FÜR POSTERSESSION (14. Januar 2025):

**EMPFEHLUNG: POC-Code ins Hauptprojekt migrieren!**

Der POC enthält genau die Funktionen, die laut Exposé für die Postersession benötigt werden:
- ✅ Metadaten-Extraktion (Datum, Ort, Rolle, Branche)
- ✅ Kompetenz-Levels (1-5) für wissenschaftliche Validierung
- ✅ Dokumenttyp-Erkennung (Stellenanzeige, Fachbuch, Modulhandbuch)
- ✅ Trend-Analyse Service (Grundlagen für Zeitreihen)
- ✅ Idempotenz (SHA-256 Hash) für Duplikat-Erkennung
- ⚠️ Zeitreihen-Analyse noch nicht vollständig (aber Basis vorhanden)

---

## 📂 STRUKTUR-VERGLEICH

### POC-Architektur (Clean Architecture):

```
docs/ideas/proof-of-concept/
├── app/
│   ├── domain/                    # 🟢 FINAL
│   │   └── models.py             # AnalysisResultDTO, CompetenceDTO mit Levels
│   ├── application/               # 🟢 FINAL
│   │   ├── job_mining_workflow_manager.py  # CRISP-DM Pipeline
│   │   ├── factories/
│   │   │   └── analysis_result_factory.py
│   │   └── services/
│   │       ├── esco_service.py
│   │       ├── organization_service.py
│   │       └── role_service.py
│   ├── infrastructure/            # 🟡 TEILWEISE FINAL
│   │   ├── extractor/
│   │   │   ├── metadata_extractor.py        # 🟢 FINAL - Datum, Ort, Rolle
│   │   │   ├── competence_extractor.py      # 🟢 FINAL
│   │   │   ├── spacy_competence_extractor.py # 🟢 FINAL
│   │   │   └── discovery_extractor.py       # 🟡 POC - Ebene 1
│   │   ├── repositories/
│   │   │   └── hybrid_competence_repository.py  # 🟢 FINAL
│   │   └── clients/
│   │       └── kotlin_rule_client.py        # 🟢 FINAL
│   ├── core/                      # 🟢 FINAL
│   │   ├── constants.py          # Blacklists, Patterns
│   │   ├── normalize.py          # Datum-Parser
│   │   └── skill_filter.py
│   └── interfaces/                # 🟢 FINAL
│       └── interfaces.py
│
├── kotlinapi/                     # 🟢 FINAL
│   ├── domain/
│   │   ├── JobPosting.kt         # 🟢 FINAL - Bidirektionale Relations
│   │   ├── Competence.kt         # 🟢 FINAL - Ebenen-Felder
│   │   └── EscoSkill.kt
│   ├── services/
│   │   ├── JobMiningService.kt   # 🟢 FINAL - Komplette Workflows
│   │   ├── TrendAnalysisService.kt  # 🟡 POC - Nur Grundlagen
│   │   └── HybridCompetenceService.kt
│   ├── adapters/
│   │   └── PythonAnalysisClient.kt  # 🟢 FINAL
│   └── presentation/
│       ├── JobController.kt
│       └── DomainRuleController.kt
│
├── tests/                         # 🟢 FINAL
│   ├── test_7_ebenen.py          # Validiert alle 7 Ebenen
│   ├── test_competence_levels.py
│   ├── test_db_compatibility.py
│   └── test_architecture_contracts.py
│
└── main.py                        # 🟢 FINAL - Vollständiger FastAPI-Server
```

### Hauptprojekt-Architektur (Basis):

```
kotlin-api/src/main/kotlin/de/layher/jobmining/kotlinapi/
├── domain/
│   └── Competence.kt              # ❌ VERALTET - Fehlt Ebenen-Felder
├── dto/
│   ├── CompetenceDTO.kt           # ❌ VERALTET - Keine Levels
│   └── AnalysisResultDTO.kt       # ❌ VERALTET - Keine is_segmented
├── service/
│   ├── PythonApiClient.kt         # ⚠️ FUNKTIONAL - Aber simpel
│   └── JobMiningService.kt        # ⚠️ FUNKTIONAL - Keine Ebenen-Logik
├── controller/
│   └── JobMiningController.kt     # ⚠️ FUNKTIONAL - Basis-Endpoints
├── repository/
│   └── JobPostingRepository.kt    # ⚠️ FUNKTIONAL
└── JobPosting.kt                  # ❌ FALSCH PLATZIERT - Gehört in domain/

python-backend/
├── main.py                        # ❌ VERALTET - Keine Ebenen-Logik
├── fuzzy_competence_extractor.py  # ❌ VERALTET - Nur Fuzzy-Matching
├── repositories/
│   └── esco_skills.py             # ⚠️ FUNKTIONAL - ESCO-Daten laden
└── data/                          # ✅ KORREKT - ESCO CSVs vorhanden
```

---

## 🔍 FEATURE-VERGLEICH: POC vs. MAIN

| Feature | POC | Main Project | Status |
|---------|-----|--------------|--------|
| **ESCO-Integration** | ✅ HybridCompetenceRepository | ✅ esco_skills.py | 🟢 BEIDE OK |
| **Metadaten-Extraktion** | ✅ metadata_extractor.py | ❌ Nur Placeholders | 🔴 POC BESSER |
| **Datum-Parsing** | ✅ normalize.parse_date() | ❌ Hardcoded "2024-12-01" | 🔴 POC BESSER |
| **Ort-Extraktion** | ✅ Regex mit 10+ Städten | ❌ "Placeholder" | 🔴 POC BESSER |
| **Rollen-Klassifikation** | ✅ role_service.py | ❌ "Placeholder" | 🔴 POC BESSER |
| **Branchen-Erkennung** | ✅ organization_service.py | ❌ "Placeholder" | 🔴 POC BESSER |
| **Dokumenttyp-Erkennung** | ✅ Fachbuch/Modulhandbuch | ❌ Nur Job-Posting | 🔴 POC BESSER |
| **Kompetenz-Levels (1-5)** | ✅ level, is_digital, is_discovery | ❌ Keine Ebenen | 🔴 POC BESSER |
| **Segmentierung** | ✅ Tasks vs Requirements | ❌ Kein Segmenting | 🔴 POC BESSER |
| **Idempotenz (SHA-256)** | ✅ raw_text_hash | ❌ Kein Hash | 🔴 POC BESSER |
| **Discovery (Ebene 1)** | ✅ discovery_extractor.py | ❌ Nicht vorhanden | 🔴 POC BESSER |
| **Fuzzy-Matching** | ✅ Ebene 2 | ✅ fuzzy_competence_extractor.py | 🟢 BEIDE OK |
| **SpaCy NLP** | ✅ spacy_competence_extractor.py | ❌ Import ungenutzt | 🔴 POC BESSER |
| **Trend-Analyse** | 🟡 TrendAnalysisService.kt (Basic) | ❌ Nicht vorhanden | 🟡 POC ANSÄTZE |
| **Factory-Pattern** | ✅ AnalysisResultFactory | ❌ Manuell im Service | 🔴 POC BESSER |
| **Blacklisting** | ✅ GLOBAL_BLACKLIST | ❌ Nicht vorhanden | 🔴 POC BESSER |
| **JPA-Entities** | ✅ Bidirektional (class) | ⚠️ data class (falsch) | 🔴 POC BESSER |
| **Tests** | ✅ 13 Test-Dateien | ❌ Keine Tests | 🔴 POC BESSER |
| **Batch-Processing** | ✅ Lokale Ordner | ❌ Nicht vorhanden | 🔴 POC BESSER |
| **API-Endpoints** | ✅ /analyse/file, /scrape, /batch | ⚠️ Nur /analyse | 🟡 POC MEHR |
| **Logging** | ✅ logging.getLogger(__name__) | ❌ Kein Logging | 🔴 POC BESSER |
| **Error-Handling** | ✅ Try/Catch mit HTTPException | ⚠️ Basis-Handling | 🟡 POC BESSER |

### 📊 ZUSAMMENFASSUNG:

- **POC ist besser:** 20 Features
- **Beide OK:** 2 Features
- **Main ist besser:** 0 Features

**FAZIT:** Der POC ist in JEDEM Aspekt mindestens gleichwertig oder besser!

---

## 🏷️ STATUS-KATEGORISIERUNG

### 🟢 FINAL (Produktions-Ready):

Diese Komponenten sind **bereit für die Hauptprojekt-Integration**:

#### Python:
1. **app/domain/models.py**
   - Vollständige DTOs mit Pydantic-Validierung
   - Ebenen-Felder (level, is_digital, is_discovery, source_domain)
   - @field_validator für Kotlin-Kompatibilität
   - SHA-256 Hash-Generator

2. **app/infrastructure/extractor/metadata_extractor.py**
   - Datum-Extraktion (parse_date)
   - Ort-Extraktion (10+ deutsche Städte)
   - Jobtitel-Extraktion
   - Branchen-Erkennung
   - Dokumenttyp-Erkennung (Fachbuch/Modulhandbuch)
   - Segmentierung (Tasks vs Requirements)

3. **app/application/job_mining_workflow_manager.py**
   - Zentrale CRISP-DM Pipeline
   - Orchestriert: Text → Metadaten → NLP → Factory
   - Idempotenz-Check (Hash)
   - Factory-Pattern für DTOs

4. **app/infrastructure/repositories/hybrid_competence_repository.py**
   - ESCO-Daten laden (CSV)
   - Lokale Domänen (Fachbuch, Modulhandbuch)
   - Fuzzy-Matching mit RapidFuzz
   - Level-Logik (Ebenen 2, 4, 5)

5. **app/core/constants.py**
   - GLOBAL_BLACKLIST (Rauschen filtern)
   - LOCATION_PATTERNS (Regex für Orte)
   - JOB_CATEGORY_PATTERNS (10 Kategorien)
   - TASK_SECTION_PATTERN / REQUIREMENTS_SECTION_PATTERN

6. **app/core/normalize.py**
   - parse_date() für ISO-Format (YYYY-MM-DD)
   - Unterstützt: DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD, "01. Januar 2024"
   - Robust gegen Fehler

7. **app/infrastructure/extractor/spacy_competence_extractor.py**
   - SpaCy-basierte Extraktion
   - Nutzt PhraseMatcher für Performance
   - Ebenen-Logik (2, 4, 5)
   - Digital-Skill Detection

8. **app/application/services/role_service.py**
   - Rollen-Klassifikation (IT, UX/UI, Management, Finanzen, Assistenz)
   - Regex-basiert mit JOB_CATEGORY_PATTERNS

9. **app/application/services/organization_service.py**
   - Branchen-Erkennung
   - Firmen-Namen-Extraktion (AG, GmbH, Group, KG)

10. **main.py (POC-Version)**
    - Vollständiger FastAPI-Server
    - Clean Architecture DI (Dependency Injection)
    - Endpoints: /analyse/file, /analyse/text, /analyse/scrape-url, /batch-process
    - Health-Check mit ESCO-Count

#### Kotlin:
1. **kotlinapi/domain/JobPosting.kt (POC-Version)**
   - `class JobPosting` (nicht data class!)
   - Bidirektionale Relation zu Competence
   - `@JsonManagedReference` / `@JsonBackReference`
   - rawTextHash als UNIQUE constraint
   - isSegmented-Feld

2. **kotlinapi/domain/Competence.kt (POC-Version)**
   - Ebenen-Felder: level, isDigital, isDiscovery
   - sourceDomain (Ebene 4/5)
   - roleContext (Ebene 6)

3. **kotlinapi/services/JobMiningService.kt (POC-Version)**
   - processJobAd() mit Idempotenz-Check
   - processScrapedUrl() für Web-Scraping
   - processJobDirectoryBatch() für Zeitreihen-Daten
   - Logging & Feedback
   - DTO → Entity Mapping mit allen Ebenen-Feldern

4. **kotlinapi/adapters/PythonAnalysisClient.kt**
   - HTTP-Client für Python-Backend
   - sendDocumentForAnalysis()
   - scrapeAndAnalyzeUrl()
   - processLocalJobDirectory()

### 🟡 POC (Funktioniert, aber nicht vollständig):

Diese Komponenten sind **verwendbar, aber benötigen Erweiterung**:

1. **kotlinapi/services/TrendAnalysisService.kt**
   - **Was funktioniert:** Basis-Logik für Digitalisierungs-Rate
   - **Was fehlt:** Zeitreihen-Aggregation (Jahres-Trends 2015-2025)
   - **Für Jan 14:** Muss erweitert werden mit:
     - Group by Year (posting_date)
     - Top-10-Skills pro Jahr
     - Trend-Berechnung (Anstieg/Rückgang)
     - Export für Dashboard (JSON/CSV)

2. **app/infrastructure/extractor/discovery_extractor.py**
   - **Was funktioniert:** Erkennt neue Begriffe (Ebene 1)
   - **Was fehlt:** Validierung der Qualität (viele False Positives)
   - **Für Jan 14:** Optional (kann später verfeinert werden)

3. **Tests (test_7_ebenen.py, test_competence_levels.py)**
   - **Was funktioniert:** Mocks für alle Ebenen
   - **Was fehlt:** Integration-Tests mit echter DB
   - **Für Jan 14:** Muss mit echter PostgreSQL getestet werden

### 🔵 KONZEPT (Nur Idee, nicht implementiert):

Diese Komponenten sind **Referenz-Material**:

1. **docs/ideas/architectural-patterns/*.docx**
   - Architektur-Überlegungen
   - Event-Driven, CQRS, Microservices
   - Nicht für Postersession relevant

2. **docs/ideas/module-handbook-support/**
   - ModuleHandbook.kt (Konzept-Entity)
   - document_classifier.py (Konzept-Code)
   - Für spätere Phasen (nach Postersession)

---

## 🚀 MIGRATIONS-PLAN FÜR POSTERSESSION (Jan 14)

### Phase 1: SOFORT (KW 1 - bis 3. Januar)

**Ziel:** Kern-Funktionalität von POC ins Hauptprojekt übertragen

#### 1.1 Python-Backend ersetzen
```bash
# Backup erstellen
cp -r python-backend python-backend-BACKUP

# POC-Code übertragen
cp -r docs/ideas/proof-of-concept/app/* python-backend/app/
cp docs/ideas/proof-of-concept/main.py python-backend/main.py

# Dependencies aktualisieren
pip install spacy rapidfuzz pydantic
python -m spacy download de_core_news_md
```

**Dateien:**
- ✅ main.py → Python-Backend (FINAL-Version)
- ✅ app/domain/models.py → DTOs mit Ebenen
- ✅ app/application/job_mining_workflow_manager.py → Pipeline
- ✅ app/infrastructure/extractor/metadata_extractor.py → Metadaten
- ✅ app/infrastructure/repositories/hybrid_competence_repository.py → ESCO
- ✅ app/core/constants.py → Patterns & Blacklists
- ✅ app/core/normalize.py → Datum-Parser

#### 1.2 Kotlin-API aktualisieren
```bash
# Domain-Entities aus POC
cp docs/ideas/proof-of-concept/kotlinapi/domain/JobPosting.kt \
   kotlin-api/src/main/kotlin/.../domain/JobPosting.kt

cp docs/ideas/proof-of-concept/kotlinapi/domain/Competence.kt \
   kotlin-api/src/main/kotlin/.../domain/Competence.kt

# Services aus POC
cp docs/ideas/proof-of-concept/kotlinapi/services/JobMiningService.kt \
   kotlin-api/src/main/kotlin/.../service/JobMiningService.kt
```

**Anpassungen:**
1. **JobPosting.kt:** `data class` → `class` (für JPA Bidirektional)
2. **Competence.kt:** Ebenen-Felder hinzufügen (level, isDigital, isDiscovery)
3. **DTOs:** Ebenen-Felder hinzufügen
4. **JobMiningService.kt:** Idempotenz-Check hinzufügen

#### 1.3 Datenbank-Schema erweitern
```sql
-- Migration: Ebenen-Felder zu Competence
ALTER TABLE competence ADD COLUMN level INTEGER DEFAULT 2;
ALTER TABLE competence ADD COLUMN is_digital BOOLEAN DEFAULT FALSE;
ALTER TABLE competence ADD COLUMN is_discovery BOOLEAN DEFAULT FALSE;
ALTER TABLE competence ADD COLUMN source_domain VARCHAR(255);
ALTER TABLE competence ADD COLUMN role_context VARCHAR(255);

-- Migration: Felder zu JobPosting
ALTER TABLE job_posting ADD COLUMN is_segmented BOOLEAN DEFAULT FALSE;
```

### Phase 2: KRITISCH (KW 2 - bis 10. Januar)

**Ziel:** Zeitreihen-Analyse implementieren (KERN DER THESIS!)

#### 2.1 Trend-Analyse erweitern

**File:** `kotlin-api/src/main/kotlin/.../service/TrendAnalysisService.kt`

```kotlin
@Service
class TrendAnalysisService(
    private val jobRepo: JobPostingRepository,
    private val compRepo: CompetenceRepository
) {
    // NEU: Zeitreihen-Analyse (2015-2025)
    @Transactional(readOnly = true)
    fun analyzeCompetenceTrends(startYear: Int, endYear: Int): List<YearlyTrendDTO> {
        val trends = mutableListOf<YearlyTrendDTO>()

        for (year in startYear..endYear) {
            val jobs = jobRepo.findByPostingDateYear(year)
            val competences = jobs.flatMap { it.competences }

            val topSkills = competences
                .groupBy { it.escoLabel }
                .mapValues { it.value.size }
                .entries.sortedByDescending { it.value }
                .take(10)

            trends.add(YearlyTrendDTO(
                year = year,
                totalJobs = jobs.size,
                topSkills = topSkills.map {
                    SkillCountDTO(it.key, it.value)
                }
            ))
        }

        return trends
    }
}
```

#### 2.2 Repository-Queries

**File:** `kotlin-api/src/main/kotlin/.../repository/JobPostingRepository.kt`

```kotlin
interface JobPostingRepository : JpaRepository<JobPosting, Long> {
    @Query("SELECT j FROM JobPosting j WHERE YEAR(j.postingDate) = :year")
    fun findByPostingDateYear(year: Int): List<JobPosting>

    @Query("""
        SELECT c.escoLabel, COUNT(c) as cnt
        FROM Competence c
        JOIN c.jobPosting j
        WHERE YEAR(j.postingDate) BETWEEN :startYear AND :endYear
        GROUP BY c.escoLabel
        ORDER BY cnt DESC
    """)
    fun findTopCompetencesByYearRange(
        startYear: Int,
        endYear: Int,
        limit: Pageable
    ): List<Array<Any>>
}
```

#### 2.3 Test-Daten sammeln

**Kritisch:** Echte Stellenanzeigen von 2015-2025 benötigt!

**Quellen:**
- Archive.org (Wayback Machine)
- StepStone, Indeed, LinkedIn (ältere Anzeigen)
- Hochschul-Archive (FH Gummersbach)

**Format:**
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

**Batch-Processing:**
```bash
# Über POC-Main ausführen
POST http://localhost:8000/batch-process

# Kotlin ruft Python auf:
POST http://localhost:8080/api/job-mining/batch
```

### Phase 3: FINALISIERUNG (KW 3 - bis 14. Januar)

**Ziel:** Dokumentation, Dashboard, Poster

#### 3.1 Dashboard (Minimal)

**Option 1: Kotlin-Controller mit JSON**
```kotlin
@GetMapping("/dashboard/trends")
fun getTrends(@RequestParam startYear: Int, @RequestParam endYear: Int) =
    trendService.analyzeCompetenceTrends(startYear, endYear)
```

**Option 2: Excel-Export**
```kotlin
@GetMapping("/dashboard/export")
fun exportTrendsToExcel(): ResponseEntity<ByteArray> {
    val trends = trendService.analyzeCompetenceTrends(2015, 2025)
    val workbook = createExcelWorkbook(trends)
    return ResponseEntity.ok()
        .header("Content-Disposition", "attachment; filename=trends.xlsx")
        .body(workbook.toByteArray())
}
```

#### 3.2 Dokumentation aktualisieren

**README.md:**
```markdown
# Job-Mining Projekt

## Features (Postersession)
- ✅ ESCO-Integration (35.000+ Skills)
- ✅ Metadaten-Extraktion (Datum, Ort, Rolle, Branche)
- ✅ 7-Ebenen-Modell (Discovery → Idempotenz)
- ✅ Zeitreihen-Analyse (2015-2025)
- ✅ Dokumenttyp-Erkennung (Job, Fachbuch, Modulhandbuch)
- ✅ Segmentierung (Aufgaben vs. Anforderungen)

## Setup
1. Docker-Compose starten: `docker-compose up`
2. ESCO-Daten laden (automatisch beim Start)
3. Batch-Analyse: `POST /api/job-mining/batch`
4. Trends abrufen: `GET /dashboard/trends?startYear=2015&endYear=2025`
```

#### 3.3 Poster-Inhalte vorbereiten

**Visualisierungen:**
- Zeitreihen-Diagramm (Top-10-Skills pro Jahr)
- 7-Ebenen-Modell (Grafik)
- Architektur-Diagramm (Kotlin + Python + PostgreSQL)

**Key Metrics:**
- Anzahl analysierter Jobs (gesamt & pro Jahr)
- ESCO-Skills erkannt (35.000+)
- Genauigkeit (% korrekt klassifiziert)
- Processing-Zeit (Sekunden pro Job)

---

## ⚠️ RISIKOANALYSE

### 🔴 HOCH (Muss funktionieren):

1. **POC → Main Migration**
   - **Risiko:** Breaking Changes bei Integration
   - **Mitigation:** Tests aus POC übernehmen, schrittweise migrieren
   - **Zeit:** 3-5 Tage

2. **Zeitreihen-Daten**
   - **Risiko:** Keine historischen Stellenanzeigen verfügbar
   - **Mitigation:**
     - Archive.org / Wayback Machine nutzen
     - Falls nicht genug: Synthetische Daten mit Trends generieren
     - Mindestens 50 Jobs pro Jahr (2015-2025 = 550 Jobs)
   - **Zeit:** 2-3 Tage

3. **Trend-Analyse-Logik**
   - **Risiko:** Komplexe SQL-Queries für Aggregation
   - **Mitigation:** POC-Service erweitern (bereits Basis vorhanden)
   - **Zeit:** 2 Tage

### 🟡 MITTEL (Kann fehlen, aber wichtig):

4. **Dashboard**
   - **Risiko:** Keine Zeit für UI
   - **Mitigation:** Nur JSON-API + Excel-Export
   - **Zeit:** 1 Tag

5. **ChatGPT-Integration**
   - **Risiko:** Nicht implementiert, aber im Exposé erwähnt
   - **Mitigation:** Für Postersession "Future Work" deklarieren
   - **Zeit:** 0 Tage (verschieben auf später)

### 🟢 NIEDRIG (Optional):

6. **Discovery-Extractor (Ebene 1)**
   - **Risiko:** Zu viele False Positives
   - **Mitigation:** Für Postersession deaktivieren, nur Ebenen 2-7 zeigen
   - **Zeit:** 0 Tage (später verfeinern)

---

## 📋 CHECKLISTE FÜR POSTERSESSION

### Must-Have (bis 14. Januar):
- [ ] POC-Code ins Hauptprojekt migriert
- [ ] Metadaten-Extraktion funktioniert (Datum, Ort, Rolle)
- [ ] ESCO-Integration funktioniert (35.000+ Skills)
- [ ] Zeitreihen-Daten gesammelt (mind. 50 Jobs pro Jahr, 2015-2025)
- [ ] Trend-Analyse implementiert (Top-10-Skills pro Jahr)
- [ ] Batch-Processing funktioniert
- [ ] Idempotenz (SHA-256 Hash) funktioniert
- [ ] Tests durchgeführt (mind. test_7_ebenen.py)
- [ ] README.md aktualisiert
- [ ] Poster-Visualisierungen erstellt

### Nice-to-Have (wenn Zeit):
- [ ] Dashboard (JSON-API)
- [ ] Excel-Export
- [ ] Segmentierung (Tasks vs Requirements)
- [ ] Dokumenttyp-Erkennung (Fachbuch/Modulhandbuch)
- [ ] Docker-Compose funktioniert

### Später (nach Postersession):
- [ ] ChatGPT-Integration
- [ ] Discovery-Extractor verfeinern
- [ ] Web-UI für Dashboard
- [ ] Deployment auf Server

---

## 🎓 ZUSAMMENFASSUNG

### Status: POC vs. Main

| Aspekt | POC | Main | Empfehlung |
|--------|-----|------|------------|
| **Architektur** | Clean Architecture | Basis-API | POC übernehmen |
| **Funktionalität** | 7 Ebenen | Nur Fuzzy-Matching | POC übernehmen |
| **Metadaten** | Vollständig | Placeholders | POC übernehmen |
| **Zeitreihen** | Grundlagen | Nicht vorhanden | POC erweitern |
| **Tests** | 13 Test-Dateien | Keine | POC übernehmen |
| **Dokumentation** | Gut | Minimal | POC übernehmen |

### Zeitplan:

- **KW 1 (bis 3. Jan):** POC → Main Migration
- **KW 2 (bis 10. Jan):** Zeitreihen-Analyse + Daten sammeln
- **KW 3 (bis 14. Jan):** Dashboard + Dokumentation + Poster

### Erfolgskritisch:

1. ✅ POC-Code ist **bereit** für Integration
2. ⚠️ Zeitreihen-Daten müssen **gesammelt** werden
3. ⚠️ Trend-Analyse muss **erweitert** werden

**NÄCHSTER SCHRITT:** Migration starten (Phase 1)!

---

**Erstellt von:** Claude
**Für:** Bernd
**Projekt:** job-mining-kotlin-python
**Deadline:** 14. Januar 2025 (Postersession)
