# 🎨 Batch-Progress Swagger UI Guide

## Wo sind die neuen Endpoints?

Öffne: `http://localhost:8080/swagger-ui.html` nach dem Build

---

## 📍 Navigieren zu `/api/v1/jobs`

Scroll zu dieser Sektion und expanded sie:

```
🔷 /api/v1/jobs
   ├─ 📨 POST /scrape
   ├─ 📨 POST /upload
   ├─ 📨 POST /batch-analyze              ← Startet Batch
   ├─ 🔄 GET  /batch-status                ← Polling-Alternative
   ├─ 🌊 GET  /batch-progress-stream       ← SSE LIVE (NEU!)
   ├─ 🛑 DELETE /batch-progress            ← Stop-Button (NEU!)
   ├─ 📊 GET  /reports/competence-trends
   └─ ...
```

---

## 1️⃣ **POST /batch-analyze** (Batch starten)

```
┌─────────────────────────────────────────┐
│ POST /api/v1/jobs/batch-analyze        │
├─────────────────────────────────────────┤
│ Summary: Batch-Analyse lokaler Dateien │
│                                         │
│ Description: Verarbeitet alle          │
│ Stellenanzeigen-Dateien aus dem        │
│ Python 'data/jobs' Ordner und          │
│ speichert die Ergebnisse in der        │
│ Datenbank.                             │
│                                         │
│ [Try it out]                           │
│   [Execute]                            │
└─────────────────────────────────────────┘
```

### Response (202 Accepted)
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
    "progress_bar": "░░░░░░░░░░",
    "startedAt": 1735385100000,
    "finishedAt": null
  }
}
```

---

## 2️⃣ **GET /batch-progress-stream** (SSE Live-Updates) ✨ NEU!

```
┌──────────────────────────────────────────────┐
│ GET /api/v1/jobs/batch-progress-stream      │
├──────────────────────────────────────────────┤
│ Summary: Batch-Progress Streaming (SSE)    │
│                                              │
│ Description: Abonniert den                 │
│ Live-Fortschritt der                       │
│ Batch-Verarbeitung als                     │
│ Server-Sent Events (keine Polling nötig,   │
│ Browser bleibt flüssig).                   │
│                                              │
│ Produces: text/event-stream                │
│                                              │
│ [Try it out]                               │
│   [Execute]                                │
└──────────────────────────────────────────────┘
```

### Response (Streaming Events)
```
event: progress
id: 3
data: {"total":28,"processed":3,"percentage":10,"status":"running","current_file":"Job Posting #3 - Software Engineer","estimated_seconds_remaining":180,"failed_count":0,"skipped_count":1,"progress_bar":"█░░░░░░░░░"}

event: progress
id: 7
data: {"total":28,"processed":7,"percentage":25,"status":"running","current_file":"Job Posting #7 - Product Manager","estimated_seconds_remaining":126,"failed_count":0,"skipped_count":2,"progress_bar":"██░░░░░░░░"}

...

event: completed
id: done
data: {"total":28,"processed":28,"percentage":100,"status":"completed","current_file":"","estimated_seconds_remaining":0,"failed_count":1,"skipped_count":3,"progress_bar":"██████████","finishedAt":1735385400123}
```

**Was ist SSE?**
- Server-Sent Events
- Browser öffnet Verbindung: `new EventSource('/batch-progress-stream')`
- Server pushed Updates automatisch
- Kein Polling nötig (effizient!)
- Browser bleibt immer responsiv

---

## 3️⃣ **DELETE /batch-progress** (Stop-Button) ✨ NEU!

```
┌──────────────────────────────────────────┐
│ DELETE /api/v1/jobs/batch-progress      │
├──────────────────────────────────────────┤
│ Summary: Batch-Verarbeitung stoppen     │
│                                          │
│ Description: Sendet Stop-Signal an      │
│ laufende Batch-Verarbeitung. Browser-   │
│ Freeze wird vermieden durch             │
│ asynchrone Verarbeitung.                │
│                                          │
│ [Try it out]                            │
│   [Execute]                             │
└──────────────────────────────────────────┘
```

### Response (200 OK)
```json
{
  "status": "cancelled",
  "message": "Batch-Verarbeitung wurde gestoppt",
  "processed": 15,
  "total": 28
}
```

### Response (400 Bad Request - Keine Batch aktiv)
```json
{
  "error": "Keine laufende Batch-Verarbeitung (Status: idle)"
}
```

---

## 4️⃣ **GET /batch-status** (Status abrufen)

```
┌──────────────────────────┐
│ GET /batch-status        │
├──────────────────────────┤
│ Summary: Batch-Status    │
│                          │
│ Description: Abrufen der │
│ aktuellen Fortschritts-  │
│ informationen            │
│                          │
│ [Try it out]             │
│   [Execute]              │
└──────────────────────────┘
```

### Response (200 OK)
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

## 🎬 Test-Workflow in Swagger UI

### Schritt 1: Batch starten
```
1. Gehe zu: POST /batch-analyze
2. Klicke [Try it out]
3. Klicke [Execute]
4. ✅ Response: 202 Accepted
```

### Schritt 2: Status abrufen (Polling)
```
1. Gehe zu: GET /batch-status
2. Klicke [Try it out]
3. Klicke [Execute] mehrmals
4. Sehe: processed Count erhöht sich
```

ODER

### Schritt 2 (Better): SSE abonnieren
```
1. Gehe zu: GET /batch-progress-stream
2. Klicke [Try it out]
3. Klicke [Execute]
4. Stream öffnet sich
5. Sehe: Live Updates alle 500ms
6. Schließe Stream um zu stoppen
```

### Schritt 3: Batch stoppen (optional)
```
1. Gehe zu: DELETE /batch-progress
2. Klicke [Try it out]
3. Klicke [Execute]
4. ✅ Response: {"status": "cancelled", ...}
5. SSE-Stream endet
```

---

## 📊 Response Model Reference

### `BatchProgress` Schema

| Feld | Typ | Beispiel | Beschreibung |
|------|-----|---------|-------------|
| `total` | int | 28 | Gesamtzahl Dateien |
| `processed` | int | 15 | Bisher verarbeitet |
| `percentage` | int | 53 | Prozent (0-100) |
| `status` | string | "running" | idle \| running \| completed \| cancelled |
| `current_file` | string | "Job #15 - Engineer" | Aktuelle Datei |
| `estimated_seconds_remaining` | long | 63 | Sekunden bis fertig |
| `failed_count` | int | 1 | Fehlerhafte Dateien |
| `skipped_count` | int | 2 | Übersprungene (duplikat) |
| `progress_bar` | string | "█████░░░░░" | Visuelle Anzeige |
| `startedAt` | long | 1735385100000 | Timestamp Start |
| `finishedAt` | long | 1735385400000 | Timestamp Ende |

---

## 🖥️ Swagger UI Layout

```
    ┌─────────────────────────────────────┐
    │ Swagger UI                          │
    ├─────────────────────────────────────┤
    │ Servers: http://localhost:8080      │
    │                                     │
    │ 🔍 Search endpoints...              │
    │                                     │
    │ 📂 /api/v1/jobs                     │
    │   ├─ ▼ POST /scrape                │
    │   ├─ ▼ POST /upload                │
    │   ├─ ▼ POST /batch-analyze    ← 1  │
    │   ├─ ▼ GET  /batch-status     ← 4  │
    │   ├─ ▼ GET  /batch-progress-stream  │ ← 2 (SSE)
    │   ├─ ▼ DELETE /batch-progress ← 3  │
    │   ├─ ▼ GET  /reports/...           │
    │   └─ ▼ GET  /getAllJobs            │
    │                                     │
    └─────────────────────────────────────┘
