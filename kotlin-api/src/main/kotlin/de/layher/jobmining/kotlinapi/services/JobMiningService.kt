package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient
import de.layher.jobmining.kotlinapi.domain.Competence
import de.layher.jobmining.kotlinapi.domain.JobPosting
import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
import de.layher.jobmining.kotlinapi.presentation.CompetenceReportDTO
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDate

@Service
class JobMiningService(
    private val repository: JobPostingRepository,
    private val pythonClient: PythonAnalysisClient
) {
    /**
     * Einzeldokument-Workflow mit Idempotenz-Prüfung.
     */
    @Transactional
    fun processJobAd(fileContent: ByteArray, filename: String): JobPosting {

        val resultDto = pythonClient.sendDocumentForAnalysis(fileContent, filename)

        // --- IDEMPOTENZ-PRÜFUNG FÜR EINZELDOKUMENT ---
        // Nutzt firstOrNull() für den Fall, dass durch einen Fehler Duplikate existieren.
        val existingJob = repository.findByRawTextHash(resultDto.rawTextHash).firstOrNull()

        if (existingJob != null) {
            println("--- 🛡️ IDEMPOTENZ: Stellenanzeige bereits vorhanden. Rückgabe des bestehenden Eintrags (ID: ${existingJob.id}).")
            return existingJob
        }
        // ----------------------------------------------

        val competences = resultDto.competences.map { dto ->
            Competence(
                originalTerm = dto.originalTerm,
                escoLabel = dto.escoLabel,
                escoUri = dto.escoUri,
                confidenceScore = dto.confidenceScore,
                escoGroupCode = dto.escoGroupCode
            )
        }

        val jobPosting = JobPosting(
            title = resultDto.title,
            jobRole = resultDto.jobRole,
            rawTextHash = resultDto.rawTextHash,
            rawText = resultDto.rawText,
            postingDate = LocalDate.parse(resultDto.postingDate),
            region = resultDto.region,
            industry = resultDto.industry,
            competences = competences
        )

        return repository.save(jobPosting)
    }

    /**
     * Batch-Analyse aller lokalen Dateien mit Idempotenz-Prüfung.
     */
    @Transactional
    fun processJobDirectoryBatch(): List<JobPosting> {
        val resultsDto = pythonClient.processLocalJobDirectory()

        val jobPostingsToSave = mutableListOf<JobPosting>()
        var countIgnored = 0

        resultsDto.forEach { resultDto ->
            // --- IDEMPOTENZ-PRÜFUNG FÜR BATCH ---
            // Nutzt firstOrNull() für den robusten Check.
            if (repository.findByRawTextHash(resultDto.rawTextHash).firstOrNull() == null) {

                // Mapping nur für neue Einträge
                val competences = resultDto.competences.map { dto ->
                    Competence(
                        originalTerm = dto.originalTerm,
                        escoLabel = dto.escoLabel,
                        escoUri = dto.escoUri,
                        confidenceScore = dto.confidenceScore,
                        escoGroupCode = dto.escoGroupCode
                    )
                }

                val jobPosting = JobPosting(
                    title = resultDto.title,
                    jobRole = resultDto.jobRole,
                    rawTextHash = resultDto.rawTextHash,
                    rawText = resultDto.rawText,
                    postingDate = LocalDate.parse(resultDto.postingDate),
                    region = resultDto.region,
                    industry = resultDto.industry,
                    competences = competences
                )
                jobPostingsToSave.add(jobPosting)
            } else {
                countIgnored++
            }
        }

        println("--- 🛡️ BATCH: $countIgnored Einträge ignoriert (bereits vorhanden). ${jobPostingsToSave.size} neue Einträge gespeichert.")
        return repository.saveAll(jobPostingsToSave)
    }

    /**
     * Aggregiert die Top-N der am häufigsten in allen gespeicherten Stellenanzeigen
     */
    @Transactional(readOnly = true)
    fun getTopCompetenceTrends(limit: Int = 5): List<CompetenceReportDTO> {
        val results = repository.findTopCompetencesByCount(limit)
        return results.map { array ->
            CompetenceReportDTO(
                competenceLabel = array[0] as String,
                count = array[1] as Long
            )
        }
    }
}

