package de.layher.jobmining.kotlinapi.domain

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "domain_rule")
data class DomainRule(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    // Typ der Regel: 'BLACKLIST', 'INDUSTRY_MAPPING', 'ROLE_PATTERN'
    @Column(length = 50, nullable = false)
    val ruleType: String,

    // Der Schlüsselbegriff (z.B. "kenntnisse" für Blacklist)
    @Column(length = 512, nullable = false, unique = true)
    val ruleKey: String,

    // Der Wert oder das Muster (z.B. "TRUE" für Blacklist-Einträge)
    @Column(columnDefinition = "TEXT", nullable = true)
    val ruleValue: String?,

    @Column(nullable = false)
    val isActive: Boolean = true,

    val createdAt: LocalDateTime = LocalDateTime.now()
)
