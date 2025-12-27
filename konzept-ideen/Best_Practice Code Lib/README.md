# 🏗️ REFACTORED ARCHITECTURE - Job Mining Projekt

## Clean Architecture nach Buchprinzipien

Diese Architektur implementiert:
- ✅ **Separation of Concerns** (Gharbi: Softwarearchitektur)
- ✅ **Single Responsibility Principle** (ML Engineering with Python)
- ✅ **Bounded Context** (Domain-Driven Design)
- ✅ **Open/Closed Principle** (erweiterbar ohne Änderung)
- ✅ **Dependency Injection** (testbar & wartbar)

---

## 📁 Struktur

```
refactored_architecture/
│
├── data/                           ← DATEN LAYER
│   └── competences/
│       ├── domains/               ← Bounded Contexts (Domains getrennt!)
│       │   ├── ux_design.json
│       │   ├── product_management.json
│       │   └── agile_methods.json
│       ├── sources/               ← Externe Quellen
│       └── config/
│           └── data_sources.yaml  ← Konfiguration
│
├── models/                         ← DOMAIN MODELS
│   ├── enums.py                   ← CompetenceType, JobCategory
│   └── competence.py              ← Competence Entity
│
├── repositories/                   ← DATA ACCESS LAYER
│   ├── base_repository.py         ← Abstract Base
│   ├── competence_repository.py   ← Main Repository
│   └── adapters/                  ← Adapter Pattern
│       ├── json_adapter.py        ← JSON Loader
│       ├── csv_adapter.py         ← CSV Loader (ESCO)
│       └── api_adapter.py         ← API Loader (Zukunft)
│
└── services/                       ← SERVICE LAYER (NUR LOGIK!)
    ├── competence_matcher.py      ← Matching-Logik
    └── competence_extraction.py   ← Hauptservice
```

---

## 🎯 Architektur-Prinzipien

### 1. Separation of Concerns

**Problem ALT:**
```python
class CompetenceLibrary:
    def _create_curated_library(self):
        competences = {
            'Figma': {...},  # ← DATEN im CODE!
            'Scrum': {...},
            # ... 200+ weitere ...
        }
```

**Lösung NEU:**
```python
# DATEN in JSON-Dateien
data/competences/domains/ux_design.json

# SERVICE lädt Daten vom Repository
class CompetenceExtractionService:
    def __init__(self):
        self.repository = CompetenceRepository()  # ← Dependency Injection
        self.library = self.repository.get_all_competences()
```

### 2. Single Responsibility

Jede Klasse hat **EINE** Verantwortung:

| Klasse | Verantwortung |
|--------|---------------|
| `CompetenceRepository` | Daten laden |
| `JsonAdapter` | JSON parsen |
| `CompetenceMatcher` | Matching-Logik |
| `CompetenceExtractionService` | Orchestrierung |

### 3. Bounded Context (DDD)

Domains sind **getrennt**:
- `ux_design.json` - nur UX/UI Kompetenzen
- `product_management.json` - nur Product Mgmt
- `agile_methods.json` - nur Agile

→ Klare Grenzen, einfach zu verstehen!

### 4. Open/Closed Principle

**Erweiterbar OHNE Code zu ändern:**

#### Neue Kompetenz hinzufügen:
```bash
# Einfach JSON editieren:
vim data/competences/domains/ux_design.json

# Hinzufügen:
{
  "name": "Adobe XD",
  "category": "UX Tools",
  ...
}

# Fertig! Kein Code geändert!
```

#### Neue Domain hinzufügen:
```bash
# Neue Datei erstellen:
touch data/competences/domains/devops.json

# Mit Kompetenzen füllen
# Wird automatisch geladen!
```

#### API-Anbindung aktivieren:
```yaml
# data/competences/config/data_sources.yaml
sources:
  - name: "esco_api"
    enabled: true  # ← Einfach auf true setzen!
```

---

## 🚀 Verwendung

### Basis-Setup

```python
from services.competence_extraction import CompetenceExtractionService
from models.job_ad import JobAd

# Config
class Config:
    competence_config = "data/competences/config/data_sources.yaml"

# Service initialisieren
service = CompetenceExtractionService(Config())

# Kompetenzen extrahieren
job_ads = [JobAd(...), JobAd(...)]
processed = service.extract_all(job_ads)

# Statistiken
stats = service.get_extraction_stats()
print(f"Bibliothek: {stats['library_stats']['total']} Kompetenzen")
```

### Neue Quelle hinzufügen

