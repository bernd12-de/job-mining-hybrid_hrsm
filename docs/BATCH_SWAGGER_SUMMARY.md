## 🎯 Batch-Progress Features im Swagger

### Zusammenfassung der neuen Endpoints für die **Batch-Analyse** mit **SSE-Streaming** und **Stop-Button**

---

## 📋 Endpoints

| HTTP | Path | Beschreibung | Status | Besonderheit |
|------|------|-------------|--------|--------------|
| **POST** | `/api/v1/jobs/batch-analyze` | Startet asynchrone Batch-Verarbeitung | 202 | **Non-blocking** – gibt sofort zurück |
| **GET** | `/api/v1/jobs/batch-status` | Abrufen aktueller Status | 200 | Polling-Alternative zu SSE |
| **GET** | `/api/v1/jobs/batch-progress-stream` | Live-Progress als SSE | 200 (stream) | **Real-time Updates** – Browser-freundlich |
| **DELETE** | `/api/v1/jobs/batch-progress` | Stop-Button (Abbruch) | 200/400 | Setzt Cancellation-Flag |

---

## 🚀 Workflow

```
User klickt "Starten"
         ↓
    POST /batch-analyze
         ↓ (202 Accepted)
    Server startet Batch asynchron
         ↓
    GET /batch-progress-stream (SSE-Verbindung)
         ↓
    Server pushed Updates alle 500ms
         ↓
    Browser aktualisiert UI (nicht jerky!)
         ↓
    User klickt "Stoppen" (optional)
         ↓
    DELETE /batch-progress (Cancellation-Flag)
         ↓
    Batch-Loop prüft Flag und bricht ab
         ↓
    Stream sendet "completed" Event
         ↓
    Fertig!
```

---

## 📊 Response-Format

### POST /batch-analyze
```json
{
  "status": "running",
  "progress": {
    "total": 28,
    "processed": 0,
    "percentage": 0,
    "status": "running",
    "startedAt": 1735385100000,
    "finishedAt": null,
    "progressBar": "░░░░░░░░░░",
    "current_file": "",
    "estimated_seconds_remaining": 0,
    "failed_count": 0,
    "skipped_count": 0
  }
}
```

### GET /batch-status
```json
{
  "total": 28,
  "processed": 7,
  "percentage": 25,
  "status": "running",
  "startedAt": 1735385100000,
  "finishedAt": null,
  "progressBar": "██░░░░░░░░",
  "current_file": "Job Posting #7 - Product Manager",
  "estimated_seconds_remaining": 126,
  "failed_count": 0,
  "skipped_count": 2
}
```

### GET /batch-progress-stream (SSE)
```
data: {"total":28,"processed":7,"percentage":25,"status":"running","current_file":"Job Posting #7","estimated_seconds_remaining":126,"failed_count":0,"skipped_count":2,"progress_bar":"██░░░░░░░░"}

data: {"total":28,"processed":15,"percentage":53,"status":"running","current_file":"Job Posting #15","estimated_seconds_remaining":63,"failed_count":1,"skipped_count":2,"progress_bar":"█████░░░░░"}

data: {"total":28,"processed":28,"percentage":100,"status":"completed","current_file":"","estimated_seconds_remaining":0,"failed_count":1,"skipped_count":3,"progress_bar":"██████████","finishedAt":1735385400123}
```

### DELETE /batch-progress
```json
{
  "status": "cancelled",
  "message": "Batch-Verarbeitung wurde gestoppt",
  "processed": 15,
  "total": 28
}
```

---

## 🎨 Neue Felder in BatchProgress

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `current_file` | String | Aktuelle Datei (z.B. "Job #7 - Product Manager") |
| `estimated_seconds_remaining` | Long | Geschätzte verbleibende Zeit in Sekunden |
| `failed_count` | Int | Anzahl fehlgeschlagener Jobs |
| `skipped_count` | Int | Anzahl übersprungener (duplikat) Jobs |
| `progressBar` | String | Visuelle Anzeige (█░░ 30%) |
| `status` | String | Zustand: "idle" \| "running" \| "completed" \| "cancelled" |

---

## 🔧 ETA-Berechnung

```
elapsed_seconds = (now - startedAt) / 1000
seconds_per_item = elapsed_seconds / processed

if (processed > 0 && processed < total):
    remaining_items = total - processed
    eta_seconds = seconds_per_item × remaining_items
else:
    eta_seconds = 0
```

**Beispiel:**
- Total: 28 Dateien
- Processed: 7 Dateien in 30 Sekunden
- Durchschnitt: 30 / 7 ≈ 4.3 Sekunden pro Datei
- Verbleibend: 28 - 7 = 21 Dateien
- ETA: 21 × 4.3 ≈ **90 Sekunden** (1.5 min)

---

## ✅ Besonderheiten

### 1. Non-Blocking (Kein Browser-Freeze)
- `POST /batch-analyze` gibt sofort 202 zurück
- Server verarbeitet asynchron in eigenem Thread
- Browser muss nicht warten

### 2. SSE statt Polling
- Server **pushed** Updates (nicht Client abrufen)
- Verbindung bleibt offen (~5 min Timeout)
- Nur echte Änderungen werden übertragen
- UI bleibt immer responsiv

### 3. Cancellation
- `DELETE /batch-progress` setzt Flag
- Batch-Loop prüft Flag nach jeder Datei
- Sauberes Shutdown ohne Ressourcen-Leak
- Verarbeitete Jobs werden trotzdem gespeichert

### 4. Fehlerbehandlung
- Fehler pro Datei werden getracked
- Batch läuft weiter (1 fehlgeschlagene Datei ≠ kompletter Fehler)
- `failed_count` und `skipped_count` in jedem Update
- Log-Nachrichten für Debugging

