package de.layher.jobmining.kotlinapi.presentation

import org.springframework.beans.factory.annotation.Value
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag

@RestController
@RequestMapping("/api/links")
@Tag(name = "Service Links", description = "Zugriff auf alle verfügbaren UIs und Dashboards")
class ServiceLinksController(
    @Value("\${server.port:8080}") private val serverPort: String
) {
    
    data class ServiceLink(
        val name: String,
        val description: String,
        val url: String,
        val category: String
    )
    
    data class ServiceLinksResponse(
        val services: List<ServiceLink>,
        val info: String
    )

    @GetMapping
    @Operation(
        summary = "Alle verfügbaren Service-Links",
        description = """
            Liefert URLs zu allen verfügbaren UIs und Dashboards:
            - Swagger UI (diese API-Dokumentation)
            - Streamlit Dashboard (Visualisierung & Reports)
            - Python FastAPI Docs (Backend-API)
            - Actuator Health (System-Status)
        """
    )
    fun getServiceLinks(): ServiceLinksResponse {
        val baseUrl = if (serverPort == "8080") "http://localhost" else "http://localhost:$serverPort"
        
        return ServiceLinksResponse(
            services = listOf(
                ServiceLink(
                    name = "Swagger UI",
                    description = "API-Dokumentation & Discovery-Review (Kandidaten freigeben/ablehnen)",
                    url = "$baseUrl:8080/swagger-ui/index.html",
                    category = "API Documentation"
                ),
                ServiceLink(
                    name = "Streamlit Dashboard",
                    description = "Visualisierung: Top Skills, Zeitreihen, Domain-Mix, CSV/PDF-Reports",
                    url = "http://localhost:8501",
                    category = "Dashboard"
                ),
                ServiceLink(
                    name = "Python FastAPI Docs",
                    description = "Python Backend API-Tests & Workflow-Management",
                    url = "http://localhost:8000/docs",
                    category = "API Documentation"
                ),
                ServiceLink(
                    name = "Actuator Health",
                    description = "System-Status: DB, Disk, Liveness, Readiness",
                    url = "$baseUrl:8080/actuator/health",
                    category = "Monitoring"
                ),
                ServiceLink(
                    name = "Discovery Candidates",
                    description = "Unbekannte Begriffe aus Job-Analysen (JSON-API)",
                    url = "$baseUrl:8080/api/discovery/candidates",
                    category = "Discovery"
                ),
                ServiceLink(
                    name = "Discovery Approved",
                    description = "Freigegebene Skill-Mappings (JSON-API)",
                    url = "$baseUrl:8080/api/discovery/approved",
                    category = "Discovery"
                ),
                ServiceLink(
                    name = "Discovery Ignore",
                    description = "Abgelehnte Begriffe (JSON-API)",
                    url = "$baseUrl:8080/api/discovery/ignore",
                    category = "Discovery"
                )
            ),
            info = "Alle Services laufen im lokalen Docker-Stack. Swagger UI bietet interaktive API-Tests."
        )
    }
}
