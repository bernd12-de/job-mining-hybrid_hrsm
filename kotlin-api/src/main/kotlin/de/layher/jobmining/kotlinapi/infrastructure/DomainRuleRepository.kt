package de.layher.jobmining.kotlinapi.infrastructure

import de.layher.jobmining.kotlinapi.domain.DomainRule
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository

@Repository
interface DomainRuleRepository : JpaRepository<DomainRule, Long> {

    /**
     * Gibt alle aktiven Regeln eines bestimmten Typs (z.B. 'BLACKLIST') zurück.
     */
    fun findAllByRuleTypeAndIsActiveTrue(ruleType: String): List<DomainRule>

    /**
     * Sucht eine Regel anhand ihres Schlüssels (z.B. der Blacklist-Begriff)
     */
    fun findByRuleKey(ruleKey: String): DomainRule?
}