```python
from repositories.adapters.json_adapter import JsonAdapter

# Neuen Adapter erstellen
custom_adapter = JsonAdapter(
    file_pattern="data/custom_skills/*.json",
    enabled=True
)

# Zum Repository hinzufügen
service.repository.add_adapter(custom_adapter)

# Bibliothek neu laden
service.reload_library()
```

---

## 📊 Vorteile vs. Alte Architektur

| Aspekt | ALT | NEU |
|--------|-----|-----|
| **Lines of Code** | 830 Zeilen | ~200 Zeilen (Service) |
| **Neue Kompetenz** | Code ändern | JSON editieren |
| **Neue Domain** | Code erweitern | Neue JSON-Datei |
| **API-Integration** | Umschreiben | Config aktivieren |
| **Testbarkeit** | Schwierig | Einfach (Mocking) |
| **Wartbarkeit** | Schwer | Einfach |
| **Datenänderung** | Deployment | Datei austauschen |
| **Bounded Contexts** | ❌ Alles zusammen | ✅ Domains getrennt |

---

## 🧪 Testing

### Repository testen:
```python
def test_repository():
    repo = CompetenceRepository("test_config.yaml")
    comps = repo.get_all_competences()
    assert len(comps) > 0
```

### Matcher testen:
```python
def test_matcher():
    matcher = CompetenceMatcher()
    text = "Experience with Figma and Sketch required"
    
    library = [
        Competence(name="Figma", category="UX Tools", ...),
        Competence(name="Sketch", category="UX Tools", ...)
    ]
    
    found = matcher.find_matches(text, library)
    assert len(found) == 2
```

### Service testen (mit Mock):
```python
def test_service_with_mock():
    # Repository mocken
    mock_repo = Mock()
    mock_repo.get_all_competences.return_value = [...]
    
    service = CompetenceExtractionService(config)
    service.repository = mock_repo
    
    # Test durchführen
    ...
```

---

## 🔧 Erweiterung

### Neue JSON-Domain erstellen:

```json
{
  "domain": "DevOps",
  "version": "1.0",
  "competences": [
    {
      "name": "Docker",
      "category": "DevOps Tool",
      "type": "tool",
      "alternative_labels": ["Docker Container"],
      "esco_uri": "esco:skill/docker",
      "confidence": 1.0
    },
    {
      "name": "Kubernetes",
      "category": "DevOps Tool",
      "type": "platform",
      "alternative_labels": ["K8s"],
      "esco_uri": "esco:skill/kubernetes",
      "confidence": 1.0
    }
  ]
}
```

Speichern als: `data/competences/domains/devops.json`

### Eigenen Adapter erstellen:

```python
from repositories.base_repository import BaseRepository

class DatabaseAdapter(BaseRepository):
    """Lädt Kompetenzen aus Datenbank"""
    
    def __init__(self, connection_string):
        self.connection = connect(connection_string)
    
    def load(self) -> List[Competence]:
        # SQL query
        rows = self.connection.execute("SELECT * FROM competences")
        
        # Convert to Competence objects
        return [self._parse_row(row) for row in rows]
    
    def is_enabled(self) -> bool:
        return True

# Verwendung:
db_adapter = DatabaseAdapter("postgresql://...")
service.repository.add_adapter(db_adapter)
```

---

## 📚 Theoretische Grundlagen

Diese Architektur basiert auf:

1. **Gharbi (2024): Softwarearchitektur**
   - Trennung von Verantwortlichkeiten
   - Information Hiding
   - Schmale Schnittstellen

2. **ML Engineering with Python (2024)**
   - SOLID Principles
   - Separation of Concerns
   - Bounded Contexts

3. **Domain-Driven Design (DDD)**
   - Bounded Context
   - Repository Pattern
   - Domain Models

---

## ✅ Checkliste: Gute Architektur

- [x] Daten getrennt von Logik
- [x] Jede Klasse eine Verantwortung
- [x] Erweiterbar ohne Änderung
- [x] Domains klar getrennt
- [x] Testbar (Dependency Injection)
- [x] Wartbar (kleine Klassen)
- [x] Dokumentiert
- [x] Config-basiert
- [x] Cache-fähig
- [x] Logging

---

## 🎉 Zusammenfassung

**Vorher:** 830 Zeilen Code mit Daten vermischt
**Nachher:** Clean Architecture mit getrennten Layers

**Neue Kompetenz:**
- Vorher: Code ändern, testen, deployen
- Nachher: JSON editieren, fertig!

**Neue Domain:**
- Vorher: Code erweitern, umschreiben
- Nachher: Neue JSON-Datei erstellen

**API-Anbindung:**
- Vorher: Alles umschreiben
- Nachher: Config-Flag auf `true` setzen
