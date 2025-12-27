package de.layher.jobmining.kotlinapi.service

import de.layher.jobmining.kotlinapi.dto.*
import de.layher.jobmining.kotlinapi.repository.CompetenceRepository
import de.layher.jobmining.kotlinapi.repository.JobPostingRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

/**
 * Service für Zeitreihen-Analyse und Trend-Berechnung
 * Kern-Service für die Postersession (14. Januar 2025)
 */
@Service
class TrendAnalysisService(
    private val jobPostingRepository: JobPostingRepository,
    private val competenceRepository: CompetenceRepository
) {
    private val logger = LoggerFactory.getLogger(TrendAnalysisService::class.java)

    // =========================================================
    // JÄHRLICHE TREND-ANALYSE
    // =========================================================

    /**
     * Analysiert Trends für einen Jahresbereich (z.B. 2015-2025)
     * KERN-FUNKTION für Postersession!
     */
    @Transactional(readOnly = true)
    fun analyzeYearlyTrends(startYear: Int, endYear: Int): List<YearlyTrendDTO> {
        logger.info("📊 Starte Zeitreihen-Analyse für Jahre $startYear-$endYear")

        val trends = mutableListOf<YearlyTrendDTO>()

        for (year in startYear..endYear) {
            val jobPostings = jobPostingRepository.findByPostingDateYear(year)

            if (jobPostings.isEmpty()) {
                logger.warn("⚠️ Keine Daten für Jahr $year gefunden")
                continue
            }

            val allCompetences = jobPostings.flatMap { it.competences }

            // Top-10-Skills für dieses Jahr
            val topSkills = allCompetences
                .filter { it.escoLabel != null }
                .groupBy { it.escoLabel!! }
                .mapValues { (_, competences) ->
                    SkillCountDTO(
                        escoLabel = competences.first().escoLabel!!,
                        count = competences.size,
                        level = competences.first().level,
                        isDigital = competences.first().isDigital,
                        roleContext = competences.first().roleContext
                    )
                }
                .values
                .sortedByDescending { it.count }
                .take(10)

            // Digitalisierungsrate berechnen
            val digitalCount = allCompetences.count { it.isDigital }
            val digitalRate = if (allCompetences.isNotEmpty()) {
                (digitalCount.toDouble() / allCompetences.size) * 100
            } else 0.0

            // Durchschnittliche Confidence
            val avgConfidence = allCompetences
                .map { it.confidenceScore }
                .average()

            trends.add(
                YearlyTrendDTO(
                    year = year,
                    totalJobs = jobPostings.size,
                    totalCompetences = allCompetences.size,
                    topSkills = topSkills,
                    digitalRate = String.format("%.2f", digitalRate).toDouble(),
                    avgConfidence = String.format("%.2f", avgConfidence).toDouble()
                )
            )

            logger.info("✅ Jahr $year: ${jobPostings.size} Jobs, ${allCompetences.size} Skills, ${String.format("%.2f", digitalRate)}% digital")
        }

        return trends
    }

    /**
     * Findet die Top-N steigenden Skills (über alle Jahre)
     */
    @Transactional(readOnly = true)
    fun findTopRisingSkills(startYear: Int, endYear: Int, limit: Int = 10): List<SkillTrendDTO> {
        logger.info("📈 Suche Top-$limit steigende Skills ($startYear-$endYear)")

        val allSkills = competenceRepository.findAllUniqueSkillLabels()
        val trends = mutableListOf<SkillTrendDTO>()

        for (skill in allSkills) {
            val startCount = competenceRepository.countSkillOccurrencesByYear(skill, startYear).toInt()
            val endCount = competenceRepository.countSkillOccurrencesByYear(skill, endYear).toInt()

            if (startCount > 0) {  // Nur Skills, die im Startjahr existierten
                val trendScore = ((endCount - startCount).toDouble() / startCount) * 100

                trends.add(
                    SkillTrendDTO(
                        escoLabel = skill,
                        startYear = startYear,
                        endYear = endYear,
                        startCount = startCount,
                        endCount = endCount,
                        trendScore = String.format("%.2f", trendScore).toDouble(),
                        trendDirection = SkillTrendDTO.calculateTrendDirection(trendScore)
                    )
                )
            }
        }

        return trends
            .filter { it.trendScore > 0 }  // Nur steigende Skills
            .sortedByDescending { it.trendScore }
            .take(limit)
    }

    /**
     * Findet die Top-N fallenden Skills (über alle Jahre)
     */
    @Transactional(readOnly = true)
    fun findTopFallingSkills(startYear: Int, endYear: Int, limit: Int = 10): List<SkillTrendDTO> {
        logger.info("📉 Suche Top-$limit fallende Skills ($startYear-$endYear)")

        val allSkills = competenceRepository.findAllUniqueSkillLabels()
        val trends = mutableListOf<SkillTrendDTO>()

        for (skill in allSkills) {
            val startCount = competenceRepository.countSkillOccurrencesByYear(skill, startYear).toInt()
            val endCount = competenceRepository.countSkillOccurrencesByYear(skill, endYear).toInt()

            if (startCount > 0) {
                val trendScore = ((endCount - startCount).toDouble() / startCount) * 100

                trends.add(
                    SkillTrendDTO(
                        escoLabel = skill,
                        startYear = startYear,
                        endYear = endYear,
                        startCount = startCount,
                        endCount = endCount,
                        trendScore = String.format("%.2f", trendScore).toDouble(),
                        trendDirection = SkillTrendDTO.calculateTrendDirection(trendScore)
                    )
                )
            }
        }

        return trends
            .filter { it.trendScore < 0 }  // Nur fallende Skills
            .sortedBy { it.trendScore }  // Aufsteigend (negativste zuerst)
            .take(limit)
    }

    // =========================================================
    // DIGITALISIERUNGS-TREND
    // =========================================================

    /**
     * Analysiert die Digitalisierungsrate pro Jahr
     */
    @Transactional(readOnly = true)
    fun analyzeDigitalizationTrend(startYear: Int, endYear: Int): List<DigitalizationRateDTO> {
        logger.info("💻 Analysiere Digitalisierungsrate ($startYear-$endYear)")

        val rates = mutableListOf<DigitalizationRateDTO>()

        for (year in startYear..endYear) {
            val allCompetences = jobPostingRepository.findByPostingDateYear(year)
                .flatMap { it.competences }

            val digitalSkills = allCompetences.count { it.isDigital }
            val totalSkills = allCompetences.size

            val digitalRatePercent = if (totalSkills > 0) {
                (digitalSkills.toDouble() / totalSkills) * 100
            } else 0.0

            rates.add(
                DigitalizationRateDTO(
                    year = year,
                    digitalSkills = digitalSkills,
                    totalSkills = totalSkills,
                    digitalRatePercent = String.format("%.2f", digitalRatePercent).toDouble()
                )
            )
        }

        return rates
    }

    // =========================================================
    // LEVEL-VERTEILUNG (7-EBENEN-MODELL)
    // =========================================================

    /**
     * Analysiert die Verteilung der Ebenen pro Jahr
     */
    @Transactional(readOnly = true)
    fun analyzeLevelDistribution(startYear: Int, endYear: Int): List<LevelDistributionDTO> {
        logger.info("🎯 Analysiere Ebenen-Verteilung ($startYear-$endYear)")

        val distributions = mutableListOf<LevelDistributionDTO>()

        for (year in startYear..endYear) {
            val allCompetences = jobPostingRepository.findByPostingDateYear(year)
                .flatMap { it.competences }

            val level1 = allCompetences.count { it.level == 1 }
            val level2 = allCompetences.count { it.level == 2 }
            val level3 = allCompetences.count { it.isDigital }  // Ebene 3
            val level4 = allCompetences.count { it.level == 4 }
            val level5 = allCompetences.count { it.level == 5 }

            distributions.add(
                LevelDistributionDTO(
                    year = year,
                    level1Discovery = level1,
                    level2Esco = level2,
                    level3Digital = level3,
                    level4Textbook = level4,
                    level5Academia = level5
                )
            )
        }

        return distributions
    }

    // =========================================================
    // ROLLEN-STATISTIK
    // =========================================================

    /**
     * Analysiert Skills pro Rollen-Kontext
     */
    @Transactional(readOnly = true)
    fun analyzeRoleStatistics(): List<RoleStatisticsDTO> {
        logger.info("👥 Analysiere Rollen-Statistik")

        val roleStats = mutableListOf<RoleStatisticsDTO>()
        val competences = competenceRepository.findAll()

        val groupedByRole = competences
            .filter { it.roleContext != null }
            .groupBy { it.roleContext!! }

        for ((role, competencesForRole) in groupedByRole) {
            val jobCount = competencesForRole.mapNotNull { it.jobPosting }.distinct().size

            val avgCompetencesPerJob = if (jobCount > 0) {
                competencesForRole.size.toDouble() / jobCount
            } else 0.0

            val topSkills = competencesForRole
                .filter { it.escoLabel != null }
                .groupBy { it.escoLabel!! }
                .mapValues { (_, comps) -> comps.size }
                .entries
                .sortedByDescending { it.value }
                .take(5)
                .map { SkillCountDTO(escoLabel = it.key, count = it.value) }

            roleStats.add(
                RoleStatisticsDTO(
                    roleContext = role,
                    jobCount = jobCount,
                    avgCompetencesPerJob = String.format("%.2f", avgCompetencesPerJob).toDouble(),
                    topSkills = topSkills
                )
            )
        }

        return roleStats.sortedByDescending { it.jobCount }
    }

    // =========================================================
    // DASHBOARD (KOMPLETT)
    // =========================================================

    /**
     * Erstellt komplettes Dashboard für Postersession
     */
    @Transactional(readOnly = true)
    fun generateDashboard(startYear: Int, endYear: Int): DashboardDTO {
        logger.info("🚀 Generiere vollständiges Dashboard ($startYear-$endYear)")

        return DashboardDTO(
            timeRange = "$startYear-$endYear",
            yearlyTrends = analyzeYearlyTrends(startYear, endYear),
            topRisingSkills = findTopRisingSkills(startYear, endYear, 10),
            topFallingSkills = findTopFallingSkills(startYear, endYear, 10),
            digitalizationTrend = analyzeDigitalizationTrend(startYear, endYear),
            levelDistribution = analyzeLevelDistribution(startYear, endYear)
        )
    }

    // =========================================================
    // HELPER-FUNKTIONEN
    // =========================================================

    /**
     * Prüft, ob Daten für einen Jahresbereich vorhanden sind
     */
    fun hasDataForYearRange(startYear: Int, endYear: Int): Boolean {
        val availableYears = jobPostingRepository.findAvailableYears()
        return availableYears.any { it in startYear..endYear }
    }

    /**
     * Gibt alle verfügbaren Jahre zurück
     */
    fun getAvailableYears(): List<Int> {
        return jobPostingRepository.findAvailableYears()
    }
}
