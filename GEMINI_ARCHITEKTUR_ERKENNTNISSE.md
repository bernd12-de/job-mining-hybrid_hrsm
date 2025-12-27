# 🤖 GEMINI-ARCHITEKTUR-ERKENNTNISSE

**Datum:** 2024-12-27
**Quelle:** docs/ideas/architectural-patterns/Gemini_ESCO_Domain_Parser/ (66 Screenshots)
**Quelle:** docs/ideas/architectural-patterns/Refactor_Datum_Jobtitel__gemini_esco_/ (23 Screenshots)

---

## 🎯 EXECUTIVE SUMMARY

Die Gemini-Chats dokumentieren **2 kritische Architektur-Entscheidungen**, die für dein Job-Mining-Projekt FUNDAMENTAL sind:

### 1. **Domain-Driven Design (DDD)** statt CSV-Chaos
- **Problem:** CSV-Einlesefehler führen erst im späten Code zu Crashes
- **Lösung:** dataclasses als typisierte Blaupause für Entities

### 2. **Intelligente Pipeline (V13.3)** statt Keyword-Matching
- **Problem:** "Isolierte-Wörter-Problem" - Keywords allein reichen nicht
- **Lösung:** Kontext-basierte Extraktion mit Sektions-Filter, Rollen-Brille, NLP

---

## 📂 ORDNER 1: Gemini_ESCO_Domain_Parser (66 Screenshots)

### 🔴 PROBLEM: CSV-Einlesefehler

**Ausgangssituation:**
```python
# VORHER: CSV direkt in Dict/List laden
df = pd.read_csv("jobs.csv")
for row in df.iterrows():
    # FEHLER tritt erst hier auf, wenn Spalte fehlt!
    posting_date = row['Posting_Date']  # KeyError!
```

**Was schiefging:**
- Fehlende Spalten → KeyError erst im Code
- Falsches Datumsformat (str statt date) → Fehler bei Verarbeitung
- Keine Validierung → Pipeline stürzt ab

### ✅ LÖSUNG: Domain-Driven Design

**Architektur-Prinzip:**
> "Daten SOFORT nach dem Einlesen in strukturierte, typisierte Objekte umwandeln. Dadurch wird der Fehler, der durch fehlende oder falsch formatierte CSV-Spalten entsteht, nicht erst im späteren Code, sondern direkt beim Parsen abgefangen."

#### 1. **Entitäten** (core/entities/job_domain.py)

```python
from dataclasses import dataclass, field
from datetime import import date
from typing import List, Optional, Dict

@dataclass(frozen=True)  # ✅ Immutable für Entitäten!
class Skill:
    skill_id: str
    label: str
    skill_domain: str  # tool, method, framework, soft
    esco_id: Optional[str] = None
    confidence: float = 1.0
    source_section: Optional[str] = None

@dataclass(frozen=True)
class JobPosting:
    job_id: str
    title: str
    company: str
    posting_date: Optional[date] = None  # ✅ date statt str!
    date_precision: Optional[str] = "implicit"  # day, month, implicit
    region: Optional[str] = None
    industry_label: Optional[str] = None
    skills: List[Skill] = field(default_factory=list)
```

**Vorteile:**
- ✅ Typisierung fängt Fehler ab (posting_date als `date` statt `str`)
- ✅ Frozen = Immutability (gut für Entitäten)
- ✅ Validierung direkt bei Erstellung

#### 2. **TrendRecord** (für Zeitreihen-Analyse)

```python
@dataclass(frozen=True)
class TrendRecord:
    skill_label: str
    year: int
    region: str
    count: int
    trend_score: float
```

**Zweck:** Stellt das Ergebnis der Zeitreihenanalyse dar (Ebene 7).

#### 3. **Parser-Adapter** (infrastructure/ingestion/csv_parser.py)

