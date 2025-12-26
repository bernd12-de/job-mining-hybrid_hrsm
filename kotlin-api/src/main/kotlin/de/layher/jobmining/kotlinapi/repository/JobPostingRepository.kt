package de.layher.jobmining.kotlinapi.repository

import de.layher.jobmining.kotlinapi.JobPosting
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface JobPostingRepository : JpaRepository<JobPosting, Long> {
    fun findByRawTextHash(rawTextHash: String): JobPosting?
}
