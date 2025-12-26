package de.layher.jobmining.kotlinapi.service

import de.layher.jobmining.kotlinapi.dto.AnalysisResultDTO
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.Resource
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Service
import org.springframework.util.LinkedMultiValueMap
import org.springframework.util.MultiValueMap
import org.springframework.web.client.RestTemplate
import org.springframework.web.multipart.MultipartFile

@Service
class PythonApiClient(
    @Value("\${python.api.url}")
    private val pythonApiUrl: String
) {
    private val restTemplate = RestTemplate()

    fun analyzeJobAd(file: MultipartFile): AnalysisResultDTO {
        val headers = HttpHeaders()
        headers.contentType = MediaType.MULTIPART_FORM_DATA

        val body: MultiValueMap<String, Any> = LinkedMultiValueMap()
        body.add("file", object : org.springframework.core.io.ByteArrayResource(file.bytes) {
            override fun getFilename(): String {
                return file.originalFilename ?: "document"
            }
        })

        val requestEntity = HttpEntity(body, headers)

        val url = "$pythonApiUrl/analyse"

        return restTemplate.postForObject(url, requestEntity, AnalysisResultDTO::class.java)
            ?: throw RuntimeException("Failed to get response from Python API")
    }
}
