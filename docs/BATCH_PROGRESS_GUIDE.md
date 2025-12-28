# 🎯 Batch-Progress mit SSE-Streaming & Stop-Button

## Übersicht

Die **erweiterte Batch-Verarbeitung** verhindert Browser-Freeze durch **Server-Sent Events (SSE)** und zeigt Live-Updates ohne Polling:

```
✨ Neue Features:
✅ Live-Fortschrittsanzeige (keine Polling nötig)
✅ Aktuelle Datei-Anzeige (welche Datei wird gerade verarbeitet)
✅ ETA-Berechnung (wie lange noch?)
✅ Fehler- und Skipped-Zählung
✅ Stop-Button zum Abbrechen
✅ Browser bleibt flüssig (async Verarbeitung)
```

---

## 🔧 Neue Endpoints

### 1. **POST /api/v1/jobs/batch-analyze** (Batch starten)

```bash
curl -X POST http://localhost:8080/api/v1/jobs/batch-analyze
```

**Response (202 Accepted):**
```json
{
  "status": "running",
  "progress": {
    "total": 28,
    "processed": 0,
    "percentage": 0,
    "status": "running",
    "current_file": "",
    "estimated_seconds_remaining": 0,
    "failed_count": 0,
    "skipped_count": 0,
    "progress_bar": "░░░░░░░░░░"
  }
}
```

---

### 2. **GET /api/v1/jobs/batch-progress-stream** (SSE Live-Updates)

```bash
curl -X GET http://localhost:8080/api/v1/jobs/batch-progress-stream
```

**Event Format (Server-Sent Events):**
```
event: progress
id: 3
data: {"total":28,"processed":3,"percentage":10,"status":"running","current_file":"Job Posting #3 - Software Engineer","estimated_seconds_remaining":180,"failed_count":0,"skipped_count":1,"progress_bar":"█░░░░░░░░░"}

event: progress
id: 7
data: {"total":28,"processed":7,"percentage":25,"status":"running","current_file":"Job Posting #7 - Product Manager","estimated_seconds_remaining":126,"failed_count":0,"skipped_count":2,"progress_bar":"██░░░░░░░░"}

event: completed
id: done
data: {"total":28,"processed":28,"percentage":100,"status":"completed","current_file":"","estimated_seconds_remaining":0,"failed_count":1,"skipped_count":3,"progress_bar":"██████████","finishedAt":1735385400123}
```

**Browser-Implementierung:**
```javascript
const eventSource = new EventSource('http://localhost:8080/api/v1/jobs/batch-progress-stream');

eventSource.addEventListener('progress', (e) => {
    const data = JSON.parse(e.data);
    console.log(`${data.processed}/${data.total} | ETA: ${data.estimated_seconds_remaining}s`);
    console.log(`Aktuell: ${data.current_file}`);
});

eventSource.addEventListener('completed', (e) => {
    console.log('✅ Fertig!');
    eventSource.close();
});
```

---

### 3. **DELETE /api/v1/jobs/batch-progress** (Stop-Button)

```bash
curl -X DELETE http://localhost:8080/api/v1/jobs/batch-progress
```

**Response (200 OK):**
```json
{
  "status": "cancelled",
  "message": "Batch-Verarbeitung wurde gestoppt",
  "processed": 15,
  "total": 28
}
```

**Wenn keine Batch läuft (400 Bad Request):**
```json
{
  "error": "Keine laufende Batch-Verarbeitung (Status: idle)"
}
```

---

### 4. **GET /api/v1/jobs/batch-status** (Status abrufen)

```bash
curl -X GET http://localhost:8080/api/v1/jobs/batch-status
```

**Response:**
```json
{
  "total": 28,
  "processed": 15,
  "percentage": 53,
  "status": "running",
  "current_file": "Job Posting #15 - Data Scientist",
  "estimated_seconds_remaining": 63,
  "failed_count": 1,
  "skipped_count": 2,
  "progress_bar": "█████░░░░░",
  "startedAt": 1735385100000,
  "finishedAt": null
}
```

---

## 🏗️ Technische Details

### BatchProgressService.kt

**Neue Felder:**
```kotlin
data class BatchProgress(
    val total: Int = 0,
    val processed: Int = 0,
    val percentage: Int = 0,
    val status: String = "idle", // idle|running|completed|cancelled
    val startedAt: Long? = null,
    val finishedAt: Long? = null,
    val progressBar: String = "",
    val currentFile: String = "",              // ← NEU
    val estimatedSecondsRemaining: Long = 0,  // ← NEU
    val failedCount: Int = 0,                 // ← NEU
    val skippedCount: Int = 0                 // ← NEU
)
```

**Neue Methoden:**
```kotlin
fun cancel() {
    cancellationRequested = true
    // Status wird auf "cancelled" gesetzt
}

fun isCancellationRequested(): Boolean {
    // Batch-Loop prüft das regelmäßig
}
```

**ETA-Berechnung:**
```
ETA = (elapsed_seconds / processed_items) × remaining_items
```

---

### JobMiningService.kt Batch-Loop

**Cancellation-Check:**
```kotlin
resultsDto.forEach { resultDto ->
    // 🛑 CANCELLATION CHECK
    if (progress.isCancellationRequested()) {
        println("⛔ BATCH ABGEBROCHEN: User hat Stop geklickt...")
        return@forEach // Foreach beendet
    }
    // ... weitere Verarbeitung
}
```

