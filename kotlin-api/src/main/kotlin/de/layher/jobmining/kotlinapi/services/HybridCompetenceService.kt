package de.layher.jobmining.kotlinapi.services

import de.layher.jobmining.kotlinapi.infrastructure.EscoDataRepository
import de.layher.jobmining.kotlinapi.infrastructure.JobPostingRepository
import de.layher.jobmining.kotlinapi.infrastructure.bridge.PythonNlpBridge
import org.springframework.stereotype.Service

@Service
class HybridCompetenceService(
    private val pythonClient: PythonNlpBridge, // Ruft Python-Script/API auf
    private val escoRepo: EscoDataRepository,
    private val jobRepo: JobPostingRepository, // 🚨 FIX: Ersetzt 'DatabaseHandler'
    private val domainRuleService: DomainRuleService // 🚨 NEU: Für den Blacklist-Check
) {

    fun processJob(jobId: Long, jobText: String) {
        // A. Extraktion (Python liefert Roh-Labels)
        // 🚨 FIX: Die Bridge-Methode heißt meist 'analyze' oder 'extractCompetences'
        val rawLabels = pythonClient.analyze(jobText)

        // B. Mapping & Filterung in Kotlin (Sinn-Ebene)
        val enrichedSkills = rawLabels
            // 🚨 FIX: Nutzt den DB-gestützten Service statt einer statischen Liste
            .filterNot { domainRuleService.isBlacklisted(it) }
            // 🚨 FIX: Methode im Repo heißt 'getSkillByLabel'
            .mapNotNull { escoRepo.getSkillByLabel(it) }

        // C. Analyse
        val digitalCount = enrichedSkills.count { it.isDigital }
        val share = if (enrichedSkills.isNotEmpty()) {
            digitalCount.toDouble() / enrichedSkills.size
        } else 0.0

        // D. Speichern des Audits / Ergebnisses
        jobRepo.findById(jobId).ifPresent { job ->
            // Hier können Ergebnisse am Job-Objekt gespeichert werden
            jobRepo.save(job)
        }
    }
}