```python
import pandas as pd
from datetime import import datetime
from core.entities.job_posting import JobPosting, Skill

class CsvParser:
    """Konvertiert CSV → JobPosting-Objekte."""

    def parse(self, csv_path: str) -> List[JobPosting]:
        jobs: List[JobPosting] = []

        try:
            df = pd.read_csv(csv_path)

            # ✅ WICHTIG: Erwartete Spalten überprüfen!
            required_cols = ['Job_ID', 'Title', 'Company', 'Posting_Date', 'Region', 'Industry']
            if not all(col in df.columns for col in required_cols):
                missing = [col for col in required_cols if col not in df.columns]
                raise ValueError(f"Fehlende Spalten im CSV: {missing}")

            for _, row in df.iterrows():
                try:
                    # Direkte Konvertierung in Domain-Model-Typen mit Fehlerbehandlung
                    posting_date = None
                    if pd.notna(row['Posting_Date']):
                        # ✅ Sicherstellen, dass die Spalte in den datetime-Typ konvertiert wird
                        posting_date = datetime.strptime(str(row['Posting_Date']), '%Y-%m-%d').date()

                    # Erstellung der typisierten JobPosting-Instanz
                    job = JobPosting(
                        job_id=str(row['Job_ID']),
                        title=str(row['Title']),
                        company=str(row['Company']),
                        posting_date=posting_date,
                        region=str(row['Region']),
                        industry_label=str(row['Industry']),
                        # Skills müssen separat aus CSV-Spalten geparst und hinzugefügt werden
                        skills=[]
                    )
                    jobs.append(job)

                except Exception as e:
                    # Fehler auf Zeilenebene abfangen (z.B. falsches Datumsformat)
                    print(f"Warnung: Zeile mit ID {row.get('Job_ID', 'N/A')} konnte nicht geparst werden: {e}")
                    # Sie können hier entscheiden, ob Sie die Zeile überspringen oder einen Standardwert setzen

        except Exception as e:
            # Fehler auf Dateiebene abfangen (z.B. fehlende Datei, falscher Separator, fehlende Spalten)
            print(f"Kritischer Fehler beim Parsen der Datei {csv_path}: {e}")
            return []  # Leere Liste zurückgeben, um die Pipeline nicht zu stoppen

        return jobs
```

**Vorteile gegen "CSV-Einlesefehler":**
- ✅ try...except-Blöcke fangen sowohl kritische Fehler (Datei existiert nicht, falscher Header) als auch Zeilenfehler (falsches Datumsformat in einer Zeile) ab
- ✅ Die Rückgabe einer Liste von JobPosting-Objekten stellt sicher, dass alle nachfolgenden Services (Mapper, Analyzer) nur mit **sauberen, validierten** Daten arbeiten

#### 4. **JobAdParser** - Hauptklasse (Strukturierte Extraktion)

**Zweck:** Implementiert den Ingestion-Layer: Extrahiert Roh-Text und konvertiert ihn in die strukturierte JobPosting Entity.

```python
class JobAdParser:
    """
    Implementiert den Ingestion-Layer: Extrahiert Roh-Text und konvertiert
    ihn in die strukturierte JobPosting Entity.
    """

    def parse(self, file_path: str) -> JobPosting:
        """Der zentrale Konvertierungsschritt: Rohdaten -> JobPosting Entity."""

        raw_text = _extract_raw_text(file_path)

        if not raw_text:
            raise ValueError(f"Konnte keinen Text aus {os.path.basename(file_path)} extrahieren.")

        # Strukturierte Felder extrahieren (mit Regelwerk)
        job_title = self._extract_title(raw_text)
        job_company = self._extract_company(raw_text)
        posting_date = self._extract_date(raw_text, file_path)  # Datum mit Fallback auf Metadaten

        # JobPosting Entity erstellen (Erfüllung des Architektur-Vertrags)
        job_id = os.path.basename(file_path)

        return JobPosting(
            job_id=job_id,
            title=job_title,
            company=job_company,
            posting_date=posting_date,
            region=self._extract_region(raw_text),
            industry_label=self._extract_industry(raw_text),
            skills=[]  # Skills werden später durch CompetenceExtractor hinzugefügt
        )
```

