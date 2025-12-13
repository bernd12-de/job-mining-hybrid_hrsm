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

// Modell für den URL-Input vom Frontend
data class URLRequest(val url: String)

@RestController
@RequestMapping("/api/v1/jobs")
class JobController(
    private val jobMiningService: JobMiningService
) {

    @Operation(
        summary = "Web-Scraping und Analyse",
        description = "Nimmt eine Web-URL (z.B. von StepStone) entgegen, scrapt den Inhalt und speichert die Analyse. Kann JavaScript-Rendering verwenden (renderJs=true)."
    )
    @PostMapping("/scrape")
    fun scrapeUrlAndAnalyze(
        @RequestBody request: URLRequest,
        @RequestParam(required = false, defaultValue = "false") renderJs: Boolean
    ): JobPosting {
        if (request.url.isBlank()) {
            throw IllegalArgumentException("Die URL darf nicht leer sein.")
        }

        // KORREKTUR: Übergibt den fehlenden Parameter 'renderJs' an den Service
        return jobMiningService.processScrapedUrl(request.url, renderJs)
    }


    @Operation(
        summary = "Batch-Analyse lokaler Dateien",
        description = "Verarbeitet alle Stellenanzeigen-Dateien aus dem Python 'data/jobs' Ordner und speichert die Ergebnisse in der Datenbank."
    )
    @PostMapping("/batch-analyze")
    fun analyzeLocalDirectory(): List<JobPosting> {
        return jobMiningService.processJobDirectoryBatch()
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
    ): JobPosting {

        if (file.isEmpty) {
            throw IllegalArgumentException("Die Datei darf nicht leer sein.")
        }

        return jobMiningService.processJobAd(
            file.bytes,
            file.originalFilename ?: "unbekannt"
        )
    }

    @GetMapping("/reports/competence-trends")
    fun getCompetenceTrends(
        @RequestParam(defaultValue = "5") limit: Int
    ): List<CompetenceReportDTO> {
        return jobMiningService.getTopCompetenceTrends(limit)
    }
}
