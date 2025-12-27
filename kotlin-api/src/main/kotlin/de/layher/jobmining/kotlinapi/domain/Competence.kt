package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*

// 🔴 WICHTIG: MUSS eine reguläre 'class' sein (nicht data class) für JPA bidirektionale Relationen
@Entity
@Table(name = "competence")
class Competence(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "original_term", nullable = false, length = 512)
    val originalTerm: String,

    @Column(name = "esco_label", length = 512)
    val escoLabel: String? = null,

    @Column(name = "esco_uri", length = 512)
    val escoUri: String? = null,

    @Column(name = "confidence_score")
    val confidenceScore: Double = 1.0,

    // ESCO-Gruppencode für semantisches Clustering
    @Column(name = "esco_group_code", length = 255)
    val escoGroupCode: String? = null,

    // --- 7-EBENEN-MODELL: Felder für wissenschaftliche Validierung ---
    @Column(name = "is_digital")
    val isDigital: Boolean = false,      // Ebene 3: Digital-Hebel

    @Column(name = "is_discovery")
    val isDiscovery: Boolean = false,    // Ebene 1: Neufund (Discovery)

    @Column(name = "level")
    val level: Int = 2,                  // Ebene 1-5 (Discovery, ESCO, Digital, Fachbuch, Academia)

    @Column(name = "role_context", length = 255)
    val roleContext: String? = null,     // Ebene 6: Rollen-Kontext (UX, Java Dev, etc.)

    @Column(name = "source_domain", length = 255)
    val sourceDomain: String? = null     // Ebene 4/5: Fachbuch/Modulhandbuch

) {
    // Bidirektionale Beziehung im Body (Standard-JPA-Fix für StackOverflow)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_posting_id", nullable = false)
    @com.fasterxml.jackson.annotation.JsonBackReference  // Verhindert zirkuläre Serialisierung
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
