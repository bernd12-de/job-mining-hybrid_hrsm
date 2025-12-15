-- V1__create_initial_schema.sql
-- ERSTELLT DAS KORRIGIERTE SCHEMA MIT SICHEREN LÄNGEN (SSoT)

-- 1. Tabelle: job_posting (Basierend auf JobPosting.kt)
CREATE TABLE job_posting (
                             id BIGSERIAL PRIMARY KEY,
                             title VARCHAR(1024) NOT NULL, -- Korrigierte Länge
                             job_role VARCHAR(512) NOT NULL,
                             raw_text_hash TEXT NOT NULL UNIQUE, -- TEXT für SHA-256 Hash
                             raw_text TEXT NOT NULL, -- Korrigierter Typ für den gesamten Stellentext
                             posting_date DATE NOT NULL,
                             region VARCHAR(255) NOT NULL,
                             industry VARCHAR(512) NOT NULL
);

-- 2. Tabelle: competence (Basierend auf Competence.kt)
CREATE TABLE competence (
                            id BIGSERIAL PRIMARY KEY,
                            job_posting_id BIGINT NOT NULL REFERENCES job_posting(id), -- Foreign Key

                            original_term VARCHAR(512) NOT NULL, -- Korrigierte Länge
                            esco_label VARCHAR(512) NOT NULL, -- Korrigierte Länge
                            esco_uri VARCHAR(512) NOT NULL, -- KRITISCH: Korrigierte Länge für ESCO-URLs
                            confidence_score DOUBLE PRECISION NOT NULL,
                            esco_group_code VARCHAR(255)
);

-- Index zur Beschleunigung der Abfragen (Zeitreihenanalyse)
CREATE INDEX idx_job_posting_date ON job_posting (posting_date);
CREATE INDEX idx_competence_label ON competence (esco_label);
