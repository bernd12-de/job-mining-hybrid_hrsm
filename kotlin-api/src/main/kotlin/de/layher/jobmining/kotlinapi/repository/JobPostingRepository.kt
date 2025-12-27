package de.layher.jobmining.kotlinapi.repository

import de.layher.jobmining.kotlinapi.domain.JobPosting
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.time.LocalDate

@Repository
interface JobPostingRepository : JpaRepository<JobPosting, Long> {

    // =========================================================
    // IDEMPOTENZ (EBENE 7)
    // =========================================================

    /**
     * Findet JobPosting anhand des SHA-256 Hash (Idempotenz-Check)
     */
    fun findByRawTextHash(rawTextHash: String): List<JobPosting>

    // =========================================================
    // ZEITREIHEN-ANALYSE
    // =========================================================

    /**
     * Findet alle JobPostings eines bestimmten Jahres
     */
    @Query("SELECT j FROM JobPosting j WHERE FUNCTION('YEAR', j.postingDate) = :year")
    fun findByPostingDateYear(@Param("year") year: Int): List<JobPosting>

    /**
     * Findet alle JobPostings zwischen zwei Jahren
     */
    @Query("SELECT j FROM JobPosting j WHERE FUNCTION('YEAR', j.postingDate) BETWEEN :startYear AND :endYear")
    fun findByPostingDateYearRange(
        @Param("startYear") startYear: Int,
        @Param("endYear") endYear: Int
    ): List<JobPosting>

    /**
     * Findet alle JobPostings zwischen zwei Daten
     */
    fun findByPostingDateBetween(startDate: LocalDate, endDate: LocalDate): List<JobPosting>

    /**
     * Zählt JobPostings pro Jahr
     */
    @Query("""
        SELECT FUNCTION('YEAR', j.postingDate) as year, COUNT(j) as count
        FROM JobPosting j
        WHERE j.postingDate IS NOT NULL
        GROUP BY FUNCTION('YEAR', j.postingDate)
        ORDER BY year DESC
    """)
    fun countJobPostingsByYear(): List<Array<Any>>

    /**
     * Findet alle JobPostings einer bestimmten Region
     */
    fun findByRegion(region: String): List<JobPosting>

    /**
     * Findet alle JobPostings einer bestimmten Branche
     */
    fun findByIndustry(industry: String): List<JobPosting>

    /**
     * Findet alle JobPostings mit Segmentierung
     */
    fun findByIsSegmented(isSegmented: Boolean): List<JobPosting>

    /**
     * Zählt segmentierte vs. nicht-segmentierte JobPostings
     */
    @Query("""
        SELECT j.isSegmented, COUNT(j)
        FROM JobPosting j
        GROUP BY j.isSegmented
    """)
    fun countBySegmentation(): List<Array<Any>>

    // =========================================================
    // STATISTIK-QUERIES
    // =========================================================

    /**
     * Findet die neuesten N JobPostings
     */
    fun findTop10ByOrderByPostingDateDesc(): List<JobPosting>

    /**
     * Zählt alle JobPostings
     */
    @Query("SELECT COUNT(j) FROM JobPosting j")
    fun countAllJobPostings(): Long

    /**
     * Findet alle verfügbaren Jahre (für Filter)
     */
    @Query("""
        SELECT DISTINCT FUNCTION('YEAR', j.postingDate)
        FROM JobPosting j
        WHERE j.postingDate IS NOT NULL
        ORDER BY FUNCTION('YEAR', j.postingDate) DESC
    """)
    fun findAvailableYears(): List<Int>

    /**
     * Findet alle verfügbaren Regionen (für Filter)
     */
    @Query("SELECT DISTINCT j.region FROM JobPosting j ORDER BY j.region")
    fun findAvailableRegions(): List<String>

    /**
     * Findet alle verfügbaren Branchen (für Filter)
     */
    @Query("SELECT DISTINCT j.industry FROM JobPosting j ORDER BY j.industry")
    fun findAvailableIndustries(): List<String>
}
