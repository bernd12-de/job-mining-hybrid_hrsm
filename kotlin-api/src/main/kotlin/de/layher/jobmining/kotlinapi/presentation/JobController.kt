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
@RestController
@RequestMapping("/api/v1/jobs")
class JobController(
    private val jobMiningService: JobMiningService
) {

    @Operation(
        summary = "Kompetenz-Trendbericht",
        description = "Gibt die Top N der am häufigsten in allen Stellenanzeigen gefundenen Kompetenzen zurück."
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


// Zukünftiger Endpunkt für Reports (Phase 3.2)
// @GetMapping("/reports/trends")
// fun getCompetenceTrends(): List<TrendReportDTO> { ... }
