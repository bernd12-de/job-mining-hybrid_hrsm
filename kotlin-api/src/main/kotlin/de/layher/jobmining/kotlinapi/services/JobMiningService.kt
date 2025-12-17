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
            industry = resultDto.industry
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
            industry = resultDto.industry // KEIN KOMMA HIER!
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
        var countIgnored = 0

        resultsDto.forEach { resultDto ->
            // --- IDEMPOTENZ-PRÜFUNG FÜR BATCH ---
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

                // Konvertierung zu einem Set VOR der JobPosting-Erstellung
                val competenceSet = competences.toMutableSet()

                val jobPosting = JobPosting(
                    title = resultDto.title,
                    jobRole = resultDto.jobRole,
                    rawTextHash = resultDto.rawTextHash,
                    rawText = resultDto.rawText,
                    postingDate = LocalDate.parse(resultDto.postingDate),
                    region = resultDto.region,
                    industry = resultDto.industry // KEIN KOMMA HIER!
                )

                // Setzen der Kompetenzen auf das erstellte Objekt
                jobPosting.competences = competenceSet

                // WICHTIGER FIX: Setze die bidirektionale Gegenreferenz
                jobPosting.competences.forEach { competence ->
                    competence.jobPosting = jobPosting
                }

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
