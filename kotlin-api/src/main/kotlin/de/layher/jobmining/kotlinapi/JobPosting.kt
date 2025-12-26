package de.layher.jobmining.kotlinapi

import de.layher.jobmining.kotlinapi.domain.Competence
import jakarta.persistence.*
import java.time.LocalDate

@Entity
data class JobPosting(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val title: String,
    val jobRole: String,

    @Column(columnDefinition = "TEXT", unique = true)
    val rawTextHash: String, // Für Idempotenz-Prüfung

    val postingDate: LocalDate,
    val region: String,
    val industry: String,

    // Liste der gefundenen Kompetenzen
    @OneToMany(cascade = [CascadeType.ALL], fetch = FetchType.EAGER, orphanRemoval = true)
    @JoinColumn(name = "job_posting_id")
    val competences: List<Competence> = emptyList()
)
