package de.layher.jobmining.kotlinapi.service

import de.layher.jobmining.kotlinapi.JobPosting
import de.layher.jobmining.kotlinapi.domain.Competence
import de.layher.jobmining.kotlinapi.repository.JobPostingRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.multipart.MultipartFile
import java.time.LocalDate
import java.time.format.DateTimeFormatter

@Service
class JobMiningService(
    private val pythonApiClient: PythonApiClient,
    private val jobPostingRepository: JobPostingRepository
) {

    @Transactional
    fun processJobAd(file: MultipartFile): JobPosting {
        // 1. Call Python API for analysis
        val analysisResult = pythonApiClient.analyzeJobAd(file)

        // 2. Check if already processed (idempotency)
        val existingJobPosting = jobPostingRepository.findByRawTextHash(analysisResult.rawTextHash)
        if (existingJobPosting != null) {
            return existingJobPosting
        }

        // 3. Map DTOs to entities
        val competences = analysisResult.competences.map { dto ->
            Competence(
                originalTerm = dto.originalTerm,
                escoLabel = dto.escoLabel,
                escoUri = dto.escoUri,
                confidenceScore = dto.confidenceScore,
                escoGroupCode = dto.escoGroupCode
            )
        }

        // 4. Create and save JobPosting
        val jobPosting = JobPosting(
            title = analysisResult.title,
            jobRole = analysisResult.jobRole,
            rawTextHash = analysisResult.rawTextHash,
            postingDate = parseDate(analysisResult.postingDate),
            region = analysisResult.region,
            industry = analysisResult.industry,
            competences = competences
        )

        return jobPostingRepository.save(jobPosting)
    }

    private fun parseDate(dateString: String): LocalDate {
        return try {
            LocalDate.parse(dateString)
        } catch (e: Exception) {
            // Fallback if parsing fails
            LocalDate.now()
        }
    }
}