---

## 🧪 Test-Commands

### 1. Batch starten
```bash
curl -X POST http://localhost:8080/api/v1/jobs/batch-analyze
```

### 2. Status abrufen
```bash
curl http://localhost:8080/api/v1/jobs/batch-status
```

### 3. SSE im Terminal abonnieren
```bash
curl -N http://localhost:8080/api/v1/jobs/batch-progress-stream
```

### 4. Batch stoppen
```bash
curl -X DELETE http://localhost:8080/api/v1/jobs/batch-progress
```

### 5. SSE im Browser (DevTools Console)
```javascript
const es = new EventSource('http://localhost:8080/api/v1/jobs/batch-progress-stream');
es.onmessage = (e) => console.log('Progress:', JSON.parse(e.data));
es.addEventListener('completed', () => { console.log('Done!'); es.close(); });
es.onerror = (e) => console.error('Stream Error:', e);
```

---

## 🎯 Im Swagger UI

```
Servers: http://localhost:8080

/api/v1/jobs:
  
  POST /batch-analyze
    Summary: Batch-Analyse lokaler Dateien
    Description: Verarbeitet alle Stellenanzeigen-Dateien aus dem Python 'data/jobs' Ordner
    Responses:
      202: Batch akzeptiert (progress)
      500: Interner Fehler
  
  GET /batch-status
    Summary: Status der Batch-Verarbeitung
    Description: Abrufen des aktuellen Fortschritts (Poll-Alternatve)
    Responses:
      200: BatchProgress (JSON)
  
  GET /batch-progress-stream
    Summary: Batch-Progress Streaming (SSE)
    Description: Live-Fortschritt als Server-Sent Events (Browser-freundlich)
    Produces: text/event-stream
    Responses:
      200: Server-Sent Events Stream
      
  DELETE /batch-progress
    Summary: Batch-Verarbeitung stoppen
    Description: Sendet Stop-Signal an laufende Batch
    Responses:
      200: Batch gestoppt (status, processed, total)
      400: Keine laufende Batch
```

---

## 📊 Browser-Demo

HTML-Interface mit Live-Updates:
- 📈 Fortschrittsbalken (mit % und visuellem █░░)
- 📄 Aktuelle Datei
- ⏱️ Geschätzte Restzeit
- 📊 Fehler-/Skipped-Zählung
- 🛑 Start/Stop-Buttons
- 📝 Live-Log der Ereignisse

**Siehe:** `kotlin-api/batch-progress-demo.html`

---

## 🔐 Sicherheit

- Keine Authentifizierung/Autorisierung in diesem POC
- SSE-Stream wird nach **5 Minuten** geschlossen
- Cancellation kann jederzeit erfolgen
- Keine Datei-Uploads über Batch-Endpoint

---

## 🚀 Performance

- **Durchsatz:** ~1-5 Dateien/Sekunde (abhängig von Python-Backend)
- **Memory:** Streaming reduziert RAM-Nutzung
- **Network:** SSE effizienter als Polling (500ms Intervall)
- **UI:** Immer responsiv (async + push-based)

---

## 📝 Beispiel-Integration (Frontend)

```javascript
class BatchProgressManager {
    constructor(apiBase = 'http://localhost:8080/api/v1/jobs') {
        this.apiBase = apiBase;
        this.eventSource = null;
        this.isRunning = false;
    }
    
    async start() {
        const res = await fetch(`${this.apiBase}/batch-analyze`, { method: 'POST' });
        if (res.ok) {
            this.isRunning = true;
            this.connectStream();
        }
    }
    
    connectStream() {
        this.eventSource = new EventSource(`${this.apiBase}/batch-progress-stream`);
        
        this.eventSource.addEventListener('progress', (e) => {
            const progress = JSON.parse(e.data);
            console.log(`${progress.processed}/${progress.total} | ETA: ${progress.estimated_seconds_remaining}s`);
            this.updateUI(progress);
        });
        
        this.eventSource.addEventListener('completed', (e) => {
            console.log('✅ Batch completed!');
            this.isRunning = false;
            this.eventSource.close();
        });
    }
    
    async stop() {
        const res = await fetch(`${this.apiBase}/batch-progress`, { method: 'DELETE' });
        if (res.ok) {
            console.log('⏹️ Batch stopped!');
            this.isRunning = false;
            this.eventSource?.close();
        }
    }
    
    updateUI(progress) {
        // Update DOM elements
        document.getElementById('progress').textContent = `${progress.percentage}%`;
        document.getElementById('current').textContent = progress.current_file;
        document.getElementById('eta').textContent = `${Math.round(progress.estimated_seconds_remaining / 60)} min`;
    }
}

// Nutzung
const manager = new BatchProgressManager();
document.getElementById('start-btn').onclick = () => manager.start();
document.getElementById('stop-btn').onclick = () => manager.stop();
```

---

## ✨ Zusammenfassung

| Feature | Zustand | Details |
|---------|---------|---------|
| Non-blocking Batch | ✅ | POST gibt 202 zurück |
| SSE Streaming | ✅ | GET /batch-progress-stream |
| Stop-Button | ✅ | DELETE /batch-progress |
| ETA-Berechnung | ✅ | Automatisch berechnet |
| Aktuelle Datei | ✅ | `current_file` Feld |
| Fehler-Tracking | ✅ | `failed_count` / `skipped_count` |
| Swagger-Docs | ✅ | Automatisch generiert |
| HTML-Demo | ✅ | `batch-progress-demo.html` |
