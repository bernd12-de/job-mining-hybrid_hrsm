package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDate

// 🚨 FIX 1: Wechsel von data class zu class
@Entity
@Table(name = "job_posting")
class JobPosting(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(length = 1024)
    val title: String,
    @Column(length = 512)
    val jobRole: String,

    @Column(columnDefinition = "TEXT", unique = true)
    val rawTextHash: String, // <- Wichtig für Idempotenz und Hashcode

    @Column(columnDefinition = "TEXT")
    val rawText: String,

    val postingDate: LocalDate,
    val region: String,
    @Column(length = 512)
    val industry: String
) {
    // 🚨 FIX 2: Die bidirektionale Beziehung (ToMany) bleibt im Body.
    @OneToMany(mappedBy = "jobPosting", cascade = [CascadeType.ALL], orphanRemoval = true, fetch = FetchType.LAZY)
    var competences: MutableSet<Competence> = mutableSetOf()

    // 🚨 FIX 3: Manuelle Implementierung von equals und hashCode (ohne competences!)
    // Wir verwenden rawTextHash als Business-Key, da es UNIQUE ist (Idempotenz).
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is JobPosting) return false

        // Wir nutzen den Hash des Textes zur Identifizierung, falls die ID noch null ist
        return rawTextHash == other.rawTextHash
    }

    override fun hashCode(): Int {
        // Wir nutzen den Hash des Textes zur Identifizierung
        return rawTextHash.hashCode()
    }
}
