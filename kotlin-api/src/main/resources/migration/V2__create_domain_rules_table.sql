-- V2__create_domain_rules_table.sql
-- ERSTELLT DIE TABELLE FÜR DAS WARTBARE REGELWERK (Domain Service)

CREATE TABLE domain_rule (
                             id BIGSERIAL PRIMARY KEY,
                             rule_type VARCHAR(50) NOT NULL,
                             rule_key VARCHAR(512) NOT NULL UNIQUE,
                             rule_value TEXT, -- Lässt den Wert NULL zu
                             is_active BOOLEAN NOT NULL DEFAULT TRUE,
                             created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index zur schnellen Abfrage der Regeln
CREATE INDEX idx_domain_rule_key ON domain_rule (rule_key);

-- Initiales Befüllen mit den Blacklist-Einträgen (PostgreSQL-Syntax ist korrekt)
-- Wir lassen rule_value explizit NULL, da es für Blacklist-Einträge nicht benötigt wird
-- und setzen rule_type auf 'BLACKLIST'.
INSERT INTO domain_rule (rule_type, rule_key) VALUES
                                                  ('BLACKLIST', 'kenntnisse'),
                                                  ('BLACKLIST', 'fähigkeiten'),
                                                  ('BLACKLIST', 'kommunikation'),
                                                  ('BLACKLIST', 'deutsch'),
                                                  ('BLACKLIST', 'englisch'),
                                                  ('BLACKLIST', 'erfahrung'),
                                                  ('BLACKLIST', 'agil'),
                                                  ('BLACKLIST', 'management'),
                                                  ('BLACKLIST', 'analyse'),
                                                  ('BLACKLIST', 'projektleitung'),
                                                  ('BLACKLIST', 'kunden'),
                                                  ('BLACKLIST', 'lösung'),
                                                  ('BLACKLIST', 'team'),
                                                  ('BLACKLIST', 'technik'),
                                                  ('BLACKLIST', 'bereich'),
                                                  ('BLACKLIST', 'verantwortung übernehmen'),
                                                  ('BLACKLIST', 'beratung'),
                                                  ('BLACKLIST', 'dienstleistungen'),
                                                  ('BLACKLIST', 'informatik'),
                                                  ('BLACKLIST', 'digitalisierung'),
                                                  ('BLACKLIST', 'prägen'),
                                                  ('BLACKLIST', 'datenschutz'),
                                                  ('BLACKLIST', 'ethik'),
                                                  ('BLACKLIST', 'gesundheit'),
                                                  ('BLACKLIST', 'kommunizieren'),
                                                  ('BLACKLIST', 'agiles');
