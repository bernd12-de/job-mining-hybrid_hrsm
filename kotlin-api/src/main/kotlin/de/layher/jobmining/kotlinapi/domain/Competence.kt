package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*

// MUSS eine reguläre 'class' sein
@Entity
@Table(name = "competence")
class Competence(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "original_term",nullable = false,length = 512)
    val originalTerm: String,

    @Column(name = "esco_label",nullable = false,length = 512)
    val escoLabel: String,

    @Column(name = "esco_uri", nullable = false,length = 512)
    val escoUri: String,

    @Column(name = "confidence_score", nullable = false)
    val confidenceScore: Double,

    // ESCO-Gruppencode
    @Column(name = "esco_group_code", length = 255)
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
