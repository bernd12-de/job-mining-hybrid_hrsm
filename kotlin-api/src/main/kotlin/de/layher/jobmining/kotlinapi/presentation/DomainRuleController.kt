package de.layher.jobmining.kotlinapi.presentation

import de.layher.jobmining.kotlinapi.adapters.CompetenceDTO
import de.layher.jobmining.kotlinapi.services.DomainRuleService
import org.springframework.web.bind.annotation.*
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.http.ResponseEntity

@RestController
@RequestMapping("/api/v1/rules")
@Tag(name = "Regelverwaltung", description = "API für das Abrufen und Verwalten von Domänenregeln (Blacklist, Mappings).")
class DomainRuleController(
    private val domainRuleService: DomainRuleService
) {

    @Operation(
        summary = "Blacklist abrufen",
        description = "Gibt alle aktiven Blacklist-Schlüssel (generische Begriffe) als Liste zurück. Wird vom Python-Backend verwendet."
    )
    @GetMapping("/blacklist")
    fun getBlacklist(): ResponseEntity<List<String>> {
        val blacklist = domainRuleService.getActiveBlacklistKeys()
        return ResponseEntity.ok(blacklist)
    }

    @Operation(
        summary = "Rollen-Mappings abrufen",
        description = "Gibt aktive Mappings von Rolle (Key) zu Regex-Muster (Value) zurück. Wird vom Python-Backend verwendet."
    )
    @GetMapping("/role-mappings")
    fun getRoleMappings(): ResponseEntity<Map<String, String>> {
        val mappings = domainRuleService.getActiveRoleMappings()
        return ResponseEntity.ok(mappings)
    }

    @Operation( // <--- NEUER ENDPUNKT (KORRIGIERT)
        summary = "Branchen-Mappings abrufen",
        description = "Gibt aktive Mappings von Branche (Key) zu Regex-Muster (Value) zurück. Wird vom Python-Backend verwendet."
    )
    @GetMapping("/industry-mappings") // 🚨 KRITISCHER FIX: NUR der relative Pfad
    fun getIndustryMappings(): ResponseEntity<Map<String, String>> {
        // 🚨 KRITISCHER FIX: Korrekter Aufruf der existierenden Methode
        val mappings = domainRuleService.getActiveIndustryMappings()
        return ResponseEntity.ok(mappings)
    }

    @Operation(summary = "Vollständige ESCO-Wissensbasis abrufen")
    @GetMapping("/esco-full")
    fun getFullEscoKnowledgeBase(): ResponseEntity<List<CompetenceDTO>> {
        // Holt alle 31.655 Begriffe aus dem Service
        val allSkills = domainRuleService.getAllCompetences()
        return ResponseEntity.ok(allSkills)
    }


    // Zukünftige Endpunkte (z.B. POST /rules/blacklist zum Hinzufügen über Admin-UI)
    // ...
}
