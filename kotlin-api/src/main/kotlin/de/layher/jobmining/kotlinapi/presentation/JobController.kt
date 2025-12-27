package de.layher.jobmining.kotlinapi.presentation

import de.layher.jobmining.kotlinapi.services.JobMiningService
import de.layher.jobmining.kotlinapi.domain.JobPosting
import org.springframework.http.MediaType
import org.springframework.web.bind.annotation.*
import org.springframework.web.multipart.MultipartFile

// Swagger / OpenAPI
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.Parameter
import io.swagger.v3.oas.annotations.media.Schema
// Importieren Sie das neue DTO
import de.layher.jobmining.kotlinapi.presentation.CompetenceReportDTO
import org.springframework.http.ResponseEntity
import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient

// Modell für den URL-Input vom Frontend
data class URLRequest(val url: String)

@RestController
@RequestMapping("/api/v1/jobs")
class JobController(
    private val jobMiningService: JobMiningService,
    // 👇 HIER kommt der "Client" her. Das ist einfach deine Klasse aus 'adapters/'
    private val pythonClient: PythonAnalysisClient
) {

    @Operation(
        summary = "Web-Scraping und Analyse",
        description = "Nimmt eine Web-URL (z.B. von StepStone) entgegen, scrapt den Inhalt und speichert die Analyse. Kann JavaScript-Rendering verwenden (renderJs=true)."
    )
    @PostMapping("/scrape")
    fun scrapeUrlAndAnalyze(
        @RequestBody request: URLRequest,
        @RequestParam(required = false, defaultValue = "false") renderJs: Boolean
    ): ResponseEntity<*> {
        return try {
            if (request.url.isBlank()) {
                return ResponseEntity.badRequest().body(mapOf(
                    "error" to "Die URL darf nicht leer sein."
                ))
            }

            val result = jobMiningService.processScrapedUrl(request.url, renderJs)
            ResponseEntity.ok(result)
        } catch (e: IllegalArgumentException) {
            ResponseEntity.badRequest().body(mapOf(
                "error" to e.message
            ))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "Interner Fehler: ${e.message}"
            ))
        }
    }


    @Operation(
        summary = "Batch-Analyse lokaler Dateien",
        description = "Verarbeitet alle Stellenanzeigen-Dateien aus dem Python 'data/jobs' Ordner und speichert die Ergebnisse in der Datenbank."
    )
    @PostMapping("/batch-analyze")
    fun analyzeLocalDirectory(): ResponseEntity<*> {
        return try {
            val results = jobMiningService.processJobDirectoryBatch()
            ResponseEntity.ok(mapOf(
                "status" to "success",
                "processed" to results.size,
                "jobs" to results
            ))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "Batch-Verarbeitung fehlgeschlagen: ${e.message}"
            ))
        }
    }

    @Operation(
        summary = "ADMIN: Datenbank bereinigen",
        description = "Löscht ALLE gespeicherten Stellenanzeigen und zugehörigen Kompetenzen."
    )
    @DeleteMapping("/admin/clear-all-data")
    fun clearAllData(): Map<String, Any> {
        val count = jobMiningService.deleteAllPostings()
        return mapOf("status" to "OK", "message" to "Datenbank erfolgreich bereinigt.", "deleted_count" to count)
    }

    @Operation(
        summary = "Upload einer Stellenanzeige",
        description = "Nimmt eine PDF oder DOCX-Datei entgegen und startet den Analyse-Workflow."
    )
    @PostMapping(
        "/upload",
        consumes = [MediaType.MULTIPART_FORM_DATA_VALUE]
    )
    fun uploadAndAnalyzeJobAd(
        @Parameter(
            description = "PDF- oder DOCX-Stellenanzeige",
            required = true,
            schema = Schema(type = "string", format = "binary")
        )
        @RequestPart("file")
        file: MultipartFile
    ): ResponseEntity<*> {
        return try {
            if (file.isEmpty) {
                return ResponseEntity.badRequest().body(mapOf(
                    "error" to "Die Datei darf nicht leer sein."
                ))
            }

            val result = jobMiningService.processJobAd(
                file.bytes,
                file.originalFilename ?: "unbekannt"
            )
            ResponseEntity.ok(result)
        } catch (e: IllegalArgumentException) {
            ResponseEntity.badRequest().body(mapOf(
                "error" to e.message
            ))
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "Fehler bei der Dateiverarbeitung: ${e.message}"
            ))
        }
    }

    @GetMapping("/reports/competence-trends")
    fun getCompetenceTrends(
        @RequestParam(defaultValue = "5") limit: Int
    ): List<CompetenceReportDTO> {
        return jobMiningService.getTopCompetenceTrends(limit)
    }

    @GetMapping("/reports/dashboard-metrics")
    fun getDashboardMetrics(@RequestParam(defaultValue = "10") top_n: Int): ResponseEntity<*> {
        return try {
            val metrics = pythonClient.getDashboardMetrics(top_n)
            ResponseEntity.ok(metrics)
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Dashboard-Metriken konnten nicht geladen werden: ${e.message}"
            ))
        }
    }

    @GetMapping("/reports/export.csv")
    fun proxyCsvReport(): ResponseEntity<*> {
        return try {
            val bytes = pythonClient.downloadCsvReport()
                ?: return ResponseEntity.status(502).body(mapOf(
                    "error" to "CSV-Report konnte nicht vom Python-Backend geladen werden"
                ))

            ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=job_mining_data_report.csv")
                .contentType(MediaType.TEXT_PLAIN)
                .body(bytes)
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Fehler beim Laden des CSV-Reports: ${e.message}"
            ))
        }
    }

    @GetMapping("/reports/export.pdf")
    fun proxyPdfReport(): ResponseEntity<*> {
        return try {
            val bytes = pythonClient.downloadPdfReport()
                ?: return ResponseEntity.status(502).body(mapOf(
                    "error" to "PDF-Report konnte nicht vom Python-Backend geladen werden"
                ))

            ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=job_mining_report.pdf")
                .contentType(MediaType.APPLICATION_PDF)
                .body(bytes)
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Fehler beim Laden des PDF-Reports: ${e.message}"
            ))
        }
    }

    // In JobController.kt hinzufügen
    @Operation(
        summary = "Alle analysierten Stellenanzeigen abrufen",
        description = "Gibt eine Liste aller in der Datenbank gespeicherten Jobs inklusive der extrahierten Kompetenzen zurück."
    )
    @GetMapping
    fun getAllJobs(): ResponseEntity<List<JobPosting>> {
        val jobs = jobMiningService.getAllStoredJobs()
        return ResponseEntity.ok(jobs)
    }

    @PostMapping("/admin/sync-python-knowledge")
    fun syncPythonKnowledge(): ResponseEntity<*> {
        return try {
            val result = pythonClient.triggerKnowledgeRefresh()
            ResponseEntity.ok(mapOf(
                "status" to "success",
                "message" to result
            ))
        } catch (e: Exception) {
            ResponseEntity.status(502).body(mapOf(
                "error" to "Knowledge-Refresh fehlgeschlagen: ${e.message}"
            ))
        }
    }

    @Operation(summary = "ADMIN: System-Status prüfen")
    @GetMapping("/admin/system-health")
    fun checkSystemHealth(): ResponseEntity<*> {
        return try {
            val pythonStatus = pythonClient.checkHealth()

            val fullStatus = mapOf(
                "kotlin_backend" to "ONLINE",
                "database" to "CONNECTED",
                "python_worker" to pythonStatus
            )
            ResponseEntity.ok(fullStatus)
        } catch (e: Exception) {
            ResponseEntity.status(500).body(mapOf(
                "error" to "System-Health-Check fehlgeschlagen: ${e.message}",
                "kotlin_backend" to "ONLINE",
                "python_worker" to mapOf("status" to "ERROR", "message" to e.message)
            ))
        }
    }



}