**Wichtig:**
- **Hilfsfunktionen:** Reine, robuste **Text-Extraktion** (Ihre vorhandene Logik)
- **JobAdParser Klasse:** Verantwortlich für die **Feld-Extraktion mit Regeln** und die **Erstellung der JobPosting Entity**

**Code-Vorschlag für die Korrektur (parser.py in infrastructure/ingestion/):**

Sie können die vorhandene Funktion `extract_text_from_file` in eine private Methode (`_extract_raw_text`) umwandeln und eine Hauptklasse hinzufügen:

```python
# job-mining/infrastructure/ingestion/parser.py
from core.entities.job_posting import JobPosting
from datetime import import date
import re, os

# --- HILFSFUNKTIONEN (Reine, robuste Text-Extraktion) ---

def _extract_raw_text(file_path: str) -> str:
    """Ihre vorhandene Logik für PDF/DOCX/TXT/Bilder."""
    # 1. Bilder (Screenshots) nutzen immer OCR
    if file_extension in ['.jpg', '.jpeg', '.png']:
        text = _perform_ocr_fallback(file_path)

    elif file_extension in ['.docx']:
        # 3. Handling für DOCX (mit python-docx)
        document = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])

    elif file_extension in ['.doc', '.txt']:
        # 4. Einfache Datei-Einlesung für ältere oder Plain-Text-Formate
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

    else:
        # Unbekanntes Format
        return None

    return text.strip() if text.strip() else None

# --- 3. HAUPTKLASSE: JobAdParser (Konvertiert Rohdaten zur Entity) ---

class JobAdParser:
    """
    Implementiert den Ingestion-Layer: Nutzt Roh-Text und erstellt die JobPosting Entity.
    """

    def parse(self, file_path: str) -> JobPosting:
        """Der zentrale Konvertierungsschritt: Rohdaten -> JobPosting Entity."""

        raw_text = _extract_raw_text(file_path)

        if not raw_text:
            raise ValueError(f"Konnte keinen Text aus {os.path.basename(file_path)} extrahieren.")

        # Strukturierte Felder extrahieren (mit Regelwerk)
        job_title = self._extract_title(raw_text)
        job_company = self._extract_company(raw_text)
        posting_date = self._extract_date(raw_text, file_path)

        # JobPosting Entity erstellen
        job_id = os.path.basename(file_path)

        return JobPosting(
            job_id=job_id,
            title=job_title,
            company=job_company,
            posting_date=posting_date,
            region=self._extract_region(raw_text),
            industry_label=self._extract_industry(raw_text),
            skills=[]
        )

    def _extract_title(self, raw_text: str) -> str:
        # Ihre Logik (erste Zeile, bereinigt)
        pass

    def _extract_date(self, raw_text: str, file_path: str) -> date:
        # Ihre Logik (4-stufiger Fallback - siehe Ordner 2!)
        pass
```

#### 5. **Pipeline Entrypoint** (main.py oder pipeline.py)

```python
from infrastructure.ingestion.csv_parser import CsvParser

def run_analysis(csv_file_path: str):
    parser = CsvParser()

    # Der Parser gibt JobPosting-Objekte zurück, keine Rohdaten mehr
    clean_jobs = parser.parse(csv_file_path)

    if not clean_jobs:
        print("Analyse abgebrochen: Keine Jobdaten verfügbar.")
        return

    print(f"Erfolgreich {len(clean_jobs)} Jobs geparst. Starte ESCO-Mapping...")

    # Beispiel-Aufruf für den Trend-Analyzer (aus dem Blueprint)
    # ...
```

**Dieser Ansatz mit dem Domain-Model und dem Parser-Adapter ist die entscheidend bessere und langfristig notwendige Lösung für ein wissenschaftliches, reproduzierbares System.**

---

### 🔑 KERNKONZEPTE

