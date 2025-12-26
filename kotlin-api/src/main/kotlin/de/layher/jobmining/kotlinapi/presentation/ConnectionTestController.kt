package de.layher.jobmining.kotlinapi.presentation

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.client.RestTemplate

@RestController
class ConnectionTestController(private val restTemplate: RestTemplate) {

    @GetMapping("/test-python")
    fun testPython(): String {
        return try {
            // Testet, ob die Python-API (lokal gestartet) antwortet
            val response = restTemplate.getForObject("http://localhost:8000/health/status", String::class.java)
            "Python erreichbar: $response"
        } catch (e: Exception) {
            "Python NICHT erreichbar: ${e.message}"
        }
    }
}
