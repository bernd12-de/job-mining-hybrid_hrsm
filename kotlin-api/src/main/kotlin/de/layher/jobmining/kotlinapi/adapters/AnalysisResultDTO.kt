package de.layher.jobmining.kotlinapi.adapters

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonCreator // NEUER IMPORT
import java.time.LocalDate

/**
 * DTO für eine einzelne extrahierte Kompetenz (Entspricht Python models.CompetenceDTO)
 */
data class CompetenceDTO @JsonCreator constructor(
    // Achtung: Wenn @JsonCreator genutzt wird, müssen alle Properties explizit im Konstruktor stehen.
    // Die @JsonProperty-Annotationen sind korrekt gesetzt.
    @JsonProperty("original_term")
    val originalTerm: String,

    @JsonProperty("confidence_score")
    val confidenceScore: Double,

    @JsonProperty("esco_label")
    val escoLabel: String,

    @JsonProperty("esco_uri")
    val escoUri: String,

    // Optional, da Custom Skills keinen ESCO Group Code haben
    @JsonProperty("esco_group_code")
    val escoGroupCode: String? = null
)

/**
 * DTO für das gesamte Analyseergebnis (Entspricht Python models.AnalysisResultDTO)
 */
data class AnalysisResultDTO @JsonCreator constructor(
    // Alle Properties müssen im primären Konstruktor stehen.
    val title: String,

    @JsonProperty("job_role")
    val jobRole: String,

    val region: String,
    val industry: String,

    @JsonProperty("posting_date")
    val postingDate: String,

    @JsonProperty("raw_text_hash")
    val rawTextHash: String,

    @JsonProperty("raw_text")
    val rawText: String,

    // Composite: Liste von Kompetenzen
    val competences: List<CompetenceDTO>
)
