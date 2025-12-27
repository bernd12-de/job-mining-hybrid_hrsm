package de.layher.jobmining.kotlinapi.repository

import de.layher.jobmining.kotlinapi.domain.Competence
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository

@Repository
interface CompetenceRepository : JpaRepository<Competence, Long> {

    // =========================================================
    // 7-EBENEN-MODELL QUERIES
    // =========================================================

    /**
     * Findet alle Discovery-Skills (Ebene 1)
     */
    fun findByIsDiscoveryTrue(): List<Competence>

    /**
     * Findet alle Skills eines bestimmten Levels
     */
    fun findByLevel(level: Int): List<Competence>

    /**
     * Findet alle digitalen Skills (Ebene 3)
     */
    fun findByIsDigitalTrue(): List<Competence>

    /**
     * Findet alle Skills mit einem bestimmten Rollen-Kontext
     */
    fun findByRoleContext(roleContext: String): List<Competence>

    /**
     * Findet alle Skills aus einer bestimmten Source-Domain (Fachbuch/Academia)
     */
    fun findBySourceDomain(sourceDomain: String): List<Competence>

    // =========================================================
    // ZEITREIHEN-ANALYSE QUERIES
    // =========================================================

    /**
     * Top-N Skills für ein bestimmtes Jahr
     */
    @Query("""
        SELECT c.escoLabel, COUNT(c) as cnt
        FROM Competence c
        JOIN c.jobPosting j
        WHERE FUNCTION('YEAR', j.postingDate) = :year
        AND c.escoLabel IS NOT NULL
        GROUP BY c.escoLabel
        ORDER BY cnt DESC
    """)
    fun findTopSkillsByYear(@Param("year") year: Int): List<Array<Any>>

    /**
     * Top-N Skills für einen Jahresbereich
     */
    @Query("""
        SELECT c.escoLabel, COUNT(c) as cnt
        FROM Competence c
        JOIN c.jobPosting j
        WHERE FUNCTION('YEAR', j.postingDate) BETWEEN :startYear AND :endYear
        AND c.escoLabel IS NOT NULL
        GROUP BY c.escoLabel
        ORDER BY cnt DESC
    """)
    fun findTopSkillsByYearRange(
        @Param("startYear") startYear: Int,
        @Param("endYear") endYear: Int
    ): List<Array<Any>>

    /**
     * Zählt Competences pro Jahr
     */
    @Query("""
        SELECT FUNCTION('YEAR', j.postingDate) as year, COUNT(c) as count
        FROM Competence c
        JOIN c.jobPosting j
        WHERE j.postingDate IS NOT NULL
        GROUP BY FUNCTION('YEAR', j.postingDate)
        ORDER BY year DESC
    """)
    fun countCompetencesByYear(): List<Array<Any>>

    /**
     * Zählt digitale Skills pro Jahr (Digitalisierungsrate)
     */
    @Query("""
        SELECT
            FUNCTION('YEAR', j.postingDate) as year,
            COUNT(c) FILTER (WHERE c.isDigital = true) as digitalCount,
            COUNT(c) as totalCount
        FROM Competence c
        JOIN c.jobPosting j
        WHERE j.postingDate IS NOT NULL
        GROUP BY FUNCTION('YEAR', j.postingDate)
        ORDER BY year DESC
    """)
    fun countDigitalSkillsByYear(): List<Array<Any>>

    /**
     * Level-Verteilung pro Jahr
     */
    @Query("""
        SELECT
            FUNCTION('YEAR', j.postingDate) as year,
            c.level,
            COUNT(c) as count
        FROM Competence c
        JOIN c.jobPosting j
        WHERE j.postingDate IS NOT NULL
        GROUP BY FUNCTION('YEAR', j.postingDate), c.level
        ORDER BY year DESC, c.level
    """)
    fun countByLevelAndYear(): List<Array<Any>>

    // =========================================================
    // SKILL-TREND-ANALYSE
    // =========================================================

    /**
     * Zählt Vorkommen eines Skills für ein bestimmtes Jahr
     */
    @Query("""
        SELECT COUNT(c)
        FROM Competence c
        JOIN c.jobPosting j
        WHERE c.escoLabel = :skillLabel
        AND FUNCTION('YEAR', j.postingDate) = :year
    """)
    fun countSkillOccurrencesByYear(
        @Param("skillLabel") skillLabel: String,
        @Param("year") year: Int
    ): Long

    /**
     * Findet alle eindeutigen Skill-Labels (für Trend-Berechnung)
     */
    @Query("SELECT DISTINCT c.escoLabel FROM Competence c WHERE c.escoLabel IS NOT NULL")
    fun findAllUniqueSkillLabels(): List<String>

    // =========================================================
    // ROLLEN-STATISTIK
    // =========================================================

    /**
     * Top-Skills pro Rollen-Kontext
     */
    @Query("""
        SELECT c.roleContext, c.escoLabel, COUNT(c) as cnt
        FROM Competence c
        WHERE c.roleContext IS NOT NULL
        AND c.escoLabel IS NOT NULL
        GROUP BY c.roleContext, c.escoLabel
        ORDER BY c.roleContext, cnt DESC
    """)
    fun findTopSkillsByRole(): List<Array<Any>>

    /**
     * Zählt Competences pro Rollen-Kontext
     */
    @Query("""
        SELECT c.roleContext, COUNT(c)
        FROM Competence c
        WHERE c.roleContext IS NOT NULL
        GROUP BY c.roleContext
        ORDER BY COUNT(c) DESC
    """)
    fun countByRoleContext(): List<Array<Any>>

    // =========================================================
    // DURCHSCHNITTSWERTE
    // =========================================================

    /**
     * Durchschnittliche Confidence-Score für ein Jahr
     */
    @Query("""
        SELECT AVG(c.confidenceScore)
        FROM Competence c
        JOIN c.jobPosting j
        WHERE FUNCTION('YEAR', j.postingDate) = :year
    """)
    fun averageConfidenceByYear(@Param("year") year: Int): Double?

    /**
     * Durchschnittliche Anzahl Competences pro JobPosting
     */
    @Query("""
        SELECT AVG(size(j.competences))
        FROM JobPosting j
    """)
    fun averageCompetencesPerJob(): Double?
}
