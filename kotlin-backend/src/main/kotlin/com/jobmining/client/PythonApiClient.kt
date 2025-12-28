package com.jobmining.client

import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate
import org.springframework.web.client.postForObject
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import org.slf4j.LoggerFactory

/**
 * Kotlin Client zum Senden von Job-Daten an das Python FastAPI Backend
 *
 * Use Cases:
 * - Kotlin Spring Boot → Python FastAPI Integration
 * - Hybrid-Architektur: Kotlin für Business Logic, Python für ML/NLP
 * - Batch-Processing: Kotlin sammelt Daten, Python verarbeitet sie
 */
@Service
class PythonApiClient(
    private val restTemplate: RestTemplate = RestTemplate()
) {

    private val logger = LoggerFactory.getLogger(PythonApiClient::class.java)
    private var pythonApiUrl = "http://localhost:5000"  // Config über application.properties

    /**
     * Data Transfer Object für Job-Daten
     */
    data class JobInputDto(
        val title: String,
        val role: String,
        val description: String? = null,
        val city: String,
        val country: String = "DE",
        val latitude: Double? = null,
        val longitude: Double? = null,
        val postedAt: String,  // ISO 8601 Format: "2025-12-27T10:00:00"
        val skills: List<String> = emptyList(),
        val source: String = "kotlin_backend"
    )

    /**
     * Response vom Python API
     */
    data class IngestResponse(
        val status: String,
        val count: Int,
        val message: String
    )

    /**
     * Sendet Job-Daten an das Python API
     *
     * @param jobs Liste von Jobs zum Senden
     * @return Response vom API
     */
    fun sendJobs(jobs: List<JobInputDto>): IngestResponse {
        val url = "$pythonApiUrl/api/data/ingest"

        return try {
            logger.info("📤 Sending ${jobs.size} jobs to Python API: $url")

            val headers = HttpHeaders()
            headers.contentType = MediaType.APPLICATION_JSON

            val request = HttpEntity(jobs, headers)

            val response = restTemplate.postForObject<IngestResponse>(url, request)

            logger.info("✅ Successfully sent ${response?.count ?: 0} jobs")
            response ?: throw RuntimeException("Empty response from API")

        } catch (e: Exception) {
            logger.error("❌ Failed to send jobs to Python API: ${e.message}", e)
            throw RuntimeException("Failed to send jobs: ${e.message}", e)
        }
    }

    /**
     * Generiert Sample-Jobs für Testing
     *
     * @param count Anzahl der zu generierenden Jobs
     * @return Liste von Sample-Jobs
     */
    fun generateSampleJobs(count: Int = 10): List<JobInputDto> {
        val roles = listOf("Software Developer", "Data Scientist", "DevOps Engineer", "Project Manager", "UI/UX Designer")
        val cities = listOf(
            Triple("Berlin", 52.5200, 13.4050),
            Triple("München", 48.1351, 11.5820),
            Triple("Hamburg", 53.5511, 9.9937),
            Triple("Köln", 50.9375, 6.9603),
            Triple("Frankfurt", 50.1109, 8.6821)
        )

        val skillsByRole = mapOf(
            "Software Developer" to listOf("Python", "Java", "JavaScript", "Docker", "Kubernetes", "Git", "SQL"),
            "Data Scientist" to listOf("Python", "R", "Machine Learning", "TensorFlow", "Pandas", "SQL"),
            "DevOps Engineer" to listOf("Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "Linux", "CI/CD"),
            "Project Manager" to listOf("Agile", "Scrum", "Jira", "MS Project"),
            "UI/UX Designer" to listOf("Figma", "Adobe XD", "Sketch", "Prototyping")
        )

        val formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME

        return (1..count).map {
            val role = roles.random()
            val (city, lat, lon) = cities.random()
            val year = (2020..2025).random()
            val month = (1..12).random()
            val day = (1..28).random()
            val postedAt = LocalDateTime.of(year, month, day, 10, 0)

            JobInputDto(
                title = "$role (m/w/d) - $city",
                role = role,
                description = "Wir suchen einen $role für unser Team in $city.",
                city = city,
                country = "DE",
                latitude = lat,
                longitude = lon,
                postedAt = postedAt.format(formatter),
                skills = skillsByRole[role]?.shuffled()?.take((3..6).random()) ?: emptyList(),
                source = "kotlin_backend"
            )
        }
    }

    /**
     * Sendet einen einzelnen Job
     *
     * @param job Job-Daten
     * @return Response vom API
     */
    fun sendJob(job: JobInputDto): IngestResponse {
        return sendJobs(listOf(job))
    }

    /**
     * Prüft ob das Python API erreichbar ist
     *
     * @return true wenn erreichbar, sonst false
     */
    fun isApiAvailable(): Boolean {
        return try {
            val response = restTemplate.getForObject("$pythonApiUrl/", Map::class.java)
            logger.info("✅ Python API is available: ${response?.get("message")}")
            true
        } catch (e: Exception) {
            logger.warn("⚠️ Python API is not available: ${e.message}")
            false
        }
    }

    /**
     * Setzt die API-URL (für Testing oder verschiedene Umgebungen)
     *
     * @param url URL des Python API
     */
    fun setPythonApiUrl(url: String) {
        this.pythonApiUrl = url
        logger.info("🔧 Python API URL set to: $url")
    }
}


/**
 * Example Controller zum Testen des Clients
 */
// @RestController
// @RequestMapping("/api/integration")
// class IntegrationController(
//     private val pythonApiClient: PythonApiClient
// ) {
//
//     private val logger = LoggerFactory.getLogger(IntegrationController::class.java)
//
//     /**
//      * Test-Endpoint: Sendet Sample-Daten an Python API
//      *
//      * GET /api/integration/send-test-data?count=20
//      */
//     @GetMapping("/send-test-data")
//     fun sendTestData(@RequestParam(defaultValue = "10") count: Int): Map<String, Any> {
//         logger.info("🧪 Generating and sending $count test jobs to Python API...")
//
//         // 1. Generate sample jobs
//         val jobs = pythonApiClient.generateSampleJobs(count)
//
//         // 2. Send to Python API
//         val response = pythonApiClient.sendJobs(jobs)
//
//         return mapOf(
//             "generated" to count,
//             "sent" to response.count,
//             "status" to response.status,
//             "message" to response.message
//         )
//     }
//
//     /**
//      * Test-Endpoint: Prüft Python API Status
//      *
//      * GET /api/integration/check-api
//      */
//     @GetMapping("/check-api")
//     fun checkApi(): Map<String, Any> {
//         val available = pythonApiClient.isApiAvailable()
//         return mapOf(
//             "available" to available,
//             "message" to if (available) "Python API is reachable" else "Python API is not reachable"
//         )
//     }
// }


/**
 * Example: Standalone Usage (ohne Spring)
 */
fun main() {
    println("=" * 60)
    println("Kotlin → Python API Integration Test")
    println("=" * 60)

    val client = PythonApiClient()

    // 1. Check API availability
    println("\n1️⃣ Checking Python API...")
    val available = client.isApiAvailable()
    println("   Status: ${if (available) "✅ Available" else "❌ Not Available"}")

    if (!available) {
        println("\n⚠️ Python API is not running. Start it with:")
        println("   cd python-backend && python api_with_db.py")
        return
    }

    // 2. Generate sample jobs
    println("\n2️⃣ Generating 10 sample jobs...")
    val jobs = client.generateSampleJobs(10)
    jobs.take(2).forEach { job ->
        println("   - ${job.title} | ${job.city} | ${job.skills.joinToString(", ")}")
    }

    // 3. Send to Python API
    println("\n3️⃣ Sending jobs to Python API...")
    val response = client.sendJobs(jobs)
    println("   ✅ ${response.message}")
    println("   Status: ${response.status}")
    println("   Count: ${response.count}")

    println("\n" + "=" * 60)
    println("✅ Integration test completed successfully!")
    println("=" * 60)
}

operator fun String.times(n: Int) = repeat(n)
