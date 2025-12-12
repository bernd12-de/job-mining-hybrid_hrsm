package de.layher.jobmining.kotlinapi.adapters

import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.ByteArrayResource
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Component
import org.springframework.util.LinkedMultiValueMap
import org.springframework.web.client.RestTemplate

// Importiert das DTO, das wir auch im Code haben

@Component
class PythonAnalysisClient(
    // Verwendung des Wertes aus application.properties (oder default: localhost:8000)
    @Value("\${python.api.base-url:http://localhost:8000}")
    private val pythonApiBaseUrl: String
) {

    private val restTemplate = RestTemplate()

    /**
     * Führt den Datei-Upload und den Analyse-Aufruf an das Python-Backend (/analyse) durch.
     */
    fun sendDocumentForAnalysis(bytes: ByteArray, filename: String): AnalysisResultDTO {

        // 1. Header vorbereiten
        val headers = HttpHeaders().apply {
            // Wichtig: Setze ContentType nur auf MULTIPART_FORM_DATA,
            // die Boundary wird von RestTemplate automatisch gesetzt.
            contentType = MediaType.MULTIPART_FORM_DATA
        }

        // 2. Multipart-Body bauen (Verwendet LinkedMultiValueMap, um reaktive Abhängigkeiten zu vermeiden)
        val body = LinkedMultiValueMap<String, Any>()

        // Datei als ByteArrayResource verpacken, um sie als "file" zu senden
        val fileResource = object : ByteArrayResource(bytes) {
            override fun getFilename(): String = filename
        }

        // "file" muss exakt zum @File(...)-Parameter im Python-Backend passen
        body.add("file", fileResource)

        // 3. Request-Entität erstellen
        val requestEntity = HttpEntity(body, headers)

        // 4. POST Request senden und JSON in unser DTO mappen
        val url = "$pythonApiBaseUrl/analyse"

        // Führt den Post-Request durch und mappt das Ergebnis
        val response = restTemplate.postForEntity(url, requestEntity, AnalysisResultDTO::class.java)

        return response.body
            ?: throw IllegalStateException("Analyse-Ergebnis vom Python-Service war leer.")
    }
}
