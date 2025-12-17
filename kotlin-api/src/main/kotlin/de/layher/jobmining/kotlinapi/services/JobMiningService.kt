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

        // Konvertierung zu einem Set VOR der JobPosting-Erstellung
        val competenceSet = competences.toMutableSet()

        // 🚨 FINALER FIX: Das fehlerhafte Argument wurde entfernt und das Komma nach industry gelöscht.
        val jobPosting = JobPosting(
            title = resultDto.title,
            jobRole = resultDto.jobRole,
            rawTextHash = resultDto.rawTextHash,
            rawText = resultDto.rawText,
            postingDate = LocalDate.parse(resultDto.postingDate),
            region = resultDto.region,
            industry = resultDto.industry,
            isSegmented = resultDto.is_segmented
        )

        // Setzen der Kompetenzen auf das erstellte Objekt
        jobPosting.competences = competenceSet

        // WICHTIGER FIX: Setze die bidirektionale Gegenreferenz (Competence -> JobPosting)
        jobPosting.competences.forEach { competence ->
            competence.jobPosting = jobPosting
        }


        return repository.save(jobPosting)
    }

    /**
     * Führt den Scraper-Workflow aus (Web-URL).
     */
    @Transactional
    fun processScrapedUrl(url: String, renderJs: Boolean): JobPosting {

        // 1. Aufruf des Python-Scraper-Microservice
        val resultDto = pythonClient.scrapeAndAnalyzeUrl(url, renderJs)

        // --- IDEMPOTENZ-PRÜFUNG ---
        val existingJob = repository.findByRawTextHash(resultDto.rawTextHash).firstOrNull()

        if (existingJob != null) {
            println("--- 🛡️ IDEMPOTENZ (URL): Stellenanzeige bereits vorhanden. Rückgabe des bestehenden Eintrags (ID: ${existingJob.id}).")
            return existingJob
        }
        // -----------------------------

        // 2. Mapping und Speicherung
        val competences = resultDto.competences.map { dto ->
            Competence(
                originalTerm = dto.originalTerm,
                escoLabel = dto.escoLabel,
                escoUri = dto.escoUri,
                confidenceScore = dto.confidenceScore,
                escoGroupCode = dto.escoGroupCode
            )
        }

        // Konvertierung zu einem Set VOR der JobPosting-Erstellung
        val competenceSet = competences.toMutableSet()

        val jobPosting = JobPosting(
            title = resultDto.title,
            jobRole = resultDto.jobRole,
            rawTextHash = resultDto.rawTextHash,
            rawText = resultDto.rawText,
            postingDate = LocalDate.parse(resultDto.postingDate),
            region = resultDto.region,
            industry = resultDto.industry,
            isSegmented = resultDto.is_segmented
        )

        // Setzen der Kompetenzen auf das erstellte Objekt
        jobPosting.competences = competenceSet

        // WICHTIGER FIX: Setze die bidirektionale Gegenreferenz (Competence -> JobPosting)
        jobPosting.competences.forEach { competence ->
            competence.jobPosting = jobPosting
        }

        return repository.save(jobPosting)
    }

    /**
     * Löscht alle gespeicherten JobPostings.
     */
    @Transactional
    fun deleteAllPostings(): Long {
        val count = repository.count()
        repository.deleteAll()
        println("--- ⚠️ ADMIN: Datenbank bereinigt. $count Einträge gelöscht.")
        return count
    }

    /**
     * Batch-Analyse aller lokalen Dateien mit Idempotenz-Prüfung.
     */
    @Transactional
    fun processJobDirectoryBatch(): List<JobPosting> {
        val resultsDto = pythonClient.processLocalJobDirectory()
        val jobPostingsToSave = mutableListOf<JobPosting>()

        // 🛡️ Set zur Verfolgung von Hashes innerhalb DIESES Batch-Laufs
        val seenHashesInBatch = mutableSetOf<String>()
        var countIgnored = 0

        resultsDto.forEach { resultDto ->
            val hash = resultDto.rawTextHash

            // 1. Check gegen DB UND 2. Check gegen aktuelle Batch-Liste
            if (repository.findByRawTextHash(hash).firstOrNull() == null && !seenHashesInBatch.contains(hash)) {

                seenHashesInBatch.add(hash) // Hash registrieren

                val competences = resultDto.competences.map { dto ->
                    Competence(
                        originalTerm = dto.originalTerm,
                        escoLabel = dto.escoLabel,
                        escoUri = dto.escoUri,
                        confidenceScore = dto.confidenceScore,
                        escoGroupCode = dto.escoGroupCode
                    )
                }.toMutableSet()

                val jobPosting = JobPosting(
                    title = resultDto.title.take(1000),
                    jobRole = resultDto.jobRole,
                    rawTextHash = resultDto.rawTextHash,
                    rawText = resultDto.rawText,
                    postingDate = LocalDate.parse(resultDto.postingDate),
                    region = resultDto.region,
                    industry = resultDto.industry.take(500),
                    isSegmented = resultDto.is_segmented
                )

                jobPosting.competences = competences
                jobPosting.competences.forEach { it.jobPosting = jobPosting }
                jobPostingsToSave.add(jobPosting)
            } else {
                countIgnored++
            }
        }

        println("--- 🛡️ BATCH: $countIgnored Einträge ignoriert. ${jobPostingsToSave.size} neue Einträge werden gespeichert.")
        return repository.saveAll(jobPostingsToSave)
    }
    // In JobMiningService.kt hinzufügen
    @Transactional(readOnly = true)
    fun getAllStoredJobs(): List<JobPosting> {
        return repository.findAll()
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