| Konzept | Beschreibung | Zweck |
|---------|--------------|-------|
| **@dataclass(frozen=True)** | Immutable Entities | Verhindert versehentliche Änderungen |
| **Parser-Adapter** | Infrastructure Layer | Trennt Datei-Lese-Logik von Domänen-Logik |
| **Trennung** | Roh-Text-Extraktion vs. Feld-Extraktion | Clean Architecture |
| **Validierung** | Try-Except auf Zeilen-Ebene | Verhindert Pipeline-Crash |

---

### 📊 ENTITÄTEN-ÜBERSICHT

| Entität | Zweck | Kernfelder (Auszug) |
|---------|-------|---------------------|
| **Skill** | Stellt eine extrahierte Kompetenz dar | skill_id, label, skill_domain (tool/soft/method), esco_id, confidence |
| **JobPosting** | Stellt das Ergebnis eines geparsten Stellenangebots dar | job_id, title, posting_date, region, industry_label, skills |
| **TrendRecord** | Stellt das Ergebnis der Zeitreihenanalyse dar | skill_label, year, region, count, trend_score |

---

### ✅ VORTEILE FÜR DEIN PROJEKT

1. **Fehler-Prävention:** CSV-Fehler werden direkt beim Parsing abgefangen, nicht erst im späteren Code
2. **Wissenschaftliche Validität:** Saubere, typisierte Daten für reproduzierbare Analysen
3. **Clean Architecture:** Trennung von Infrastructure (Parser) und Domain (Entities)
4. **Erweiterbarkeit:** Neue Entitäten (z.B. `Textbook`, `ModuleHandbook`) einfach hinzufügen

---

## 📂 ORDNER 2: Refactor_Datum_Jobtitel__gemini_esco_ (23 Screenshots)

### 🔴 PROBLEM: "Isolierte-Wörter-Problem"

**Ausgangssituation:**
```python
# VORHER: Keyword-Matching allein
text = "Wir nutzen modernste Technologie"  # Ganzer Text
if "Technologie" in text:
    skills.append("Technologie")  # ❌ FALSCH - Das ist kein Skill des Bewerbers!
```

**Was schiefging:**
- Keywords aus Abschnitt "Wir bieten" werden als Skills gezählt (FALSCH!)
- "Team" aus "Wir sind ein tolles Team" fliegt raus (Rauschen)
- Keine Unterscheidung: "Kommunikation" für Product Owner (Level 4 in agile_methods.json) vs. Lagerist (Level 2 in ESCO)

### ✅ LÖSUNG: "Intelligente Pipeline" (V13.3 Logik)

**Architektur-Prinzip:**
> "Wenn wir nicht mehr stur nach Keywords suchen, sondern den **Kontext der ganzen Beschreibung** nutzen, ändert sich der Arbeitsablauf des Programms (der Pipeline) grundlegend."

#### 🔧 3 SCHRITTE DER INTELLIGENTEN PIPELINE

### **1. Sektions-Filter** (Wo steht es?)

**Problem:** Das Programm liest nicht mehr den ganzen Brei der PDF.
Es schneidet zuerst den Text in Scheiben.

**Was es macht:**
- Ignoriert den Abschnitt "Über uns" und "Wir bieten" (Benefits)

**Warum:**
- Wenn im Bereich "Wir bieten" steht: "Wir nutzen modernste Technologie", ist das **kein** Skill des Bewerbers

**Aktion:**
- Der `CompetenceExtractor` bekommt nur noch den Text aus **"Deine Aufgaben"** und **"Dein Profil"**

