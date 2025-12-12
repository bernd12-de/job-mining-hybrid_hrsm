package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDate

@Entity
data class JobPosting(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val title: String,
    val jobRole: String,

    @Column(columnDefinition = "TEXT")
    val rawTextHash: String, // Für Idempotenz-Prüfung

    // NEU: Speichert den gesamten extrahierten Text
    @Column(columnDefinition = "TEXT")
    val rawText: String,

    val postingDate: LocalDate,
    val region: String,
    val industry: String,

    // Liste der gefundenen Kompetenzen
    @OneToMany(cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    @JoinColumn(name = "job_id")
    val competences: List<Competence> = emptyList()
)

//@Entity
//data class Competence(
//    @Id
//    @GeneratedValue(strategy = GenerationType.IDENTITY)
//    val id: Long? = null,
//
//    val originalTerm: String,
//    val escoLabel: String,
//    val escoUri: String,
//    val confidenceScore: Double
//)
