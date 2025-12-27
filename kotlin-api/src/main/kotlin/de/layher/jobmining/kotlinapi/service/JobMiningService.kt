package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.adapters.PythonAnalysisClient
import de.layher.jobmining.kotlinapi.adapters.CompetenceDTO
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
     * Zentrales Mapping: Transformiert ein DTO von Python in eine JPA-Entität.
     * Nutzt die exakten Variablennamen aus deinem Modell.
     */
    private fun mapDtoToEntity(dto: CompetenceDTO, jobPosting: JobPosting): Competence {
        return Competence(
            originalTerm = dto.originalTerm,
            escoLabel = dto.escoLabel,
            escoUri = dto.escoUri,
            confidenceScore = dto.confidenceScore,
            escoGroupCode = dto.escoGroupCode,
            isDigital = dto.isDigital,       // Ebene 3
            isDiscovery = dto.isDiscovery,   // Ebene 1
            level = dto.level,               // Ebene 2, 4 oder 5
            roleContext = dto.roleContext,   // Ebene 6
            sourceDomain = dto.sourceDomain   // Ebene 4/5
        ).apply { this.jobPosting = jobPosting }
    }

    /**
     * Einzel-Workflow: PDF/DOCX-Analyse mit Status-Meldungen.
     */
    @Transactional
    fun processJobAd(fileContent: ByteArray, filename: String): JobPosting {
        println("--- 🚀 STARTE ANALYSE: Datei '$filename' wird an Python gesendet...")
        val resultDto = pythonClient.sendDocumentForAnalysis(fileContent, filename)

        // Idempotenz-Check (Ebene 7)
        val existingJob = repository.findByRawTextHash(resultDto.rawTextHash).firstOrNull()
        if (existingJob != null) {
            println("--- 🛡️ IDEMPOTENZ: Job bereits bekannt (Hash: ${resultDto.rawTextHash.take(8)}...). Überspringe Speicherung.")
            return existingJob
        }

        val jobPosting = JobPosting(
            title = resultDto.title,
            jobRole = resultDto.jobRole,
            rawTextHash = resultDto.rawTextHash,
            rawText = resultDto.rawText,
            postingDate = LocalDate.parse(resultDto.postingDate),
            region = resultDto.region,
            industry = resultDto.industry.take(500),
            isSegmented = resultDto.is_segmented // Ebene 6 Status
        )

        jobPosting.competences = resultDto.competences.map { dto ->
            mapDtoToEntity(dto, jobPosting)
        }.toMutableSet()

        val saved = repository.save(jobPosting)
        println("--- ✅ ERFOLG: Job '${saved.title}' mit ${saved.competences.size} Kompetenzen gespeichert (ID: ${saved.id}).")
        return saved
    }

    /**
     * Scraper-Workflow: Web-URL Analyse mit Feedback.
     */
    @Transactional
    fun processScrapedUrl(url: String, renderJs: Boolean): JobPosting {
        println("--- 🌐 SCRAPING: Analysiere URL: $url (JS-Rendering: $renderJs)")
        val resultDto = pythonClient.scrapeAndAnalyzeUrl(url, renderJs)

        val existingJob = repository.findByRawTextHash(resultDto.rawTextHash).firstOrNull()
        if (existingJob != null) {
            println("--- 🛡️ IDEMPOTENZ: Web-Anzeige bereits vorhanden.")
            return existingJob
        }

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

        jobPosting.competences = resultDto.competences.map { dto ->
            mapDtoToEntity(dto, jobPosting)
        }.toMutableSet()

        val saved = repository.save(jobPosting)
        println("--- ✅ ERFOLG: Web-Anzeige '${saved.title}' erfolgreich indexiert.")
        return saved
    }

    /**
     * Batch-Analyse: Verarbeitet alle lokalen Dateien für die Zeitreihenanalyse.
     */
    @Transactional
    fun processJobDirectoryBatch(): List<JobPosting> {
        println("--- 📂 BATCH-PROZESS: Starte Massenverarbeitung lokaler Dateien...")
        val resultsDto = pythonClient.processLocalJobDirectory()
        val jobPostingsToSave = mutableListOf<JobPosting>()
        val seenHashesInBatch = mutableSetOf<String>()
        var countIgnored = 0

        resultsDto.forEach { resultDto ->
            val hash = resultDto.rawTextHash

            if (repository.findByRawTextHash(hash).firstOrNull() == null && !seenHashesInBatch.contains(hash)) {
                seenHashesInBatch.add(hash)

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

                jobPosting.competences = resultDto.competences.map { dto ->
                    mapDtoToEntity(dto, jobPosting)
                }.toMutableSet()

                jobPostingsToSave.add(jobPosting)
            } else {
                countIgnored++
            }
        }

        val finalSaved = repository.saveAll(jobPostingsToSave)
        println("--- 🛡️ BATCH-ABSCHLUSS: $countIgnored Duplikate ignoriert. ${finalSaved.size} neue Jobs erfolgreich in DB importiert.")
        return finalSaved
    }

    @Transactional
    fun deleteAllPostings(): Long {
        val count = repository.count()
        repository.deleteAll()
        println("--- ⚠️ ADMIN: Datenbank wurde komplett bereinigt ($count Einträge gelöscht).")
        return count
    }

    @Transactional(readOnly = true)
    fun getAllStoredJobs(): List<JobPosting> = repository.findAll()

    @Transactional(readOnly = true)
    fun getTopCompetenceTrends(limit: Int = 5): List<CompetenceReportDTO> {
        println("--- 📊 REPORTING: Berechne Top $limit Kompetenz-Trends...")
        val results = repository.findTopCompetencesByCount(limit)
        return results.map { array ->
            CompetenceReportDTO(
                competenceLabel = array[0] as String,
                count = array[1] as Long
            )
        }
    }
}
