package de.layher.jobmining.kotlinapi.domain.rules

// core/domain/rules/SkillBlacklist.kt
object SkillBlacklist {
    private val blacklist = setOf(
        "erfahrung", "kenntnisse", "bereich", "aufgaben",
        "verantwortung", "team", "sowie", "entwicklung"
    )

    fun isBlacklisted(label: String): Boolean = label.lowercase() in blacklist
}
