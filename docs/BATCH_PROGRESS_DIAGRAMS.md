# 🎨 Batch-Progress Visuelle Übersicht

## Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser / Frontend                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  HTML UI (batch-progress-demo.html)                      │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │ Status: RUNNING ⚪                                │    │  │
│  │  │ Progress: 7 / 28 files (25%)                     │    │  │
│  │  │ ██░░░░░░░░                                       │    │  │
│  │  │ Current: Job #7 - Product Manager                │    │  │
│  │  │ ETA: 1 min 54 sec                                │    │  │
│  │  │ Errors: 0 | Skipped: 2                           │    │  │
│  │  │                                                   │    │  │
│  │  │ [▶ Start]  [⏹ Stop]                             │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                            │  │
│  │  JavaScript:                                              │  │
│  │  ├─ POST /batch-analyze (Start)                          │  │
│  │  ├─ GET /batch-progress-stream (SSE Connect)    ← LIVE   │  │
│  │  ├─ UPDATE UI (every 500ms from server)                  │  │
│  │  └─ DELETE /batch-progress (Stop)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↕ HTTP/SSE                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  │                       │
┌─────────────────▼────────────┐  ┌──────▼────────────────────────┐
│  1. POST /batch-analyze      │  │  2. GET /batch-progress-stream│
│  (202 Accepted)              │  │  (SSE - 500ms updates)        │
│                              │  │                               │
│  ┌──────────────────────┐    │  │  ┌──────────────────────────┐ │
│  │ {                    │    │  │  │ event: progress          │ │
│  │   "status":"running" │    │  │  │ id: 7                    │ │
│  │   "progress": {      │    │  │  │ data: {                  │ │
│  │     "processed": 0   │    │  │  │   "processed": 7,        │ │
│  │     "total": 28      │    │  │  │   "total": 28,           │ │
│  │     "percentage": 0  │    │  │  │   "percentage": 25,      │ │
│  │   }                  │    │  │  │   "current_file": "..." │ │
│  │ }                    │    │  │  │   "eta": 126,           │ │
│  └──────────────────────┘    │  │  │   ...                    │ │
│                              │  │  │ }                        │ │
│                              │  │  │                          │ │
│                              │  │  │ event: progress          │ │
│                              │  │  │ id: 15                   │ │
│                              │  │  │ data: {...}              │ │
│                              │  │  │                          │ │
│                              │  │  │ ...                      │ │
│                              │  │  │                          │ │
│                              │  │  │ event: completed         │ │
│                              │  │  │ id: done                 │ │
│                              │  │  │ data: {processed: 28...}│ │
│                              │  │  └──────────────────────────┘ │
└──────────────────────────────┘  └──────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  │                       │
        ┌─────────▼──────────┐   ┌────────▼──────────────┐
        │ 3. DELETE /batch   │   │ 4. GET /batch-status │
        │ (Stop-Button)      │   │ (Polling Alternative)│
        │                    │   │                      │
        │ 200 OK:            │   │ 200 OK:              │
        │ {                  │   │ {                    │
        │   "status":        │   │   "processed": 7,    │
        │   "cancelled",     │   │   "total": 28,       │
        │   "message": "..." │   │   "percentage": 25,  │
        │   "processed": 15  │   │   "current_file":... │
        │ }                  │   │   "eta": 126,        │
        │                    │   │   ...                │
        └────────────────────┘   └──────────────────────┘
                  │                       │
                  └───────────┬───────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Kotlin Spring Boot                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  JobController                                             │ │
│  │  ├─ POST /batch-analyze()                                 │ │
│  │  │   └─ Call: jobMiningService.processJobDirectoryBatchAsync()
│  │  │       (asynchron, returns 202)                         │ │
│  │  │                                                         │ │
│  │  ├─ GET /batch-progress-stream()                          │ │
│  │  │   └─ SSE Emitter                                       │ │
│  │  │       Poll every 500ms: batchProgress.snapshot()       │ │
│  │  │       IF changed: emitter.send(event)                  │ │
│  │  │                                                         │ │
│  │  ├─ DELETE /batch-progress()                              │ │
│  │  │   └─ batchProgress.cancel()  ← Sets Flag               │ │
│  │  │                                                         │ │
│  │  └─ GET /batch-status()                                   │ │
│  │      └─ Return: batchProgress.snapshot()                  │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↕                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  JobMiningService                                          │ │
│  │  @Async                                                    │ │
│  │  fun processJobDirectoryBatchAsync(progress) {            │ │
│  │      progress.start()                                      │ │
│  │                                                             │ │
│  │      resultsDto.forEach { file →                          │ │
│  │          // CANCELLATION CHECK ← User clicked Stop!       │ │
│  │          if (progress.isCancellationRequested()) return    │ │
│  │                                                             │ │
│  │          try {                                             │ │
│  │              // Process file                               │ │
│  │          } catch (e: Exception) {                          │ │
│  │              failedCount++  ← Track errors                 │ │
│  │          }                                                  │ │
│  │                                                             │ │
│  │          // UPDATE PROGRESS (with details!)                │ │
│  │          progress.update(                                  │ │
│  │              processed = processedCount,                   │ │
│  │              percentage = ...,                             │ │
│  │              currentFile = file.title,  ← NEW!             │ │
│  │              failedCount = ...,  ← NEW!                    │ │
│  │              skippedCount = ...   ← NEW!                   │ │
│  │          )                                                  │ │
│  │      }                                                      │ │
│  │                                                             │ │
│  │      progress.finish()                                     │ │
│  │  }                                                          │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            ↕                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  BatchProgressService                                      │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ @Service                                             │  │ │
│  │  │ class BatchProgressService {                         │  │ │
│  │  │                                                       │  │ │
│  │  │   private val ref =                                  │  │ │
│  │  │     AtomicReference(BatchProgress())                 │  │ │
│  │  │                                                       │  │ │
│  │  │   @Volatile                                          │  │ │
│  │  │   private var cancellationRequested = false          │  │ │
│  │  │                                                       │  │ │
│  │  │   fun update(                                        │  │ │
│  │  │     processed, percentage, bar,                      │  │ │
│  │  │     currentFile, ← NEW!                              │  │ │
│  │  │     failedCount,  ← NEW!                             │  │ │
│  │  │     skippedCount  ← NEW!                             │  │ │
│  │  │   ) {                                                │  │ │
│  │  │     // Calculate ETA automatically ← NEW!             │  │ │
│  │  │     val eta = if (processed > 0 && total > processed)│  │ │
│  │  │       (elapsed / processed) * (total - processed)     │  │ │
│  │  │     else 0                                           │  │ │
│  │  │                                                       │  │ │
│  │  │     ref.set(cur.copy(                               │  │ │
│  │  │       processed, percentage, bar,                    │  │ │
│  │  │       currentFile,                  ← NEW!           │  │ │
│  │  │       estimatedSecondsRemaining = eta, ← NEW!        │  │ │
│  │  │       failedCount,  ← NEW!                           │  │ │
│  │  │       skippedCount  ← NEW!                           │  │ │
│  │  │     ))                                               │  │ │
│  │  │   }                                                  │  │ │
│  │  │                                                       │  │ │
│  │  │   fun cancel() {                    ← NEW!            │  │ │
│  │  │     cancellationRequested = true                      │  │ │
│  │  │   }                                                  │  │ │
│  │  │                                                       │  │ │
│  │  │   fun isCancellationRequested() = cancellationRequested
│  │  │                                    ← NEW!             │  │ │
│  │  │ }                                                    │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request/Response Flow

```
TIMELINE: User startet Batch-Verarbeitung

t=0s
User: "Starten!"
   ↓
Frontend: POST /batch-analyze
   ↓
Backend: 202 Accepted
   ↓ (async background job starts)
Frontend: Instantly shows "Preparing stream..."
   ↓

t=0.1s
Frontend: GET /batch-progress-stream (WebSocket-like)
   ↓
Backend: SseEmitter opens (listening for changes)
   ↓
JobMiningService starts processing files async
   ↓

t=5s
JobMiningService processes file #3
   ├─ progress.update(processed=3, ...)
   └─ → BatchProgressService updates state
      
       SseEmitter detects change
       ↓
       Server: event: progress
               id: 3
               data: {"processed":3, "total":28, "percentage":10, ...}
       ↓
       Frontend receives immediately
       ↓
       Updates UI: "3/28 | 10% | ETA: 2min 30sec | Job #3"

t=10s
Frontend/User: "Hmm, let's continue..."
   (SSE keeps streaming every 500ms)

t=35s
Frontend/User: "Stop this! I need something else"
   ↓
User: [⏹ Stop Button]
   ↓
Frontend: DELETE /batch-progress
   ↓
Backend: batchProgress.cancel() ← Sets flag
   ↓
JobMiningService loop checks flag:
   if (progress.isCancellationRequested()) return@forEach
   ↓
   Batch stops gracefully after current file
   ↓
   (Already processed files remain in DB)

t=36s
Backend: status = "cancelled"
   ↓
SseEmitter:
   event: completed
   data: {"status":"cancelled", "processed":15, "total":28}
   ↓
Frontend: Closes SSE connection
   ↓
UI: "Cancelled after 15/28 files"
```

---

## Datenfluss: Progress-Update

```
JobMiningService.processJobDirectoryBatchAsync()
│
├─ File #1: Process
│  └─ progress.update(
│       processed=1, percentage=3,
│       currentFile="Job #1 - Engineer",
│       failedCount=0, skippedCount=0
│     )
│     └─ BatchProgressService updates ref
│        └─ SseEmitter polls every 500ms
│           └─ IF changed: emitter.send(data)
│
├─ File #2: Process
│  └─ progress.update(...) → emitter.send(...)
│
├─ File #3: Process
│  └─ progress.update(...) → emitter.send(...)
│
├─ File #4: FAILS (try-catch)
│  └─ failedCount++
│     └─ progress.update(..., failedCount=1) → emitter.send(...)
│
├─ File #5: Process
│  └─ progress.update(...) → emitter.send(...)
│
├─ File #6: Duplicate (skipped)
│  └─ skippedCount++
│     └─ progress.update(..., skippedCount=1) → emitter.send(...)
│
├─ ...
│
├─ CANCELLATION CHECK (after File #15)
│  └─ if (progress.isCancellationRequested()) return
│     └─ Loop exits early
│
└─ progress.finish()
   └─ status = "completed" / "cancelled"
      └─ emitter.send(final event)
         └─ Frontend closes SSE
```

---

## SSE vs. Polling Vergleich

```
POLLING (alt):                          SSE (neu):
═════════════════════════════════════════════════════════════

t=0s: POST /batch-analyze               t=0s: POST /batch-analyze
      ↓ 202 Accepted                         ↓ 202 Accepted

t=0.5s: GET /batch-status               t=0.1s: GET /batch-progress-stream
        ↓ 200 OK                              ↓ SSE connection open
        processed: 0                         
                                        t=0.5s: (Server detects change)
t=1s: GET /batch-status                        ↓ event: progress
      ↓ 200 OK                               └─ Frontend updates
      processed: 1                        
                                        t=1s: (Server detects change)
t=1.5s: GET /batch-status                      ↓ event: progress
        ↓ 200 OK                             └─ Frontend updates
        processed: 1 (no change)
                                        t=1.5s: (No change, no send)
t=2s: GET /batch-status
      ↓ 200 OK                          t=2s: (Server detects change)
      processed: 2                           ↓ event: progress
                                           └─ Frontend updates
t=2.5s: GET /batch-status
        ↓ 200 OK                       
        processed: 2                   
                                       
...every 500ms...                       ...only when changed...

For 60-second batch:
120 requests × 500ms = 60s
Network traffic: HIGH                   Network traffic: MINIMAL
Browser overhead: HIGH                  Browser overhead: MINIMAL
UI latency: 0-500ms                     UI latency: 0-500ms
Real-time feel: OK                      Real-time feel: BETTER ✓
User cancel: Must wait ~500ms           User cancel: Instant ✓
```

---

## State Machine

```
┌──────────────┐
│     IDLE     │  (initial state)
└──────┬───────┘
       │
       │ POST /batch-analyze
       ↓
┌──────────────────┐
│     RUNNING      │  (async processing)
├──────────────────┤
│ • process loop   │
│ • emit updates   │
│ • check cancel   │
└──────┬──────┬────┘
       │      │
       │      └────────────────────────┐
       │                               │
       │ (all files done)             │ DELETE /batch-progress
       │                             │ (user clicked Stop)
       ↓                             ↓
┌──────────────────┐      ┌──────────────────┐
│   COMPLETED      │      │   CANCELLED      │
└──────┬───────────┘      └──────┬───────────┘
       │                         │
       └────────────┬────────────┘
                    │
                    │ SSE sends final event
                    │ Frontend closes connection
                    ↓
            ┌──────────────────┐
            │   READY TO REST  │
            │ (next batch can  │
            │  start again)    │
            └──────────────────┘
```

---

## Event Stream Timeline

```
SSE Connection Timeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

t=0s   ← Browser opens: GET /batch-progress-stream
       ← Server: "OK, I'll stream to you"

t=0.5s ← Server sends Event #1:
         event: progress
         id: 3
         data: {"processed":3,"percentage":10,...}

t=1s   ← (No change in progress, server waits)

t=1.5s ← Server sends Event #2:
         event: progress
         id: 7
         data: {"processed":7,"percentage":25,...}

t=2s   ← (No change, server waits)

t=2.5s ← Server sends Event #3:
         event: progress
         id: 11
         data: {"processed":11,"percentage":39,...}

...every 500-1000ms when status changes...

t=120s ← Server sends Final Event:
         event: completed
         id: done
         data: {"processed":28,"percentage":100,"status":"completed",...}
         
       ← Browser receives: eventSource.close()
       
       ← Connection closed gracefully

Total:  1 connection (opened for ~120s)
        ~120-240 events (depending on processing)
        <<< 60,000ms of updates in ONE connection
        VS. 240+ separate HTTP requests in polling! ✓
```

---

**🎉 SSE = Server pushes updates zu Browser, statt Browser fragt ständig nach!**
