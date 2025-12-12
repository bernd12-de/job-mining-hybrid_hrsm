package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient
import de.layher.jobmining.kotlinapi.domain.JobPosting
import de.layher.jobmining.kotlinapi.domain.Competence
import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDate

@Service
class JobMiningService(
    private val repository: JobPostingRepository,
    private val pythonClient: PythonAnalysisClient // Service für den HTTP-Aufruf zum Python-Backend
) {
    /**
     * Führt den End-to-End-Workflow aus:
     * 1. Sendet das Dokument an das Python-Backend.
     * 2. Empfängt das JSON-Analyseergebnis.
     * 3. Speichert das Ergebnis in der Datenbank.
     */
    @Transactional
    fun processJobAd(fileContent: ByteArray, filename: String): JobPosting {

        // 1. Aufruf des Python-Analyse-Microservice
        val resultDto = pythonClient.sendDocumentForAnalysis(fileContent, filename)

        // 2. Mapping von DTO zu Domain-Entitäten
        // Die Kompetenzen müssen zuerst gemappt werden
        val competences = resultDto.competences.map { dto ->
            Competence(
                originalTerm = dto.originalTerm,
                escoLabel = dto.escoLabel,
                escoUri = dto.escoUri,
                confidenceScore = dto.confidenceScore,
                escoGroupCode = dto.escoGroupCode // Berücksichtigt die hierarchische Anreicherung
            )
        }

        // 3. Erstellung der Hauptentität JobPosting
        val jobPosting = JobPosting(
            title = resultDto.title,
            jobRole = resultDto.jobRole,
            rawTextHash = resultDto.rawTextHash,
            rawText = resultDto.rawText, // <--- NEUES MAPPING
            postingDate = LocalDate.parse(resultDto.postingDate), // Parst den ISO-String (z.B. "2024-12-01")
            region = resultDto.region,
            industry = resultDto.industry,
            competences = competences // Liste der gemappten Kompetenzen
        )

        // 4. Speicherung in der PostgreSQL-Datenbank
        return repository.save(jobPosting)
    }
}
