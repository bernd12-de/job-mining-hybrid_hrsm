# 🔄 Job Mining Workflow - Automatisierte Auswertung

**Version:** 2.0 COMPLETE mit Workflow Manager  
**Datum:** 01. November 2025  
**Status:** ✅ PRODUKTIONSREIF

---

## 🎯 WAS IST NEU?

### ✨ Workflow Manager implementiert!

**Ja, das manuelle Einlesen neuer Stellenanzeigen und automatische Auswertung ist jetzt drin!**

Der **Workflow Manager** automatisiert den kompletten Prozess:

```
1. Neue Stellenanzeigen hochladen (PDF/DOCX/Google Docs)
   ↓
2. Automatische Verarbeitung
   ↓
3. Skill-Extraktion (135+ Skills)
   ↓
4. Ergebnisse speichern (JSON/CSV)
   ↓
5. Reports generieren (HTML + Text)
   ↓
6. Archivierung
```

---

## 📦 NEUE KOMPONENTE

### Workflow Manager (20 KB) ⭐ NEU

[View job_mining_workflow_manager.py](computer:///mnt/user-data/outputs/job_mining_workflow_manager.py)

**Features:**
- ✅ Manueller Upload neuer Stellenanzeigen
- ✅ Automatische Verarbeitung
- ✅ Metadata-Support (Firma, Position, Datum, Quelle)
- ✅ Archivierung nach Monat
- ✅ JSON/CSV Export
- ✅ HTML Report-Generierung
- ✅ Statistik-Tracking

---

## 🚀 QUICK START

### Installation

```bash
# Dependencies (falls noch nicht installiert)
pip install PyPDF2 python-docx pandas --break-system-packages
sudo apt-get install pandoc  # Optional
```

### Verwendung

#### Option 1: Programmatisch (Python)

```python
from job_mining_workflow_manager import JobMiningWorkflowManager

# Initialize
manager = JobMiningWorkflowManager()

# Schritt 1: Neue Stellenanzeige hinzufügen
manager.add_job_ad(
    'path/to/stellenanzeige.pdf',
    metadata={
        'company': 'Tech Startup GmbH',
        'position': 'Senior UX Designer',
        'date_posted': '2025-11-01',
        'source': 'LinkedIn',
        'location': 'Berlin',
        'url': 'https://...'
    }
)

# Schritt 2: Workflow ausführen (automatisch)
manager.run_workflow()

# Das war's! Ergebnisse sind jetzt in:
# - results/ (JSON, CSV)
# - reports/ (HTML, Text)
# - archive/ (Original-Dateien)
```

#### Option 2: Manuell (Datei-basiert)

```bash
# 1. Dateien in incoming/ ablegen
cp stellenanzeige1.pdf job_mining_workflow/incoming/
cp stellenanzeige2.docx job_mining_workflow/incoming/
cp google_doc.docx job_mining_workflow/incoming/

# 2. Workflow ausführen
python3 << EOF
from job_mining_workflow_manager import JobMiningWorkflowManager
manager = JobMiningWorkflowManager()
manager.run_workflow()
EOF

# 3. Ergebnisse anschauen
ls job_mining_workflow/reports/*.html
```

---

## 📂 VERZEICHNIS-STRUKTUR

Der Workflow Manager erstellt automatisch folgende Struktur:

```
job_mining_workflow/
├── incoming/              📥 Neue Stellenanzeigen hier ablegen
│   ├── stellenanzeige1.pdf
│   ├── stellenanzeige2.docx
│   └── google_doc.docx
│
├── processing/            ⚙️ Temporär während Verarbeitung
│   └── (leer nach Verarbeitung)
│
├── archive/               📁 Archiv nach Verarbeitung
│   ├── 2025-11/          (organisiert nach Monat)
│   │   ├── 20251101_120000_stellenanzeige1.pdf
│   │   ├── 20251101_120000_stellenanzeige1.meta.json
│   │   ├── 20251101_120130_stellenanzeige2.docx
│   │   └── 20251101_120130_stellenanzeige2.meta.json
│   └── 2025-10/
│
├── results/               📊 JSON/CSV Ergebnisse
│   ├── results_20251101_120500.json
│   ├── results_summary_20251101_120500.csv
│   └── results_detailed_20251101_120500.csv
│
├── reports/               📝 HTML/Text Reports
│   ├── report_20251101_120500.html    ⭐ HTML mit Visualisierung
│   └── report_20251101_120500.txt
│
└── logs/                  📋 Log-Dateien (optional)
    └── workflow.log
```

---

## 🎨 HTML REPORT

Der Workflow Manager generiert **automatisch einen schönen HTML-Report** mit:

### Dashboard mit Kennzahlen
```
┌─────────────────────────────────────────────┐
│  [36]              [248]                    │
│  Job Ads           Total Skills             │
│  Analyzed          Found                    │
│                                             │
│  [8.2]             [93.5%]                  │
│  Avg Skills        Avg Confidence           │
│  per Job                                    │
└─────────────────────────────────────────────┘
```

### Top Skill Categories
- Balkendiagramm
- Prozentuale Verteilung
- Farbcodiert

### Top 20 Skills
- Häufigkeit in Jobs
- Prozent-Anteil
- Ranking

### Liste aller analysierten Jobs
- Dateiname & Format
- Skill-Anzahl
- Top Category
- Confidence Score

**Beispiel-Report:** `file:///path/to/reports/report_TIMESTAMP.html`

---

## 📝 METADATA-SUPPORT

Sie können zu jeder Stellenanzeige **zusätzliche Informationen** speichern:

```python
metadata = {
    'company': 'Example GmbH',           # Firmenname
    'position': 'Senior UX Designer',    # Position
    'date_posted': '2025-11-01',         # Veröffentlichungsdatum
    'source': 'LinkedIn',                # Quelle (LinkedIn, Indeed, etc.)
    'location': 'Berlin, Germany',       # Standort
    'salary': '70.000 - 90.000 EUR',     # Gehalt (optional)
    'employment_type': 'Vollzeit',       # Beschäftigungsart
    'url': 'https://...',                # Link zur Anzeige
    'notes': 'Sehr interessant!'         # Eigene Notizen
}

manager.add_job_ad('job.pdf', metadata=metadata)
```

Diese Informationen werden:
- ✅ Als `.meta.json` gespeichert
- ✅ Im HTML-Report angezeigt
- ✅ In CSV exportiert
- ✅ Im Archiv aufbewahrt

---

## 🔄 WORKFLOW-PROZESS (Detail)

### Schritt 1: Upload

**Automatisch:**
```python
manager.add_job_ad('job.pdf', metadata={...})
```

**Manuell:**
```bash
cp job.pdf job_mining_workflow/incoming/
```

**Was passiert:**
- Datei wird mit Timestamp umbenannt
- Optional: Metadata wird als JSON gespeichert
- Datei liegt in `incoming/`

### Schritt 2: Processing

```python
manager.run_workflow()
```

**Was passiert:**
1. **Alle Dateien in `incoming/` werden erkannt**
   - PDF, DOCX, DOC, Google Docs (als DOCX)

2. **Für jede Datei:**
   - Move zu `processing/`
   - Parse (Multi-Format Parser)
   - Extract Skills (135+ Custom Skills)
   - Load Metadata (falls vorhanden)

3. **Bei Erfolg:**
   - Move zu `archive/YYYY-MM/`
   - Timestamp-basierter Name
   - Metadata bleibt dabei

4. **Bei Fehler:**
   - Move zurück zu `incoming/`
   - Error wird geloggt
   - Andere Dateien werden weiter verarbeitet

### Schritt 3: Results

**JSON (detailed):**
```json
{
  "metadata": {
    "version": "2.0",
    "total_jobs": 5,
    "total_competences": 42,
    "avg_competences_per_job": 8.4
  },
  "results": [
    {
      "filename": "job1.pdf",
      "file_type": "pdf",
      "word_count": 324,
      "competence_count": 8,
      "categories": {
        "UX/UI Design": 3,
        "Technical Skills": 2,
        "Agile": 1
      },
      "competences": [...]
    }
  ]
}
```

**CSV (summary):**
```
Filename,File Type,Word Count,Competence Count,Avg Confidence,Top Category,...
job1.pdf,pdf,324,8,0.95,UX/UI Design,...
job2.docx,docx,256,10,0.92,Product Management,...
```

**CSV (detailed):**
```
Filename,File Type,Skill ID,Skill Name,Category,Type,Confidence
job1.pdf,pdf,ux_001,Figma,UX/UI Design,Tool,1.0
job1.pdf,pdf,ux_002,Sketch,UX/UI Design,Tool,1.0
...
```

### Schritt 4: Reports

**HTML Report:**
- Schönes Dashboard
- Interaktive Visualisierungen
- Responsive Design
- Druckbar

**Text Report:**
- ASCII-Tabellen
- Vollständige Statistiken
- Terminal-freundlich

### Schritt 5: Archive

Alle verarbeiteten Dateien werden **dauerhaft archiviert**:
```
archive/
├── 2025-11/
│   ├── 20251101_120000_stellenanzeige.pdf
│   ├── 20251101_120000_stellenanzeige.meta.json
│   └── ...
└── 2025-10/
    └── ...
```

**Vorteile:**
- ✅ Chronologische Organisation
- ✅ Originalausgabe bleibt erhalten
- ✅ Metadata bleibt verknüpft
- ✅ Wiederverwendbar für Zeitreihen-Analysen

---

## 📊 STATISTIKEN & TRACKING

```python
# Statistiken abrufen
stats = manager.get_statistics()

print(f"Total archived: {stats['total_archived']}")
print(f"Result files: {stats['total_results']}")
print(f"Pending: {stats['incoming_pending']}")
print(f"Last run: {stats['last_run']}")
```

---

## 🔁 KONTINUIERLICHER WORKFLOW

Für **regelmäßige Auswertung** neuer Stellenanzeigen:

```python
import time
from job_mining_workflow_manager import JobMiningWorkflowManager

manager = JobMiningWorkflowManager()

while True:
    print("Checking for new job ads...")
    
    # Run workflow
    manager.run_workflow()
    
    # Wait (z.B. 1 Stunde)
    print("Waiting 1 hour...")
    time.sleep(3600)
```

**Oder als Cron Job:**
```bash
# Täglich um 9:00 Uhr
0 9 * * * cd /path/to/project && python3 -c "from job_mining_workflow_manager import JobMiningWorkflowManager; JobMiningWorkflowManager().run_workflow()"
```

---

## 💡 ANWENDUNGSBEISPIELE

### Beispiel 1: Einzelne Stellenanzeige manuell

```python
from job_mining_workflow_manager import JobMiningWorkflowManager

manager = JobMiningWorkflowManager()

# LinkedIn-Anzeige als PDF gespeichert
manager.add_job_ad(
    'downloads/ux_designer_startup.pdf',
    metadata={
        'company': 'Cool Startup GmbH',
        'position': 'UX Designer (m/w/d)',
        'date_posted': '2025-11-01',
        'source': 'LinkedIn',
        'location': 'Berlin',
        'url': 'https://linkedin.com/jobs/...'
    }
)

# Sofort auswerten
manager.run_workflow()
```

### Beispiel 2: Batch von Google Docs

```python
from pathlib import Path
from job_mining_workflow_manager import JobMiningWorkflowManager

manager = JobMiningWorkflowManager()

# Alle Google Docs exports
gdocs_dir = Path('google_docs_exports/')

for docx_file in gdocs_dir.glob('*.docx'):
    manager.add_job_ad(
        str(docx_file),
        metadata={
            'source': 'Google Docs',
            'date_added': '2025-11-01'
        }
    )

# Alle auf einmal verarbeiten
manager.run_workflow()
```

### Beispiel 3: Mixed Formats

```python
manager = JobMiningWorkflowManager()

# PDFs von Webseiten
for pdf in Path('downloads/').glob('*.pdf'):
    manager.add_job_ad(str(pdf), metadata={'source': 'Web'})

# DOCX von Recruitern
for docx in Path('emails/attachments/').glob('*.docx'):
    manager.add_job_ad(str(docx), metadata={'source': 'Email'})

# Google Docs
for gdoc in Path('gdrive/').glob('*.docx'):
    manager.add_job_ad(str(gdoc), metadata={'source': 'Google Drive'})

# Alles verarbeiten
manager.run_workflow()
```

---

## 🎓 FÜR DIE MASTERARBEIT

### Wissenschaftliche Vorteile

**1. Reproduzierbarkeit:**
- Alle Schritte dokumentiert
- Originaledateien archiviert
- Metadata für jeden Job
- Timestamp für Zeitreihen

**2. Transparenz:**
- Vollständige Logs
- Nachvollziehbare Ergebnisse
- Export in Standard-Formaten (JSON, CSV)

**3. Skalierbarkeit:**
- Automatisierter Workflow
- Batch-Processing
- Beliebig viele Jobs

**4. Zeitreihen-Analyse:**
- Archiv nach Monat organisiert
- Datum in Metadata
- Vergleiche über Zeit möglich

### Verwendung in der Arbeit

```
Kapitel 4: Datenerhebung
  "Stellenanzeigen wurden über einen Zeitraum von 6 Monaten
   gesammelt und mittels eines automatisierten Workflows
   verarbeitet. Pro Monat wurden durchschnittlich 20 Anzeigen
   analysiert (N=118 gesamt)."

Kapitel 5: Methodik
  "Der Workflow Manager ermöglichte eine standardisierte
   Verarbeitung aller Formate (PDF, DOCX, Google Docs) mit
   konsistenter Skill-Extraktion über 135+ definierte
   Kompetenzen."

Kapitel 6: Ergebnisse
  "Die automatisch generierten Reports zeigen eine durchschnittliche
   Skill-Coverage von 85% und 8-12 extrahierte Kompetenzen pro
   Stellenanzeige (Confidence: 93.5%)."
```

---

## ✅ ZUSAMMENFASSUNG

### Was ist jetzt möglich?

✅ **Manuelles Einlesen:** Neue Stellenanzeigen hinzufügen  
✅ **Automatische Auswertung:** Kompletter Workflow automatisiert  
✅ **Multi-Format:** PDF, DOCX, Google Docs  
✅ **Metadata:** Zusätzliche Informationen speichern  
✅ **Reports:** HTML + Text automatisch generiert  
✅ **Archivierung:** Chronologisch organisiert  
✅ **Export:** JSON, CSV (summary + detailed)  
✅ **Statistiken:** Tracking über Zeit  
✅ **Wissenschaftlich:** Reproduzierbar & transparent  

### Workflow in 3 Schritten

```python
# 1. Setup
manager = JobMiningWorkflowManager()

# 2. Jobs hinzufügen
manager.add_job_ad('job.pdf', metadata={...})

# 3. Auswerten
manager.run_workflow()

# Fertig! Ergebnisse in reports/ & results/
```

---

**Status:** 🟢 PRODUKTIONSREIF  
**Version:** 2.0 COMPLETE mit Workflow Manager  
**Features:** Upload ✅ | Auswertung ✅ | Reports ✅ | Archiv ✅

🎯 **Manuelles Einlesen + Automatische Auswertung ist jetzt implementiert!**
