package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*

// MUSS eine reguläre 'class' sein
@Entity
@Table(name = "competence")
class Competence(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(length = 512)
    val originalTerm: String,

    @Column(length = 512)
    val escoLabel: String,

    @Column(length = 512)
    val escoUri: String,

    val confidenceScore: Double,

    // ESCO-Gruppencode
    @Column(nullable = true)
    val escoGroupCode: String? = null // KEIN KOMMA HIER, da dies das letzte Element ist
) {
    // Bidirektionale Beziehung im Body (Standard-JPA-Fix für StackOverflow)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_posting_id", nullable = false)
    var jobPosting: JobPosting? = null

    // Manuelle equals/hashCode (StackOverflow-Fix)
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Competence) return false
        return id != null && id == other.id
    }

    override fun hashCode(): Int {
        return id?.hashCode() ?: 0
    }
}