**Code:**
```python
# metadata_extractor.py - TASK_PATTERN und REQ_PATTERN
TASK_PATTERN = re.compile(
    r'(?:DEINE AUFGABEN|TÄTIGKEITEN|WAS DU BEI UNS MACHST|YOUR TASKS|RESPONSIBILITIES|TASKS|WHAT YOU WILL DO)[\s\r\n:.-]+(.*?)(?=(?:DEIN PROFIL|PROFIL|REQUIREMENTS|WIR BIETEN|WIR SUCHEN|BENEFITS|ABOUT US|$))',
    re.DOTALL | re.IGNORECASE
)

REQ_PATTERN = re.compile(
    r'(?:PROFIL|DEIN PROFIL|YOUR PROFILE|ANFORDERUNGEN|REQUIREMENTS|QUALIFICATIONS|VORAUSSETZUNGEN|SKILLSET)[\s\r\n:.-]+(.*?)(?=(?:DEINE AUFGABEN|TASKS|WIR BIETEN|WIR SUCHEN|BENEFITS|KONTAKT|$))',
    re.DOTALL | re.IGNORECASE
)

tasks_match = TASK_PATTERN.search(text)
reqs_match = REQ_PATTERN.search(text)

clean_segment = ""
if tasks_match: clean_segment += tasks_match.group(1).strip()
if reqs_match: clean_segment += " " + reqs_match.group(1).strip()

is_segmented = bool(tasks_match or reqs_match) and len(clean_segment) > 50
```

**Fallback:** Wenn die Segmentierung fehlschlägt (Text zu kurz), nutze den gesamten Rohtext

---

### **2. Rollen-Brille** (Wer wird gesucht?)

**Problem:** Bevor nach Skills gesucht wird, bestimmt das System die **Rolle**.

**Was es macht:**
- Der `RoleService` analysiert den Titel (z.B. "Junior UX Designer")

**Warum:**
- Das Wort "Management" bedeutet bei einem "Product Owner" etwas anderes (Backlog Management) als bei einem "Teamleiter" (People Management)

**Aktion:**
- Das System lädt **dynamisch das passende Fachbuch-Wissen**
  - Rolle = UX: Lade `ux_methods.json`
  - Rolle = Java Dev: Lade `software_architecture.json`

**Code:**
```python
# role_service.py
def classify_role(self, text: str, job_title: str) -> str:
    """Klassifiziert die Rolle basierend auf Jobtitel."""
    normalized_text = text.lower()

    for category, pattern in self.category_patterns.items():
        if re.search(pattern, normalized_text):
            return category

    return "Sonstige Fachgebiete"
```

**Rollen-Kontext:**
```python
# Im CompetenceExtractor:
def extract_competences(self, text: str, role: str) -> List[CompetenceDTO]:
    # ...
    is_academic = self.repository.is_in_domain(comp.original_term, role_context)

    # Level Logik
    if is_academic and is_esco:
        comp.level = 4  # Gold-Standard (Academia validiert ESCO)
    elif is_esco:
        comp.level = 2  # Standard (ESCO)
    else:
        comp.level = 1  # Markttrend (Discovery)

    comp.role_context = role
    final_competences.append(comp)
```

---

### **3. Satz-Bau-Check** (Wie wird es benutzt?)

**Problem:** Das ist der **wichtigste Punkt gegen das "Keyword-Problem"**.
Wir nutzen **SpaCy**.

**Was es macht:**
- SpaCy findet Phrasen basierend auf ESCO (PhraseMatcher)
- Fuzzy findet Schreibfehler / Varianten
- Discovery findet unbekannte Großgeschriebene Begriffe (Ebene 1)
  - Nur wenn sie NICHT schon durch SpaCy/Fuzzy gefunden wurden

