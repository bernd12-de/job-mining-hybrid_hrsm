package de.layher.jobmining.kotlinapi.presentation

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.client.RestTemplate

@RestController
class ConnectionTestController(
    private val restTemplate: RestTemplate,
    @org.springframework.beans.factory.annotation.Value("\${python.api.base-url:http://localhost:8000}")
    private val pythonApiBaseUrl: String
) {

    @GetMapping(value = ["/test-python", "/api/v1/test-python"]) 
    fun testPython(): String {
        return try {
            // Nutze die konfigurierte Basis-URL und den korrekten Endpunkt
            val response = restTemplate.getForObject("${'$'}pythonApiBaseUrl/system/status", String::class.java)
            "Python erreichbar: $response"
        } catch (e: Exception) {
            "Python NICHT erreichbar: ${e.message}"
        }
    }
}
