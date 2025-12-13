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
     * Führt den Scraper-Workflow aus (Web-URL).
     * Enthält Idempotenz-Prüfung.
     * KORRIGIERT: Akzeptiert jetzt den renderJs Parameter.
     */
    @Transactional
    fun processScrapedUrl(url: String, renderJs: Boolean): JobPosting { // <--- KORRIGIERT

        // 1. Aufruf des Python-Scraper-Microservice
        val resultDto = pythonClient.scrapeAndAnalyzeUrl(url, renderJs) // <--- WICHTIG: ÜBERGIBT renderJs

        // --- IDEMPOTENZ-PRÜFUNG ---
        // Prüft, ob der Hash des extrahierten Texts (rawTextHash) bereits existiert.
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

        val jobPosting = JobPosting(
            title = resultDto.title, // Titel ist hier die URL
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
     * Löscht alle gespeicherten JobPostings (und kaskadierend alle Kompetenzen).
     * Administrative Funktion zur Bereinigung.
     */
    @Transactional
    fun deleteAllPostings(): Long {
        val count = repository.count()
        // KERN-FIX: Wechsle zu deleteAll() (beachtet JPA Kaskadierung)
        repository.deleteAll()
        println("--- ⚠️ ADMIN: Datenbank bereinigt. $count Einträge gelöscht.")
        return count
    }

    /**
     * Batch-Analyse aller lokalen Dateien mit Idempotenz-Prüfung.
     *
     *  // In JobMiningService.kt
     *     @Transactional
     *     fun processJobDirectoryBatch(): List<JobPosting> {
     *         return pythonClient.processLocalJobDirectory()
     *     }
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
