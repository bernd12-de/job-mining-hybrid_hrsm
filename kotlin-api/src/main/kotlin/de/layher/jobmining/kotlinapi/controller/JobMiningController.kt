package de.layher.jobmining.kotlinapi.controller

import de.layher.jobmining.kotlinapi.JobPosting
import de.layher.jobmining.kotlinapi.service.JobMiningService
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import org.springframework.web.multipart.MultipartFile

@RestController
@RequestMapping("/api/job-postings")
class JobMiningController(
    private val jobMiningService: JobMiningService
) {

    @PostMapping("/analyze", consumes = ["multipart/form-data"])
    fun analyzeJobAd(@RequestParam("file") file: MultipartFile): ResponseEntity<JobPosting> {
        return try {
            val jobPosting = jobMiningService.processJobAd(file)
            ResponseEntity.ok(jobPosting)
        } catch (e: Exception) {
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    @ExceptionHandler(Exception::class)
    fun handleException(e: Exception): ResponseEntity<Map<String, String>> {
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(mapOf("error" to (e.message ?: "Unknown error occurred")))
    }
}