**Code:**
```python
# competence_extractor.py - Intelligente Pipeline
def extract_competences(self, text: str, role: str) -> List[CompetenceDTO]:
    """
    Führt die Extraktion auf dem BEREINIGTEN Text durch.
    Nutzt die Rolle, um Fachbuch-Wissen zu kontextualisieren.
    """

    # 1. NLP Parsing (Satzstruktur verstehen: Subjekt -> Prädikat -> Objekt)
    # Das verhindert, dass wir isolierte Wörter ohne Sinn finden.
    doc = self.nlp(text)

    # 2. Spezialisten-Module abfragen
    # SpaCy: Findet Phrasen basierend auf ESCO
    results = self.spacy_ext.extract(doc, role)

    # Fuzzy: Findet Schreibfehler / Varianten
    results += self.fuzzy_ext.extract_competences(text)

    # Discovery: Findet unbekannte Großgeschriebene Begriffe (Ebene 1)
    # Nur wenn sie NICHT schon durch SpaCy/Fuzzy gefunden wurden
    results += self.discovery_ext.extract_discoveries(doc)

    # 3. Konsolidierung & 7-Ebenen-Logik
    return self._finalize_and_level(results, role)
```

**NLP-Parsing:**
```python
# SpaCy NLP Parsing (Satzstruktur: Subjekt → Prädikat → Objekt)
doc = self.nlp(text)
```

**Warum wichtig:**
- Verhindert, dass isolierte Wörter ohne Sinn gefunden werden
- Beispiel: "Wir sind ein tolles Team" → "Team" wird erkannt, aber im Kontext als Rauschen gefiltert

---

### **Konsolidierung & 7-Ebenen-Logik**

```python
def _finalize_and_level(self, dtos: List[CompetenceDTO], role: str) -> List[CompetenceDTO]:
    seen = set()
    final_list = []

    for dto in dtos:
        # Deduplizierung basierend auf URI (oder Begriff, wenn Discovery)
        unique_key = dto.esco_uri if dto.esco_uri else dto.original_term.lower()

        if unique_key not in seen:
            dto.role_context = role

            # --- DIE HAKEN-LOGIK (Ebene 1 bis 5) ---

            # Check: Fachbuch? (Ebene 4) - Aber nur im passenden Kontext!
            # Ein "Backlog" ist nur im "Agile"-Kontext Ebene 4, sonst vielleicht nur Ebene 1.
            is_academic = self.repository.is_in_domain(dto.original_term, role_context)

            # Level Logik
            if is_academic and is_esco:
                dto.level = 4  # Gold-Standard
            elif is_esco:
                dto.level = 2  # Standard
            else:
                dto.level = 1  # Markttrend (Discovery)

            final_list.append(dto)
            seen.add(unique_key)

    return final_list
```

---

### **Datum-Extraktion** (4-stufiger Fallback)

**Problem:** Die Funktion `extract_text_from_file` enthält **keine Logik** zur Suche von Datumsmustern, Titeln, Firmennamen oder Orten. Sie gibt nur den **gesamten Roh-Text** zurück.

**Lösung:** Neue Funktion und Parser-Klasse hinzufügen, die den Roh-Text nimmt und mittels **Regular Expressions (Prio 2-Fix)** das Datum (08.07.24) und andere Felder strukturiert extrahiert.

**Code:**
```python
def _extract_date(self, raw_text: str, file_path: str) -> date:
    """
    4-stufiger Fallback für Datum-Extraktion.
    Prio 1: Jahr aus Schätzung (besser als das heutige Druckdatum!)
    """

    # STUFE 1: Jahr-Schätzung (besser als Upload-Datum)
    # Wenn kein Datum gefunden, nimm das geschätzte Jahr
    # return f"{year}-01-01"

    # STUFE 2: Kontext-Suche ("Eingestellt am...")
    # Ignoriert nackte Daten im Header, sucht nach Labels.
    keyword_patterns = [
        r'(?:Eingestellt am|Veröffentlicht|Datum|Date|Posted):\s*(\d{1,2}\.\d{1,2}\.\d{4})',
        r'(?:Eingestellt am|Veröffentlicht|Datum|Date|Posted):\s*(\d{4}-\d{2}-\d{2})'
    ]

    for pattern in keyword_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return self._normalize_date(match.group(1))

    # STUFE 3: Header-Ausschluss (Heuristik)
    # Suche nach Daten im Text, aber überspringe die ersten 200 Zeichen (Header),
    # falls dort das Druckdatum steht.
    body_text = text[200:] if len(text) > 200 else text

    date_patterns = [r'(\d{1,2}\.\d{1,2}\.\d{4})', r'(\d{4}-\d{2}-\d{2})']
    for pattern in date_patterns:
        match = re.search(pattern, body_text)
        if match:
            return self._normalize_date(match.group(1))

    # STUFE 4: Notfall (Wenn alles fehlschlägt, nimm Metadaten oder Default)
    # Warnung: Das könnte das Upload-Datum sein!
    return "2024-01-01"

def _normalize_date(self, date_str: str) -> date:
    """Hilfsfunktion um z.B. 1.1.11 in 2011-01-01 zu wandeln"""
    # ... (Implementierung wie gehabt)
```

