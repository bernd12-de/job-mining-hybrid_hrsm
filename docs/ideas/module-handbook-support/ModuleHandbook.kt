// 🔵 KONZEPT - Beispiel-Code für Modulhandbuch-Entity
// NICHT in Produktion verwenden!

package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDate

/**
 * Domain-Entity für Modulhandbücher von Universitäten/Fachhochschulen
 *
 * BEISPIEL-CODE - Zeigt wie die Struktur aussehen könnte
 *
 * HINWEIS: Benötigt Competence-Entity im selben Package oder Import:
 * import de.layher.jobmining.kotlinapi.domain.Competence
 */
@Entity
data class ModuleHandbook(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    // Basis-Informationen
    val title: String,

    @Column(columnDefinition = "TEXT", unique = true)
    val rawTextHash: String,

    // Hochschul-spezifische Metadaten
    val university: String,              // z.B. "DHBW Karlsruhe"
    val studyCourse: String,             // z.B. "Wirtschaftsinformatik"
    val moduleCode: String,              // z.B. "WIN-INF-2023"
    val semester: String,                // z.B. "3. Semester"
    val ects: Int,                       // z.B. 5 ECTS

    @Enumerated(EnumType.STRING)
    val moduleType: ModuleType,          // Pflicht, Wahlpflicht, Wahlfach

    val workloadHours: Int? = null,      // z.B. 150 Stunden
    val lectureName: String? = null,     // Name der Vorlesung

    @Column(columnDefinition = "TEXT")
    val learningObjectives: String? = null,  // Lernziele

    @Column(columnDefinition = "TEXT")
    val content: String? = null,         // Modulinhalte

    val uploadDate: LocalDate = LocalDate.now(),

    // Extrahierte Kompetenzen
    @OneToMany(cascade = [CascadeType.ALL], fetch = FetchType.EAGER, orphanRemoval = true)
    @JoinColumn(name = "module_handbook_id")
    val competences: List<Competence> = emptyList()
)

enum class ModuleType {
    PFLICHTMODUL,
    WAHLPFLICHTMODUL,
    WAHLFACH
}
