package de.layher.jobmining.kotlinapi.dto

import com.fasterxml.jackson.annotation.JsonProperty

/**
 * DTO für jährliche Trend-Daten (Zeitreihen-Analyse)
 * Wird verwendet für Dashboard und Poster-Visualisierung
 */
data class YearlyTrendDTO(
    val year: Int,

    @JsonProperty("total_jobs")
    val totalJobs: Int,

    @JsonProperty("total_competences")
    val totalCompetences: Int,

    @JsonProperty("top_skills")
    val topSkills: List<SkillCountDTO>,

    @JsonProperty("digital_rate")
    val digitalRate: Double,  // Prozentsatz digitaler Skills

    @JsonProperty("avg_confidence")
    val avgConfidence: Double
)

/**
 * DTO für Skill-Zählung
 */
data class SkillCountDTO(
    @JsonProperty("esco_label")
    val escoLabel: String,

    val count: Int,

    val level: Int? = null,

    @JsonProperty("is_digital")
    val isDigital: Boolean? = null,

    @JsonProperty("role_context")
    val roleContext: String? = null
)

/**
 * DTO für Skill-Trend (Vergleich zwischen Jahren)
 */
data class SkillTrendDTO(
    @JsonProperty("esco_label")
    val escoLabel: String,

    @JsonProperty("start_year")
    val startYear: Int,

    @JsonProperty("end_year")
    val endYear: Int,

    @JsonProperty("start_count")
    val startCount: Int,

    @JsonProperty("end_count")
    val endCount: Int,

    @JsonProperty("trend_score")
    val trendScore: Double,  // Prozentuale Änderung

    @JsonProperty("trend_direction")
    val trendDirection: String  // "steigend", "fallend", "stabil"
) {
    companion object {
        fun calculateTrendDirection(trendScore: Double): String {
            return when {
                trendScore > 10.0 -> "steigend"
                trendScore < -10.0 -> "fallend"
                else -> "stabil"
            }
        }
    }
}

/**
 * DTO für Digitalisierungsrate pro Jahr
 */
data class DigitalizationRateDTO(
    val year: Int,

    @JsonProperty("digital_skills")
    val digitalSkills: Int,

    @JsonProperty("total_skills")
    val totalSkills: Int,

    @JsonProperty("digital_rate_percent")
    val digitalRatePercent: Double
)

/**
 * DTO für Rollen-Statistik
 */
data class RoleStatisticsDTO(
    @JsonProperty("role_context")
    val roleContext: String,

    @JsonProperty("job_count")
    val jobCount: Int,

    @JsonProperty("avg_competences_per_job")
    val avgCompetencesPerJob: Double,

    @JsonProperty("top_skills")
    val topSkills: List<SkillCountDTO>
)

/**
 * DTO für Regions-Statistik
 */
data class RegionStatisticsDTO(
    val region: String,

    @JsonProperty("job_count")
    val jobCount: Int,

    @JsonProperty("top_skills")
    val topSkills: List<SkillCountDTO>
)

/**
 * DTO für Level-Verteilung (7-Ebenen-Modell)
 */
data class LevelDistributionDTO(
    val year: Int,

    @JsonProperty("level_1_discovery")
    val level1Discovery: Int,

    @JsonProperty("level_2_esco")
    val level2Esco: Int,

    @JsonProperty("level_3_digital")
    val level3Digital: Int,

    @JsonProperty("level_4_textbook")
    val level4Textbook: Int,

    @JsonProperty("level_5_academia")
    val level5Academia: Int
)

/**
 * DTO für komplette Dashboard-Antwort
 */
data class DashboardDTO(
    @JsonProperty("time_range")
    val timeRange: String,  // z.B. "2015-2025"

    @JsonProperty("yearly_trends")
    val yearlyTrends: List<YearlyTrendDTO>,

    @JsonProperty("top_rising_skills")
    val topRisingSkills: List<SkillTrendDTO>,

    @JsonProperty("top_falling_skills")
    val topFallingSkills: List<SkillTrendDTO>,

    @JsonProperty("digitalization_trend")
    val digitalizationTrend: List<DigitalizationRateDTO>,

    @JsonProperty("level_distribution")
    val levelDistribution: List<LevelDistributionDTO>
)