---

### 🔑 KERNKONZEPTE DER INTELLIGENTEN PIPELINE

| Schritt | Beschreibung | Technologie | Zweck |
|---------|--------------|-------------|-------|
| **1. Sektions-Filter** | Ignoriert "Wir bieten" und "Über uns" | Regex (TASK_PATTERN, REQ_PATTERN) | Verhindert, dass Benefits als Skills gezählt werden |
| **2. Rollen-Brille** | Lädt dynamisches Fachbuch-Wissen je nach Rolle | RoleService + domain JSONs | "Kommunikation" ist Level 4 für Product Owner, Level 2 für Lagerist |
| **3. Satz-Bau-Check** | NLP-Parsing (Subjekt → Prädikat → Objekt) | SpaCy PhraseMatcher | Verhindert "isolierte Wörter ohne Sinn" |
| **4. Datum-Fallback** | 4-stufiger Fallback (Jahr-Schätzung → Kontext → Header → Default) | Regex + Metadaten | Robuste Datum-Extraktion |

---

### ✅ VORTEILE FÜR DEIN PROJEKT

1. **Weniger Müll:** "Team" aus "Wir sind ein tolles Team" fliegt raus
2. **Mehr Tiefe:** "Kommunikation" wird je nach Rolle (Product Owner vs. Lagerist) korrekt eingestuft
3. **Zeit-Reise:** Du kannst zeigen, wie sich die **Beschreibung** (der Kontext) von Skills über die Jahre verändert hat (von einfacher Nennung zu komplexer Einbettung in Methoden)
4. **Wissenschaftliche Validität:** Robuste Datum-Extraktion für Zeitreihen-Analyse

---

## 🎯 ZUSAMMENFASSUNG: WAS BEDEUTET DAS FÜR DICH?

### **Für die Postersession (14. Januar 2025):**

#### ✅ SOFORT UMSETZEN (Prio 1):

1. **Domain-Entities aus POC übernehmen:**
   ```python
   # POC hat bereits:
   docs/ideas/proof-of-concept/app/domain/models.py
   ```
   - ✅ `@dataclass` für CompetenceDTO, AnalysisResultDTO
   - ✅ `frozen=True` für Immutability
   - ✅ Validierung mit Pydantic

2. **Intelligente Pipeline aus POC übernehmen:**
   ```python
   # POC hat bereits:
   docs/ideas/proof-of-concept/app/application/job_mining_workflow_manager.py
   docs/ideas/proof-of-concept/app/infrastructure/extractor/metadata_extractor.py
   docs/ideas/proof-of-concept/app/infrastructure/extractor/spacy_competence_extractor.py
   ```
   - ✅ Sektions-Filter (TASK_PATTERN, REQ_PATTERN)
   - ✅ Rollen-Brille (role_service.py)
   - ✅ NLP-Parsing (SpaCy PhraseMatcher)
   - ✅ 4-stufiger Datum-Fallback

#### 🟡 OPTIONAL (Prio 2):

3. **Parser-Adapter Pattern:**
   - Trenne Raw-Text-Extraktion von Feld-Extraktion
   - Erstelle `JobAdParser` Klasse (siehe Code oben)

#### 🔵 SPÄTER (Prio 3):

