package de.layher.jobmining.kotlinapi.infrastructure
import de.layher.jobmining.kotlinapi.domain.JobPosting
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

// Das Repository erbt von JpaRepository und ermöglicht Spring Data JPA
// das automatische Speichern, Finden und Aktualisieren der JobPosting-Entitäten.
@Repository
interface JobPostingRepository : JpaRepository<JobPosting, Long> {

    // Optional: Fügen Sie hier später Abfragemethoden hinzu, z.B. zur Abfrage nach Hash
    fun findByRawTextHash(rawTextHash: String): JobPosting?
}
