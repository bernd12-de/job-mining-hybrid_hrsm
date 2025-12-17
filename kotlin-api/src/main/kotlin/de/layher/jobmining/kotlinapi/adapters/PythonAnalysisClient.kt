package de.layher.jobmining.kotlinapi.adapters

import com.fasterxml.jackson.annotation.JsonProperty
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.ByteArrayResource
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.util.LinkedMultiValueMap
import org.springframework.web.client.RestTemplate
import org.springframework.core.ParameterizedTypeReference
import org.springframework.http.HttpMethod

// NEUE IMPORTS FÜR ROBUSTES FEHLERHANDLING
import org.springframework.web.client.HttpStatusCodeException
import org.springframework.web.client.ResourceAccessException

// Input-Modell für die URL (muss dem Python-Modell entsprechen)
data class URLInput(val url: String, @JsonProperty("render_js") val renderJs: Boolean = false)

@Component
class PythonAnalysisClient(
    @Value("\${python.api.base-url:http://localhost:8000}")
    private val pythonApiBaseUrl: String
) {

    private val restTemplate = RestTemplate()

    /**
     * Führt den Datei-Upload und den Analyse-Aufruf an das Python-Backend (/analyse) durch.
     * FIX: Korrekte Verwendung von HttpHeaders und ByteArrayResource.
     */
    fun sendDocumentForAnalysis(bytes: ByteArray, filename: String): AnalysisResultDTO {

        try {
            val headers = HttpHeaders().apply {
                contentType = MediaType.MULTIPART_FORM_DATA // Wichtig: Multipart
            }

            // Definiere die Datei als Resource
            val fileResource = object : ByteArrayResource(bytes) {
                override fun getFilename(): String = filename
            }

            // Erstelle den Body mit dem Dateiteil
            val body = LinkedMultiValueMap<String, Any>().apply {
                add("file", fileResource) // Name muss 'file' sein (wie in FastAPI erwartet)
            }

            val requestEntity = HttpEntity(body, headers)
            val url = "$pythonApiBaseUrl/analyse"

            val response = restTemplate.postForEntity(url, requestEntity, AnalysisResultDTO::class.java)

            return response.body
                ?: throw IllegalStateException("Analyse-Ergebnis vom Python-Service war leer.")
        } catch (e: HttpStatusCodeException) {
            val pythonErrorDetail = e.responseBodyAsString.substringAfter("{\"detail\":\"").substringBeforeLast("\"}")
            throw RuntimeException("Fehler bei Dateianalyse im Python-Backend (${e.statusCode.value()}): $pythonErrorDetail")
        } catch (e: ResourceAccessException) {
            throw RuntimeException("Verbindungsfehler zum Python-Backend: Ist der Service gestartet? Fehler: ${e.message}")
        }
    }

    // In de.layher.jobmining.kotlinapi.infrastructure.bridge.PythonNlpBridge
    fun analyze(text: String): List<String> {
        // Hier kommt dein REST-Call an Python (Port 8000) rein
        return emptyList()
    }

    /**
     * Löst die Batch-Analyse aller lokalen Dateien im Python-Backend aus.
     */
    fun processLocalJobDirectory(): List<AnalysisResultDTO> {
        val url = "$pythonApiBaseUrl/batch-process"
        val responseType = object : ParameterizedTypeReference<List<AnalysisResultDTO>>() {}

        try {
            val response = restTemplate.exchange(
                url,
                HttpMethod.POST, // Es ist ein POST
                HttpEntity.EMPTY, // WICHTIG: Senden KEINEN Body, sondern ein leeres Entity
                responseType
            )
            return response.body
                ?: throw IllegalStateException("Batch-Analyse-Ergebnis vom Python-Service war leer.")
        } catch (e: HttpStatusCodeException) {
            val pythonErrorDetail = e.responseBodyAsString.substringAfter("{\"detail\":\"").substringBeforeLast("\"}")
            throw RuntimeException("Batch-Fehler im Python-Backend (${e.statusCode.value()}): $pythonErrorDetail")
        } catch (e: ResourceAccessException) {
            throw RuntimeException("Verbindungsfehler zum Python-Backend: Ist der Service gestartet? Fehler: ${e.message}")
        }
    }

    /**
     * Ruft den Scraper-Endpunkt im Python-Backend auf, um eine URL zu analysieren.
     * NEU: Fängt HTTP-Fehler ab, um die Jackson-Deserialisierungs-Warnung zu vermeiden.
     */
    fun scrapeAndAnalyzeUrl(url: String, renderJs: Boolean = false): AnalysisResultDTO {
        val requestUrl = "$pythonApiBaseUrl/scrape-url"
        val requestBody = URLInput(url, renderJs)

        try {
            // Führt den POST Request durch und mappt das Ergebnis
            val response = restTemplate.postForEntity(
                requestUrl,
                requestBody,
                AnalysisResultDTO::class.java
            )

            return response.body
                ?: throw IllegalStateException("Scraping-Analyse-Ergebnis vom Python-Service war leer.")

        } catch (e: HttpStatusCodeException) {
            // --- FIX FÜR JACKSON-WARNING ---
            // Fängt 4xx/5xx (inkl. 501 Not Implemented) und wirft eine saubere RuntimeException.
            // Dies verhindert, dass Spring den Fehler-Body in das DTO mappen muss.
            val pythonErrorDetail = e.responseBodyAsString.substringAfter("{\"detail\":\"").substringBeforeLast("\"}")

            throw RuntimeException("Web-Scraping-Fehler (${e.statusCode.value()}): $pythonErrorDetail")

        } catch (e: ResourceAccessException) {
            throw RuntimeException("Verbindungsfehler zum Python-Backend: Ist der Service gestartet? Fehler: ${e.message}")
        }
    }
}
