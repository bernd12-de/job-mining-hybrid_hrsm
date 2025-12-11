package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*

// Domain Entity: Stellt die ESCO-gemappte Kompetenz dar
@Entity
// Hinweis: Durch allOpen im build.gradle.kts muss hier kein 'open' stehen
data class Competence(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    // 1. Der Begriff, wie er in der Stellenanzeige gefunden wurde (z.B. "Figma Tool")
    val originalTerm: String,

    // 2. Das offizielle ESCO-Label oder der Custom-Label-Eintrag
    val escoLabel: String,

    // 3. Die eindeutige URI von ESCO (z.B. "http://data.europa.eu/esco/skill/...") oder die Custom-ID
    val escoUri: String,

    // 4. Die Vertrauensbewertung der Zuordnung (z.B. 0.95)
    val confidenceScore: Double,

    // ZUSÄTZLICH für die hierarchische Analyse (Phase 3)
    // ESCO-Gruppencode für semantisches Clustering (z.B. T2.1 für "Kommunikationskompetenzen")
    @Column(nullable = true) // Kann für Custom Skills leer sein
    val escoGroupCode: String? = null
)