//package de.layher.jobmining.kotlinapi.services
//
//// HINZUFÜGEN DES FEHLENDEN IMPORTS Rwport:
//import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient
//import de.layher.jobmining.kotlinapi.domain.Competence
//import de.layher.jobmining.kotlinapi.domain.JobPosting
//import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
//import de.layher.jobmining.kotlinapi.presentation.CompetenceReportDTO
////import org.springframework.data.jpa.repository.JpaRepository
////import org.springframework.stereotype.Repository
//import org.springframework.stereotype.Service
//import org.springframework.transaction.annotation.Transactional
//import java.time.LocalDate
//
//
//
//@Service
//class JobMiningService(
//    private val repository: JobPostingRepository,
//    private val pythonClient: PythonAnalysisClient // Service für den HTTP-Aufruf zum Python-Backend
//) {
//    /**
//     * Führt den End-to-End-Workflow aus:
//     * 1. Sendet das Dokument an das Python-Backend.
//     * 2. Empfängt das JSON-Analyseergebnis.
//     * 3. Speichert das Ergebnis in der Datenbank.
//     */
//    @Transactional
//    fun processJobAd(fileContent: ByteArray, filename: String): JobPosting {
//
//        // 1. Aufruf des Python-Analyse-Microservice
//        val resultDto = pythonClient.sendDocumentForAnalysis(fileContent, filename)
//
//        // NEUE IDEMPOTENZ-PRÜFUNG:
//        val existingJob = repository.findByRawTextHash(resultDto.rawTextHash)
//
//        if (existingJob != null) {
//            println("--- 🛡️ IDEMPOTENZ: Stellenanzeige bereits vorhanden. Rückgabe des bestehenden Eintrags (ID: ${existingJob.id}).")
//            return existingJob // Gebe den bereits gespeicherten Eintrag zurück
//        }
//
//        // 2. Mapping von DTO zu Domain-Entitäten
//        // Die Kompetenzen müssen zuerst gemappt werden
//        val competences = resultDto.competences.map { dto ->
//            Competence(
//                originalTerm = dto.originalTerm,
//                escoLabel = dto.escoLabel,
//                escoUri = dto.escoUri,
//                confidenceScore = dto.confidenceScore,
//                escoGroupCode = dto.escoGroupCode // Berücksichtigt die hierarchische Anreicherung
//            )
//        }
//
//        // 3. Erstellung der Hauptentität JobPosting
//        val jobPosting = JobPosting(
//            title = resultDto.title,
//            jobRole = resultDto.jobRole,
//            rawTextHash = resultDto.rawTextHash,
//            rawText = resultDto.rawText, // <--- NEUES MAPPING
//            postingDate = LocalDate.parse(resultDto.postingDate), // Parst den ISO-String (z.B. "2024-12-01")
//            region = resultDto.region,
//            industry = resultDto.industry,
//            competences = competences // Liste der gemappten Kompetenzen
//        )
//
//        // 4. Speicherung in der PostgreSQL-Datenbank
//        return repository.save(jobPosting)
//    }
//
//    @Transactional
//    fun processJobDirectoryBatch(): List<JobPosting> {
//        // 1. Auslösen der Analyse im Python-Backend
//        val resultsDto = pythonClient.processLocalJobDirectory()
//
//
//
//        // 2. Mapping und Speicherung jedes DTOs
//        val jobPostingsToSave = resultsDto.map { resultDto ->
//            // Hier nutzen wir die gleiche Mapping-Logik wie in processJobAd
//            val competences = resultDto.competences.map { dto ->
//                Competence(
//                    originalTerm = dto.originalTerm,
//                    escoLabel = dto.escoLabel,
//                    escoUri = dto.escoUri,
//                    confidenceScore = dto.confidenceScore,
//                    escoGroupCode = dto.escoGroupCode
//                )
//            }
//
//            JobPosting(
//                title = resultDto.title,
//                jobRole = resultDto.jobRole,
//                rawTextHash = resultDto.rawTextHash,
//                rawText = resultDto.rawText,
//                postingDate = LocalDate.parse(resultDto.postingDate),
//                region = resultDto.region,
//                industry = resultDto.industry,
//                competences = competences
//            )
//        }
//
//        // 3. Batch-Speicherung aller Entitäten in einer Transaktion
//        return repository.saveAll(jobPostingsToSave)
//    }
//
//    /**
//     * Aggregiert die Top-N der am häufigsten in allen gespeicherten Stellenanzeigen
//     * gefundenen Kompetenzen.
//     */
//    @Transactional(readOnly = true)
//    fun getTopCompetenceTrends(limit: Int = 5): List<CompetenceReportDTO> {
//
//        // Direkter Aufruf der Repository-Methode zur Aggregation
//        val results = repository.findTopCompetencesByCount(limit)
//
//        // Mapping des Ergebnis-Typs auf das saubere DTO
//        return results.map { array ->
//            CompetenceReportDTO(
//                competenceLabel = array[0] as String, // Das ist das ESCO-Label
//                count = array[1] as Long             // Das ist der Count
//            )
//        }
//    }
//}
//