4. **TrendRecord Entity:**
   - Für Zeitreihen-Analyse (Ebene 7)
   - Erstelle `@dataclass` für Trend-Daten

---

### **Architektur-Entscheidungen:**

| Thema | Gemini-Empfehlung | POC-Status | Main-Status | Aktion |
|-------|-------------------|------------|-------------|--------|
| **Domain Entities** | ✅ @dataclass(frozen=True) | ✅ Vorhanden | ❌ Fehlt | POC → Main |
| **Parser-Adapter** | ✅ Trennung Raw/Feld | 🟡 Teilweise | ❌ Fehlt | Neu erstellen |
| **Sektions-Filter** | ✅ Regex für Tasks/Reqs | ✅ Vorhanden | ❌ Fehlt | POC → Main |
| **Rollen-Brille** | ✅ role_service.py | ✅ Vorhanden | ❌ Fehlt | POC → Main |
| **NLP-Parsing** | ✅ SpaCy PhraseMatcher | ✅ Vorhanden | ❌ Basic | POC → Main |
| **Datum-Fallback** | ✅ 4-stufig | ✅ Vorhanden | ❌ Hardcoded | POC → Main |

---

## 📋 CHECKLISTE FÜR MIGRATION

### Phase 1: Domain-Entities (1-2 Tage)

- [ ] Kopiere `app/domain/models.py` von POC → Main
- [ ] Teste, dass Pydantic-Validierung funktioniert
- [ ] Erstelle `TrendRecord` Entity für Zeitreihen

### Phase 2: Intelligente Pipeline (2-3 Tage)

- [ ] Kopiere `metadata_extractor.py` von POC → Main
- [ ] Kopiere `spacy_competence_extractor.py` von POC → Main
- [ ] Kopiere `role_service.py` von POC → Main
- [ ] Teste Sektions-Filter mit echten PDFs
- [ ] Teste Rollen-Brille mit verschiedenen Jobtiteln

### Phase 3: Parser-Adapter (Optional, 1 Tag)

- [ ] Erstelle `JobAdParser` Klasse (siehe Code oben)
- [ ] Trenne Raw-Text-Extraktion von Feld-Extraktion
- [ ] Teste mit CSV- und PDF-Eingabe

---

## 🚀 NÄCHSTE SCHRITTE

1. **POC vs. Main Vergleich aktualisieren:**
   - Füge Gemini-Erkenntnisse zu `POC_VS_MAIN_ANALYSE.md` hinzu

2. **Migration starten:**
   - Phase 1: Domain-Entities (SOFORT)
   - Phase 2: Intelligente Pipeline (KRITISCH für Postersession)

3. **Tests schreiben:**
   - Teste Sektions-Filter mit echten Stellenanzeigen
   - Teste Rollen-Brille mit verschiedenen Jobtiteln
   - Teste Datum-Fallback mit verschiedenen Formaten

---

## 📚 QUELLEN

**Gemini-Chats:**
- `docs/ideas/architectural-patterns/Gemini_ESCO_Domain_Parser/` (66 Screenshots)
- `docs/ideas/architectural-patterns/Refactor_Datum_Jobtitel__gemini_esco_/` (23 Screenshots)

**POC-Code:**
- `docs/ideas/proof-of-concept/app/domain/models.py`
- `docs/ideas/proof-of-concept/app/infrastructure/extractor/metadata_extractor.py`
- `docs/ideas/proof-of-concept/app/infrastructure/extractor/spacy_competence_extractor.py`
- `docs/ideas/proof-of-concept/app/application/services/role_service.py`

**Referenzen:**
- [Python for AI: Week 9 - @dataclass In Python for Deep Learning Projects](https://example.com)
- Clean Architecture (Robert C. Martin)
- Domain-Driven Design (Eric Evans)

---

**Erstellt von:** Claude
**Für:** Bernd
**Projekt:** job-mining-kotlin-python
**Deadline:** 14. Januar 2025 (Postersession)
