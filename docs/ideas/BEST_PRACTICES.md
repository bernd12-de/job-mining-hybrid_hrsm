# 🏆 Best Practices für Konzept-Material

**Zweck:** Leitfaden für das Erstellen von Code-Ideen und Konzepten

---

## 📝 1. DATEI-HEADER

Jede Konzept-Datei MUSS mit einem klaren Header beginnen:

### Python-Beispiel:
```python
# 🔵 KONZEPT - Kurze Beschreibung (max. 50 Zeichen)
# NICHT in Produktion verwenden!
#
# Autor: Dein Name
# Datum: 2024-12-27
# Status: KONZEPT | POC | BEREIT | VERWORFEN

"""
Ausführliche Beschreibung der Idee.

Was macht dieser Code?
Warum ist er nützlich?
Welches Problem löst er?
"""
```

### Kotlin-Beispiel:
```kotlin
// 🔵 KONZEPT - Kurze Beschreibung
// NICHT in Produktion verwenden!
//
// Autor: Dein Name
// Datum: 2024-12-27
// Status: KONZEPT | POC | BEREIT | VERWORFEN

/**
 * Ausführliche Beschreibung der Idee.
 *
 * Was macht dieser Code?
 * Warum ist er nützlich?
 * Welches Problem löst er?
 */
```

---

## 🏷️ 2. STATUS-KENNZEICHNUNG

Verwende immer eines dieser Emojis:

| Emoji | Status | Verwendung |
|-------|--------|------------|
| 🔵 | **KONZEPT** | Nur Idee, nicht getestet |
| 🟡 | **POC** | Proof of Concept, funktioniert teilweise |
| 🟢 | **BEREIT** | Fertig, kann in Produktion |
| 🔴 | **VERWORFEN** | Idee aufgegeben, als Referenz |

**Beispiel:**
```python
# 🔵 KONZEPT - Automatische Skill-Extraktion mit BERT
```

---

## 📂 3. ORDNER-STRUKTUR

Jedes Feature-Konzept sollte einen eigenen Ordner haben:

```
docs/ideas/
└── mein-feature/
    ├── README.md          # Übersicht und Beschreibung
    ├── example_code.py    # Beispiel-Implementierung
    ├── tests.py           # Tests (optional)
    ├── requirements.txt   # Dependencies (falls POC)
    └── sample_data/       # Test-Daten (optional)
        └── example.json
```

### README.md Template:

```markdown
# Feature-Name

**Status:** 🔵 KONZEPT

## Idee

Beschreibe die Hauptidee in 2-3 Sätzen.

## Ziele

- Ziel 1
- Ziel 2
- Ziel 3

## Anwendungsfälle

- Use Case 1
- Use Case 2

## Beispiel-Code

Siehe Dateien in diesem Verzeichnis:
- `example_code.py` - Hauptimplementierung
- `tests.py` - Tests

## Technologien

- Library 1
- Library 2

## Offene Fragen

- Frage 1?
- Frage 2?

## Nächste Schritte

- [ ] Schritt 1
- [ ] Schritt 2
```

---

## 💻 4. CODE-QUALITÄT

Auch Konzept-Code sollte sauber sein:

### ✅ GUT:

```python
# 🔵 KONZEPT - Dokumenttyp-Klassifizierung

from enum import Enum
from typing import Dict, List

class DocumentType(str, Enum):
    """Unterstützte Dokumenttypen."""
    JOB_POSTING = "job_posting"
    MODULE_HANDBOOK = "module_handbook"

class Classifier:
    """
    Klassifiziert Dokumente anhand von Keywords.

    TODO: Später ML-basiert implementieren.
    """

    def classify(self, text: str) -> DocumentType:
        """
        Klassifiziert einen Text.

        Args:
            text: Der zu klassifizierende Text

        Returns:
            Der erkannte Dokumenttyp
        """
        # Implementation...
        pass

# BEISPIEL-VERWENDUNG
if __name__ == "__main__":
    classifier = Classifier()
    result = classifier.classify("Test")
    print(f"Ergebnis: {result}")
```

### ❌ SCHLECHT:

```python
# irgendwas mit dokumenten

def classify(x):  # ❌ Keine Docstring
    # ❌ Keine Typen
    return "job"  # ❌ Magic String

# ❌ Kein Beispiel
# ❌ Keine Erklärung
```

---

## 🧪 5. PROOF OF CONCEPT (POC)

Wenn dein Konzept funktioniert, mache es zu einem POC:

### Checklist für POC:

- [ ] Code ist lauffähig
- [ ] Beispiel-Verwendung funktioniert
- [ ] Test-Daten sind vorhanden
- [ ] Dependencies sind dokumentiert (requirements.txt)
- [ ] README erklärt, wie man es ausführt
- [ ] Ergebnisse sind dokumentiert (Screenshots/Output)

### Beispiel:

```
docs/ideas/document-classifier-poc/
├── README.md
│   └── "Wie ausführen: python classifier.py"
├── classifier.py          # Hauptcode
├── requirements.txt       # pandas==2.0.0
├── test_data/
│   ├── modulhandbuch.pdf
│   ├── stellenanzeige.pdf
│   └── fachbuch.pdf
└── results/
    └── classification_results.json
```