**Progress Update mit Details:**
```kotlin
progress.update(
    processed = processedCount,
    percentage = (processedCount * 100) / total,
    bar = "█".repeat(pct/10) + "░".repeat(10 - pct/10),
    currentFile = resultDto.title.take(50),  // ← Dateinamen
    failedCount = failedCount,
    skippedCount = skippedCount
)
```

---

### SSE-Streaming Endpoint

```kotlin
@GetMapping("/batch-progress-stream", produces = ["text/event-stream"])
fun batchProgressStream(): ResponseEntity<*> {
    val emitter = SseEmitter(300_000L) // 5 min Timeout
    
    Thread {
        // Poll alle 500ms auf Änderungen
        while (status == "running") {
            if (currentSnapshot != lastSnapshot) {
                emitter.send(event().data(currentSnapshot))
            }
            Thread.sleep(500)
        }
        emitter.complete() // Stream schließen
    }.start()
    
    return ResponseEntity.ok(emitter)
}
```

**Warum SSE statt Polling?**
- ✅ Server pushed Updates (nicht Client abrufen)
- ✅ Weniger Netzwerk-Traffic
- ✅ Real-time (kein Verzug)
- ✅ Browser bleibt immer responsiv
- ✅ Automatisches Reconnect bei Netzwerk-Fehler

---

## 🎨 Frontend Demo

Siehe: [batch-progress-demo.html](./batch-progress-demo.html)

**Live-Demo starten:**
```bash
# Datei im Browser öffnen
open kotlin-api/batch-progress-demo.html

# Oder mit lokalen Server:
python3 -m http.server 8001 -d kotlin-api/
# Dann: http://localhost:8001/batch-progress-demo.html
```

**Dashboard zeigt:**
- 📊 Fortschrittsbalken (visuell + %)
- 📄 Aktuelle Datei
- ⏱️ Geschätzte Restzeit
- ❌ Fehler-/Skipped-Zählung
- 🛑 Stop-Button (live)

---

## 🔄 Workflow-Beispiel (JavaScript)

```javascript
// 1. Batch starten
const startRes = await fetch('/api/v1/jobs/batch-analyze', {
    method: 'POST'
});
// → Server antwortet sofort mit 202 (nicht blocking)

// 2. Live-Updates abonnieren
const eventSource = new EventSource('/api/v1/jobs/batch-progress-stream');

eventSource.addEventListener('progress', (e) => {
    const {processed, total, current_file, estimated_seconds_remaining} = JSON.parse(e.data);
    
    // UI aktualisieren (nicht blocking!)
    updateProgressBar(processed / total);
    updateCurrentFile(current_file);
    updateETA(estimated_seconds_remaining);
});

// 3. User klickt Stop-Button
async function stopBatch() {
    const stopRes = await fetch('/api/v1/jobs/batch-progress', {
        method: 'DELETE'
    });
    const {processed, total} = await stopRes.json();
    eventSource.close();
}

// 4. Server schließt Stream wenn fertig
eventSource.addEventListener('completed', (e) => {
    console.log('✅ Batch fertig!');
    eventSource.close();
});
```

---

## 🚀 Vorher vs. Nachher

### ❌ Vorher (Polling)
```
POST /batch-analyze → 202
Loop every 500ms: GET /batch-status
→ Browser wartet (60+ Requests!)
→ Potentiell jerky UI
→ Netzwerk-Spam
```

### ✅ Nachher (SSE)
```
POST /batch-analyze → 202
GET /batch-progress-stream (WebSocket-ähnlich)
← Server pushed Updates automatisch
← Nur echte Änderungen werden gesendet
← UI immer smooth
← Browser ist nie "busy"
```

---

## 📊 Swagger UI

In Swagger sind die neuen Endpoints automatisch dokumentiert:
- **POST** `/api/v1/jobs/batch-analyze` - Batch starten (202)
- **GET** `/api/v1/jobs/batch-progress-stream` - SSE Live-Stream
- **DELETE** `/api/v1/jobs/batch-progress` - Stop-Button
- **GET** `/api/v1/jobs/batch-status` - Status abrufen

---

## 🐛 Debugging

**Logs checken:**
```bash
docker logs -f kotlin-api | grep -E "BATCH|Progress|Cancelled"
```

**SSE im Browser testen:**
```javascript
// DevTools Console
const es = new EventSource('http://localhost:8080/api/v1/jobs/batch-progress-stream');
es.onmessage = (e) => console.log('Progress:', e.data);
es.addEventListener('completed', (e) => console.log('Done!', e.data));
```

---

## ✅ Checkliste

- [x] BatchProgressService mit currentFile, ETA, failed/skipped
- [x] SSE-Streaming Endpoint (kein Browser-Freeze)
- [x] Stop-Button (DELETE /batch-progress)
- [x] Cancellation-Flag im Batch-Loop
- [x] HTML-Demo (batch-progress-demo.html)
- [x] Swagger-Dokumentation
- [ ] Tests schreiben (optional)
- [ ] In Streamlit-Dashboard integrieren (next step)

---

## 🎯 Nächste Schritte

1. **Streamlit-Integration** - SSE in Dashboard anzeigen
2. **WebSocket** - Optional für noch bessere Performance
3. **Fehler-Details** - Welche Datei ist fehlgeschlagen?
4. **Resumable Batch** - Pause & Resume support
