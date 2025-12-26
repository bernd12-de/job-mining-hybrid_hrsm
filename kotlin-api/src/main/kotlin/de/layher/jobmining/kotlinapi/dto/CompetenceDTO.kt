package de.layher.jobmining.kotlinapi.dto

import com.fasterxml.jackson.annotation.JsonProperty

data class CompetenceDTO(
    @JsonProperty("original_term")
    val originalTerm: String,

    @JsonProperty("confidence_score")
    val confidenceScore: Double = 0.0,

    @JsonProperty("esco_label")
    val escoLabel: String,

    @JsonProperty("esco_uri")
    val escoUri: String,

    @JsonProperty("esco_group_code")
    val escoGroupCode: String? = null
)