**README.md:**
```markdown
# 🟡 POC - Dokumenttyp-Klassifizierung

## Setup

```bash
pip install -r requirements.txt
python classifier.py
```

## Ergebnisse

Getestet mit 10 Dokumenten:
- ✅ 8/10 korrekt klassifiziert (80%)
- ❌ 2 Fehler bei ähnlichen Dokumenten

## Nächste Schritte

- Konfidenz-Score hinzufügen
- Mehr Test-Daten sammeln
- ML-Modell trainieren
```

---

## 📊 6. BEISPIEL-DATEN

Wenn du Test-Daten benötigst:

### ✅ GUT:

```
sample_data/
├── README.md  # Erklärt die Daten
├── minimal_example.json  # Kleines Beispiel
└── full_example.json     # Vollständiges Beispiel
```

**sample_data/README.md:**
```markdown
# Test-Daten

## minimal_example.json
Minimales Beispiel mit 3 Kompetenzen.

## full_example.json
Vollständiges Beispiel mit allen Feldern.

**Wichtig:** Keine echten/persönlichen Daten!
```

### ❌ SCHLECHT:

- Echte Kundendaten
- Persönliche Informationen
- Große Dateien (>1MB)
- Binärdateien ohne Erklärung

---

## 🔗 7. VERWEISE

Verlinke verwandte Konzepte:

```markdown
# Skill-Gap-Analyse

## Abhängigkeiten

Benötigt folgende Konzepte:
- [Modulhandbuch-Support](../module-handbook-support/)
- [Dokumenttyp-Klassifizierung](../module-handbook-support/document_classifier.py)

## Verwandte Ideen

Siehe auch:
- [Advanced NLP](../advanced-nlp/)
- [Textbook-Analysis](../textbook-analysis/)
```

---

## 🎯 8. VON KONZEPT → PRODUKTION

Wenn ein Konzept reif ist:

### Checkliste:

1. **Status auf 🟢 BEREIT setzen**
   ```python
   # 🟢 BEREIT - Dokumenttyp-Klassifizierung
   ```

2. **Issue erstellen auf GitHub**
   ```
   Titel: [Feature] Dokumenttyp-Klassifizierung implementieren
   Label: enhancement, ready-for-dev
   Beschreibung: Siehe docs/ideas/document-classifier/
   ```

3. **Plan erstellen**
   - Was muss angepasst werden?
   - Wo wird es integriert?
   - Welche Tests sind nötig?

4. **Code übertragen**
   - Von `/docs/ideas/` nach `/python-backend/` oder `/kotlin-api/`
   - Package-Struktur anpassen
   - Imports korrigieren
   - Produktiv-taugliche Error-Handling

---

## 🚫 9. WAS VERMEIDEN

### ❌ NICHT TUN:

1. **Kein Status-Emoji**
   ```python
   # Irgendwas mit Klassifizierung  ❌
   ```

2. **Produktiv-Code in /docs/ideas/**
   ```
   docs/ideas/
   └── production_service.py  ❌ Gehört nach python-backend/
   ```

3. **Konzept-Code in Produktion**
   ```kotlin
   // In kotlin-api/service/
   // 🔵 KONZEPT - NUR ZUM TESTEN  ❌ Nicht in Produktion!
   ```

4. **Keine Dokumentation**
   ```
   docs/ideas/my-feature/
   └── code.py  ❌ Wo ist README.md?
   ```

5. **Zu viel Code**
   ```python
   # 2000 Zeilen Konzept-Code  ❌ Zu groß!
   # Besser: Kleinere Module
   ```

---

## ✅ 10. GUTE BEISPIELE

### Exzellentes Konzept:

**docs/ideas/module-handbook-support/document_classifier.py**

✅ Hat alles:
- Klarer Header mit Status
- Docstrings
- Typ-Annotationen
- Beispiel-Verwendung
- Test-Cases
- TODO-Kommentare für Verbesserungen

### Verbesserungswürdig:

**docs/ideas/module-handbook-support/ModuleHandbook.kt**

⚠️ Fehlt:
- Import für `Competence`

✅ Gut:
- Klare Struktur
- Gute Kommentare
- JPA-Annotationen

---

## 📚 ZUSAMMENFASSUNG

**Must-Have:**
1. 🏷️ Status-Emoji (🔵/🟡/🟢/🔴)
2. 📝 README.md im Ordner
3. 💻 Sauberer, dokumentierter Code
4. ⚠️ Warnung "NICHT in Produktion"

**Nice-to-Have:**
5. 🧪 Beispiel-Verwendung
6. 📊 Test-Daten
7. 🔗 Verweise auf verwandte Konzepte
8. ✅ Checkliste für nächste Schritte

**Never:**
- ❌ Produktiv-Code in /docs/ideas/
- ❌ Konzept-Code ohne Status
- ❌ Echte/sensible Daten
- ❌ Undokumentierter Code

---

**Fragen?** Frag einfach! Ich helfe dir, deine Ideen zu strukturieren.
