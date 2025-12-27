# 🔧 Behebbare Fehler im Konzept-Code

## ModuleHandbook.kt

### ❌ Fehler: Fehlender Import für Competence

**Zeile 50:**
```kotlin
val competences: List<Competence> = emptyList()
//                    ^^^^^^^^^^
// Fehler: Competence ist nicht importiert!
```

### ✅ Fix:

**Option 1: Import hinzufügen** (wenn Competence in separater Datei)
```kotlin
package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDate

// NEU:
// (Competence ist bereits in derselben Package, sollte verfügbar sein)
```

**Option 2: In derselben Datei definieren**
```kotlin
// Am Ende der Datei:

@Entity
data class Competence(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val originalTerm: String,
    val escoLabel: String,
    val escoUri: String,
    val confidenceScore: Double,
    val escoGroupCode: String? = null
)
```

### 📝 Hinweis:

In Kotlin müssen Klassen im selben Package nicht explizit importiert werden.
Da `ModuleHandbook` im Package `de.layher.jobmining.kotlinapi.domain` ist,
und `Competence` auch dort sein sollte, ist KEIN Import nötig.

**ABER:** Der Code ist nur ein Konzept und wird noch nicht kompiliert.
Wenn er in Produktion geht, muss sichergestellt sein dass:
- Entweder `Competence` im selben Package liegt
- Oder der korrekte Import vorhanden ist

---

## document_classifier.py

### ✅ Keine Fehler gefunden!

Der Code ist sehr gut strukturiert:
- ✅ Saubere Typen (Enum, Dict, List)
- ✅ Docstrings vorhanden
- ✅ Beispiel-Verwendung
- ✅ Test-Cases
- ✅ TODO-Kommentare

### 🟡 Verbesserungsvorschläge:

1. **Gewichtete Keywords**
   ```python
   # Statt allen Keywords gleiche Gewichtung:
   weighted_indicators = {
       DocumentType.MODULE_HANDBOOK: {
           "modulhandbuch": 5,    # Sehr starker Indikator
           "ects": 3,             # Starker Indikator
           "studiengang": 3,
           "semester": 1          # Schwacher Indikator
       }
   }
   ```

2. **Konfidenz-Berechnung verbessern**
   ```python
   def classify_with_confidence(self, text: str, filename: str = ""):
       # Aktuell: Vereinfachte Logik
       # Besser: Verhältnis der Scores

       scores = self._calculate_scores(text, filename)
       total = sum(scores.values())

       if total == 0:
           return DocumentType.UNKNOWN, 0.0

       max_score = max(scores.values())
       confidence = max_score / total  # Relativer Anteil

       doc_type = self._get_best_match(scores)
       return doc_type, confidence
   ```

3. **Multi-Label-Klassifikation**
   ```python
   # Ein Dokument kann mehrere Typen haben
   # z.B. Modulhandbuch + Fachbuch-Referenzen

   def classify_multi_label(self, text: str, threshold: float = 0.3):
       """Gibt alle Typen zurück, die über Threshold liegen."""
       scores = self._calculate_scores(text)
       results = []

       for doc_type, score in scores.items():
           if score >= threshold:
               results.append((doc_type, score))

       return sorted(results, key=lambda x: x[1], reverse=True)
   ```

---

## Zusammenfassung

| Datei | Status | Fehler | Schweregrad |
|-------|--------|--------|-------------|
| ModuleHandbook.kt | 🔵 KONZEPT | Import fehlt (theoretisch) | 🟢 Niedrig |
| document_classifier.py | 🔵 KONZEPT | Keine | ✅ Keine |

**Empfehlung:**
- ModuleHandbook.kt: Hinweis hinzufügen, dass Competence im selben Package sein muss
- document_classifier.py: Von 🔵 KONZEPT → 🟡 POC (ist schon testbar!)

---

**Nächster Schritt:**
Teste document_classifier.py mit echten PDFs und messe die Genauigkeit!
