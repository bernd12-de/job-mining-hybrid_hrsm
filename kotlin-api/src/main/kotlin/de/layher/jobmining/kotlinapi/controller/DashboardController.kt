package de.layher.jobmining.kotlinapi.controller

import de.layher.jobmining.kotlinapi.dto.*
import de.layher.jobmining.kotlinapi.service.TrendAnalysisService
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

/**
 * REST Controller für Dashboard und Zeitreihen-Analyse
 * Endpoints für Postersession (14. Januar 2025)
 */
@RestController
@RequestMapping("/api/dashboard")
@CrossOrigin(origins = ["*"])  // Für Frontend-Zugriff
class DashboardController(
    private val trendAnalysisService: TrendAnalysisService
) {
    private val logger = LoggerFactory.getLogger(DashboardController::class.java)

    // =========================================================
    // HAUPT-DASHBOARD
    // =========================================================

    /**
     * Komplettes Dashboard für einen Jahresbereich
     *
     * GET /api/dashboard?startYear=2015&endYear=2025
     */
    @GetMapping
    fun getDashboard(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int
    ): ResponseEntity<DashboardDTO> {
        logger.info("📊 Dashboard-Request für Jahre $startYear-$endYear")

        return try {
            val dashboard = trendAnalysisService.generateDashboard(startYear, endYear)
            ResponseEntity.ok(dashboard)
        } catch (e: Exception) {
            logger.error("❌ Fehler beim Dashboard-Generieren", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    // =========================================================
    // ZEITREIHEN-ANALYSE
    // =========================================================

    /**
     * Jährliche Trends
     *
     * GET /api/dashboard/yearly-trends?startYear=2015&endYear=2025
     */
    @GetMapping("/yearly-trends")
    fun getYearlyTrends(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int
    ): ResponseEntity<List<YearlyTrendDTO>> {
        logger.info("📈 Yearly-Trends-Request für Jahre $startYear-$endYear")

        return try {
            val trends = trendAnalysisService.analyzeYearlyTrends(startYear, endYear)
            ResponseEntity.ok(trends)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Yearly-Trends", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    /**
     * Top steigende Skills
     *
     * GET /api/dashboard/rising-skills?startYear=2015&endYear=2025&limit=10
     */
    @GetMapping("/rising-skills")
    fun getRisingSkills(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int,
        @RequestParam(defaultValue = "10") limit: Int
    ): ResponseEntity<List<SkillTrendDTO>> {
        logger.info("📈 Rising-Skills-Request ($startYear-$endYear, Limit: $limit)")

        return try {
            val skills = trendAnalysisService.findTopRisingSkills(startYear, endYear, limit)
            ResponseEntity.ok(skills)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Rising-Skills", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    /**
     * Top fallende Skills
     *
     * GET /api/dashboard/falling-skills?startYear=2015&endYear=2025&limit=10
     */
    @GetMapping("/falling-skills")
    fun getFallingSkills(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int,
        @RequestParam(defaultValue = "10") limit: Int
    ): ResponseEntity<List<SkillTrendDTO>> {
        logger.info("📉 Falling-Skills-Request ($startYear-$endYear, Limit: $limit)")

        return try {
            val skills = trendAnalysisService.findTopFallingSkills(startYear, endYear, limit)
            ResponseEntity.ok(skills)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Falling-Skills", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    // =========================================================
    // DIGITALISIERUNG
    // =========================================================

    /**
     * Digitalisierungsrate pro Jahr
     *
     * GET /api/dashboard/digitalization?startYear=2015&endYear=2025
     */
    @GetMapping("/digitalization")
    fun getDigitalizationTrend(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int
    ): ResponseEntity<List<DigitalizationRateDTO>> {
        logger.info("💻 Digitalization-Request für Jahre $startYear-$endYear")

        return try {
            val rates = trendAnalysisService.analyzeDigitalizationTrend(startYear, endYear)
            ResponseEntity.ok(rates)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Digitalization-Trend", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    // =========================================================
    // 7-EBENEN-MODELL
    // =========================================================

    /**
     * Level-Verteilung pro Jahr
     *
     * GET /api/dashboard/level-distribution?startYear=2015&endYear=2025
     */
    @GetMapping("/level-distribution")
    fun getLevelDistribution(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int
    ): ResponseEntity<List<LevelDistributionDTO>> {
        logger.info("🎯 Level-Distribution-Request für Jahre $startYear-$endYear")

        return try {
            val distribution = trendAnalysisService.analyzeLevelDistribution(startYear, endYear)
            ResponseEntity.ok(distribution)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Level-Distribution", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    // =========================================================
    // ROLLEN-STATISTIK
    // =========================================================

    /**
     * Statistik pro Rollen-Kontext
     *
     * GET /api/dashboard/roles
     */
    @GetMapping("/roles")
    fun getRoleStatistics(): ResponseEntity<List<RoleStatisticsDTO>> {
        logger.info("👥 Role-Statistics-Request")

        return try {
            val stats = trendAnalysisService.analyzeRoleStatistics()
            ResponseEntity.ok(stats)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Role-Statistics", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    // =========================================================
    // METADATEN
    // =========================================================

    /**
     * Verfügbare Jahre (für Filter)
     *
     * GET /api/dashboard/available-years
     */
    @GetMapping("/available-years")
    fun getAvailableYears(): ResponseEntity<List<Int>> {
        logger.info("📅 Available-Years-Request")

        return try {
            val years = trendAnalysisService.getAvailableYears()
            ResponseEntity.ok(years)
        } catch (e: Exception) {
            logger.error("❌ Fehler bei Available-Years", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    /**
     * Health-Check
     *
     * GET /api/dashboard/health
     */
    @GetMapping("/health")
    fun healthCheck(): ResponseEntity<Map<String, String>> {
        logger.info("💚 Health-Check-Request")

        val response = mapOf(
            "status" to "OK",
            "service" to "Dashboard API",
            "timestamp" to java.time.Instant.now().toString()
        )

        return ResponseEntity.ok(response)
    }

    // =========================================================
    // EXPORT (OPTIONAL)
    // =========================================================

    /**
     * Export Dashboard-Daten als JSON
     * (Für Excel-Import oder weitere Verarbeitung)
     *
     * GET /api/dashboard/export?startYear=2015&endYear=2025
     */
    @GetMapping("/export")
    fun exportDashboard(
        @RequestParam(defaultValue = "2015") startYear: Int,
        @RequestParam(defaultValue = "2025") endYear: Int
    ): ResponseEntity<DashboardDTO> {
        logger.info("📥 Export-Request für Jahre $startYear-$endYear")

        return try {
            val dashboard = trendAnalysisService.generateDashboard(startYear, endYear)

            ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=dashboard_${startYear}_${endYear}.json")
                .body(dashboard)
        } catch (e: Exception) {
            logger.error("❌ Fehler beim Export", e)
            ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }
}
