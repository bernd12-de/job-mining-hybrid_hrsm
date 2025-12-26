package de.layher.jobmining.kotlinapi.dto

import com.fasterxml.jackson.annotation.JsonProperty

data class AnalysisResultDTO(
    val title: String,

    @JsonProperty("job_role")
    val jobRole: String,

    val region: String,
    val industry: String,

    @JsonProperty("posting_date")
    val postingDate: String,

    @JsonProperty("raw_text_hash")
    val rawTextHash: String,

    val competences: List<CompetenceDTO>
)