```

---

## 🔐 Beispiel: Browser-DevTools

```javascript
// DevTools Console > Network Tab > WS (WebSocket) / Event Stream

// Option 1: EventSource API
const eventSource = new EventSource('http://localhost:8080/api/v1/jobs/batch-progress-stream');

eventSource.addEventListener('progress', (e) => {
    console.log('Progress:', JSON.parse(e.data));
    // {
    //   "total": 28,
    //   "processed": 7,
    //   "percentage": 25,
    //   "current_file": "Job #7",
    //   "estimated_seconds_remaining": 126,
    //   ...
    // }
});

eventSource.addEventListener('completed', (e) => {
    console.log('✅ Done!');
    eventSource.close();
});

eventSource.onerror = () => {
    console.error('❌ Stream Error');
    eventSource.close();
};
```

---

## ⚡ Performance Notes

| Aspekt | Polling | SSE |
|--------|---------|-----|
| **Requests** | 120/Minute (500ms interval) | 1-2 (initial + complete) |
| **Latenz** | 0-500ms | 0-500ms |
| **Browser Load** | Höher (viele Requests) | Niedrig (Push-based) |
| **Real-time** | Gut | Besser |
| **Unterbrechungen** | Anfällig | Robust |

**SSE = Better für lange Prozesse wie Batch-Processing!**

---

## 🐛 Debugging Tips

### 1. Prüfe ob Batch läuft
```bash
curl -s http://localhost:8080/api/v1/jobs/batch-status | jq .status
# Erwartet: "running" oder "completed" oder "idle"
```

### 2. SSE-Stream in Terminal
```bash
curl -N http://localhost:8080/api/v1/jobs/batch-progress-stream
# Live-Events anschauen
```

### 3. Logs prüfen
```bash
docker logs -f kotlin-api | grep "BATCH\|Progress\|Cancelled"
```

### 4. Browser Network-Tab
- Tab öffnen: F12 > Network
- Filter: "batch"
- Click auf `/batch-progress-stream`
- Sehe: Type = "fetch", Messages = Events

---

## ✅ Checkliste für Testing

- [ ] POST /batch-analyze gibt 202 zurück
- [ ] Response enthält initial progress
- [ ] GET /batch-status aktualisiert processed count
- [ ] GET /batch-progress-stream streamed Events
- [ ] Events kommen ca. alle 500ms
- [ ] DELETE /batch-progress setzt status=cancelled
- [ ] Stream endet nach completion
- [ ] Fehler-Dateien werden getracked
- [ ] ETA nimmt ab über Zeit
- [ ] currentFile wird aktualisiert

---

## 📚 Weitere Docs

- [BATCH_PROGRESS_GUIDE.md](./BATCH_PROGRESS_GUIDE.md) - Detaillierte Technik
- [BATCH_SWAGGER_SUMMARY.md](./BATCH_SWAGGER_SUMMARY.md) - API-Referenz
- [batch-progress-demo.html](../kotlin-api/batch-progress-demo.html) - Live-Demo HTML

---

**🎉 Fertig! Batch-Progress ist jetzt in Swagger dokumentiert und einsatzbereit.**
