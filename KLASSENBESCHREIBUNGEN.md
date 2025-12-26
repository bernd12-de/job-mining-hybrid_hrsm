# Klassenbeschreibungen - Job Mining System

## Übersicht
Dieses Dokument beschreibt alle wichtigen Klassen des Job Mining Systems, das aus einem Python-Backend (FastAPI) und einem Kotlin-Backend (Spring Boot) besteht.

---

## Python Backend Klassen

### 1. DTOs (models.py)

#### CompetenceDTO
**Zweck**: Data Transfer Object für den Transport von Kompetenz-Informationen zwischen Python- und Kotlin-Backend

**Attribute**:
- `original_term: str` - Der Begriff, wie er im Stellenanzeigen-Text gefunden wurde (z.B. "Figma Tool")
- `confidence_score: float` - Vertrauensscore des Matches (0.0 - 1.0)
- `esco_label: str` - Das offizielle ESCO-Label oder Custom-Label
- `esco_uri: str` - Eindeutige ESCO URI (z.B. "http://data.europa.eu/esco/skill/...")
- `esco_group_code: Optional[str]` - ESCO Gruppencode für hierarchische Analyse (z.B. "T2.1")

**Verwendung**: Wird vom FuzzyCompetenceExtractor erstellt und im AnalysisResultDTO zurückgegeben

---

#### AnalysisResultDTO
**Zweck**: Gesamtergebnis einer Stellenanzeigen-Analyse

**Attribute**:
- `title: str` - Titel der Stellenanzeige
- `job_role: str` - Rolle/Position (aktuell Placeholder)
- `region: str` - Region (aktuell Placeholder)
- `industry: str` - Branche (aktuell Placeholder)
- `posting_date: str` - Veröffentlichungsdatum
- `raw_text_hash: str` - Hash des Rohtextes für Idempotenz-Prüfung
- `competences: List[CompetenceDTO]` - Liste der gefundenen Kompetenzen

**Verwendung**: Wird vom JobMiningWorkflowManager erstellt und als API-Response zurückgegeben

---

### 2. Interfaces (interfaces.py)

#### ITextExtractor
**Zweck**: Interface für die Dokumentenverarbeitung (PDF, DOCX)

**Methoden**:
- `extract_text(file_stream: BinaryIO, filename: str) -> str` - Extrahiert Text aus Dateien

**Implementierungen**: AdvancedTextExtractor

---

#### ICompetenceExtractor
**Zweck**: Interface für die NLP-gestützte Kompetenzextraktion

**Methoden**:
- `extract_competences(text: str) -> List[CompetenceDTO]` - Extrahiert Kompetenzen aus Text

**Implementierungen**: FuzzyCompetenceExtractor

---

#### IJobMiningWorkflowManager
**Zweck**: Interface zur Steuerung der gesamten Analyse-Pipeline

**Methoden**:
- `run_full_analysis(file_stream: BinaryIO, filename: str) -> AnalysisResultDTO` - Führt vollständige Analyse durch

**Implementierungen**: JobMiningWorkflowManager

---

### 3. Workflow Manager (job_mining_workflow_manager.py)

#### JobMiningWorkflowManager
**Zweck**: Orchestrierung der Analyse-Pipeline nach CRISP-DM Zyklus

**Abhängigkeiten** (Dependency Injection):
- `text_extractor: ITextExtractor` - Service für Text-Extraktion
- `competence_extractor: ICompetenceExtractor` - Service für Kompetenz-Extraktion

**Methoden**:
- `run_full_analysis(file_stream: BinaryIO, filename: str) -> AnalysisResultDTO`

**Ablauf**:
1. Text-Parsing via TextExtractor (PDF/DOCX)
2. Hash-Generierung für Idempotenz
3. Metadaten-Extraktion (TODO: Rolle, Region, Datum)
4. Kompetenz-Extraktion via CompetenceExtractor
5. Rückgabe des AnalysisResultDTO

**Pattern**: Facade Pattern, Dependency Injection

---

### 4. Text Extraktion (advanced_text_extractor.py)

#### AdvancedTextExtractor
**Zweck**: Robuste Implementierung der Text-Extraktion aus verschiedenen Dateiformaten

**Unterstützte Formate**:
- PDF (.pdf) - via pypdf.PdfReader
- Word (.docx) - via python-docx.Document
- Plain Text (.txt, .csv) - via UTF-8 Decoding
- Fallback für unbekannte Formate

**Methoden**:
- `extract_text(file_stream: BinaryIO, filename: str) -> str` - Hauptmethode
- `_extract_from_pdf(file_stream: BinaryIO) -> str` - PDF-spezifische Logik
- `_extract_from_docx(file_stream: BinaryIO) -> str` - DOCX-spezifische Logik

**Fehlerbehandlung**: Robustes Exception-Handling mit Fallbacks

**TODO**: OCR-Fallback für gescannte PDFs (Phase 3)

---

### 5. Kompetenz-Extraktion (fuzzy_competence_extractor.py)

#### FuzzyCompetenceExtractor
**Zweck**: Keyword-Matching gegen die Hybrid ESCO-Datenbank mit zukünftiger Fuzzy-Matching-Unterstützung

**Abhängigkeiten**:
- `repository: HybridCompetenceRepository` - Wissensbasis (ESCO + Custom Skills)
- `nlp: spacy.Language` - Optional für Lemmatisierung (aktuell deaktiviert)

**Interne Strukturen**:
- `keyword_map: Dict[str, Competence]` - Flache Map aller Keywords für schnelle Suche

**Methoden**:
- `extract_competences(text: str) -> List[CompetenceDTO]` - Hauptmethode
- `_build_keyword_map() -> Dict[str, Competence]` - Erstellt Keyword-Index

**Algorithmus (MVP)**:
1. Direktes Keyword-Matching (case-insensitive)
2. Deduplizierung via ESCO URI
3. Mapping auf CompetenceDTO mit 100% Confidence

**TODO**:
- Fuzzy Matching (fuzzywuzzy)
- TF-IDF Vectorization
- Spacy Lemmatisierung

---

### 6. Repository (repositories/hybrid_competence_repository.py)

#### Competence (Domain Entity)
**Zweck**: Interne DDD-Entität zur Repräsentation einer Kompetenz

**Attribute**:
- `preferred_label: str` - Hauptbezeichnung
- `esco_uri: str` - Eindeutige URI
- `group_code: str` - ESCO Gruppencode (optional)
- `synonyms: List[str]` - Alternative Bezeichnungen
- `keywords: List[str]` - Alle durchsuchbaren Keywords (preferred + synonyms, lowercase)

---

#### ICompetenceRepository
**Zweck**: Interface für Kompetenz-Datenquellen

**Methoden**:
- `get_all_competences() -> List[Competence]` - Liefert alle Kompetenzen

---

#### HybridCompetenceRepository
**Zweck**: Lädt und vereint ESCO-Standarddaten mit Custom Skills

**Datenquellen**:
- ESCO Skills (skills_de.csv) - ~14.000 Einträge
- ESCO Skill Groups (skillGroups_de.csv) - Hierarchie
- Custom Skills (custom_skills_extended.json) - Future/moderne Begriffe

**Methoden**:
- `get_all_competences() -> List[Competence]` - Gibt alle geladenen Kompetenzen zurück
- `_load_data()` - Orchestriert das Laden aller Quellen
- `_load_groups_data()` - Lädt ESCO Skill Groups
- `_load_esco_data() -> List[Competence]` - Lädt ESCO Skills mit Gruppenzuordnung
- `_load_custom_data() -> List[Competence]` - Lädt Custom Skills aus JSON

**Interne Strukturen**:
- `_competences: List[Competence]` - Alle geladenen Kompetenzen
- `_group_map: Dict[str, str]` - Mapping ESCO URI → Group Code

**Ladevorgang**:
1. ESCO Groups laden (für Hierarchie)
2. ESCO Skills laden und mit Groups anreichern
3. Custom Skills laden
4. Vereinigung in _competences

**Vorteile**: Hybride Wissensbasis für hohe Extraktionsrate bei modernen Begriffen

---

### 7. FastAPI Application (main.py)

#### FastAPI App
**Zweck**: REST API für Stellenanzeigen-Analyse

**Endpoints**:
- `POST /analyse` - Analysiert hochgeladene Stellenanzeigen-Dokumente

**Dependency Injection**:
- `get_workflow_manager() -> IJobMiningWorkflowManager`
  - Erstellt HybridCompetenceRepository (Singleton-ähnlich)
  - Erstellt AdvancedTextExtractor
  - Erstellt FuzzyCompetenceExtractor mit Repository
  - Erstellt JobMiningWorkflowManager mit beiden Extractors

**Request Flow**:
1. Client sendet POST /analyse mit File
2. FastAPI ruft get_workflow_manager() auf
3. manager.run_full_analysis(file.file, file.filename)
4. Rückgabe von AnalysisResultDTO als JSON

**Fehlerbehandlung**: HTTPException mit Status 500 bei Fehlern

---

## Kotlin Backend Klassen

### 1. Entities (domain/Competence.kt)

#### Competence
**Zweck**: JPA Entity für persistierte Kompetenzen

**Attribute**:
- `id: Long?` - Auto-generierte Datenbank-ID
- `originalTerm: String` - Begriff aus Stellenanzeige
- `escoLabel: String` - ESCO-Label
- `escoUri: String` - ESCO URI
- `confidenceScore: Double` - Vertrauensscore (0.0 - 1.0)
- `escoGroupCode: String?` - ESCO Gruppencode (nullable)

**JPA Annotations**:
- `@Entity` - JPA Entität
- `@Id` - Primärschlüssel
- `@GeneratedValue(strategy = IDENTITY)` - Auto-Increment
- `@Column(nullable = true)` - Optionales Feld

**Besonderheit**: Data Class mit allOpen Plugin (Kotlin JPA Kompatibilität)

---

### 2. Entities (JobPosting.kt)

#### JobPosting
**Zweck**: JPA Entity für Stellenanzeigen mit Kompetenz-Beziehung

**Attribute**:
- `id: Long?` - Auto-generierte ID
- `title: String` - Titel der Stellenanzeige
- `jobRole: String` - Position/Rolle
- `rawTextHash: String` - Hash für Idempotenz-Prüfung
- `postingDate: LocalDate` - Veröffentlichungsdatum
- `region: String` - Region
- `industry: String` - Branche
- `competences: List<Competence>` - Liste der Kompetenzen

**JPA Relationships**:
- `@OneToMany(cascade = ALL, fetch = LAZY)` - 1:n Beziehung zu Competence
- `@JoinColumn(name = "job_id")` - Foreign Key in Competence-Tabelle

**Besonderheit**: Enthält doppelte Competence-Definition (sollte konsolidiert werden)

---

### 3. Application (KotlinApiApplication.kt)

#### KotlinApiApplication
**Zweck**: Spring Boot Hauptanwendung

**Annotations**:
- `@SpringBootApplication` - Spring Boot Auto-Configuration

**Funktion**:
- `main(args: Array<String>)` - Entry Point

**TODO**: Controller, Services, Repositories für Job Mining Workflow

---

## Architektur-Patterns

### Verwendete Patterns:
1. **Dependency Injection** - Alle Services werden injiziert
2. **Repository Pattern** - Datenzugriff über Repositories
3. **Interface Segregation** - Klare Interface-Definitionen
4. **DTO Pattern** - Trennung Domain/Transfer Objects
5. **Facade Pattern** - JobMiningWorkflowManager als Facade
6. **Domain-Driven Design** - Interne Domain Entities (Competence)

### Prinzipien:
- SOLID Principles
- Clean Architecture (Layers: API → Service → Repository)
- Testbarkeit durch Interfaces
- Separation of Concerns

---

## Datenfluss

```
1. Client → POST /analyse (PDF/DOCX)
2. FastAPI → get_workflow_manager()
3. JobMiningWorkflowManager.run_full_analysis()
   ├─→ AdvancedTextExtractor.extract_text() → Raw Text
   ├─→ Hash-Generierung
   └─→ FuzzyCompetenceExtractor.extract_competences()
       └─→ HybridCompetenceRepository.get_all_competences()
           ├─→ ESCO Skills laden
           └─→ Custom Skills laden
4. Return AnalysisResultDTO
5. Client ← JSON Response
```

---

## Abhängigkeiten

### Python:
- FastAPI - Web Framework
- Pydantic - DTO Validation
- pypdf - PDF Parsing
- python-docx - DOCX Parsing
- pandas - CSV/DataFrame Verarbeitung
- spacy (optional) - NLP
- fuzzywuzzy (geplant) - Fuzzy Matching

### Kotlin:
- Spring Boot - Framework
- Spring Data JPA - ORM
- Jakarta Persistence - JPA API

---

## Offene TODOs

### Python:
1. Metadaten-Extraktion (Rolle, Region, Datum) - job_mining_workflow_manager.py:20
2. Fuzzy Matching Implementation - fuzzy_competence_extractor.py:8-9
3. Spacy Lemmatisierung - fuzzy_competence_extractor.py:22-26
4. OCR-Fallback - advanced_text_extractor.py:29

### Kotlin:
1. Controller für Job Mining Workflow
2. Services für Business Logic
3. Repositories für Persistence
4. Integration mit Python Backend
5. Competence-Duplikat konsolidieren (JobPosting.kt hat eigene Competence-Klasse)

---

*Erstellt am: 2025-12-26*
*Version: 1.0*
