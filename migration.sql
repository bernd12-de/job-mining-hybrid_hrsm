-- =========================================================
-- DATENBANK-MIGRATION: 7-Ebenen-Modell & Idempotenz
-- =========================================================
-- Datum: 2024-12-27
-- Zweck: POC → Main Migration - Neue Spalten für wissenschaftliche Validierung
-- Branch: claude/fix-kotlin-python-api-b6uDC
-- =========================================================

-- =========================================================
-- 1. COMPETENCE-TABELLE: 7-Ebenen-Modell hinzufügen
-- =========================================================

-- Ebene 1: Discovery (Neufund - unbekannte Begriffe)
ALTER TABLE competence
ADD COLUMN IF NOT EXISTS is_discovery BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN competence.is_discovery IS 'Ebene 1: Markiert unbekannte Begriffe (Discovery), die nicht in ESCO gefunden wurden';

-- Ebene 2: ESCO Standard (level = 2 ist Default)
ALTER TABLE competence
ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 2;

COMMENT ON COLUMN competence.level IS 'Ebene 1-5: 1=Discovery, 2=ESCO, 3=Digital, 4=Fachbuch, 5=Academia';

-- Ebene 3: Digital-Hebel (digitale Skills)
ALTER TABLE competence
ADD COLUMN IF NOT EXISTS is_digital BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN competence.is_digital IS 'Ebene 3: Markiert digitale Kompetenzen (z.B. aus digitalSkillsCollection)';

-- Ebene 4/5: Fachbuch/Academia (Quelle)
ALTER TABLE competence
ADD COLUMN IF NOT EXISTS source_domain VARCHAR(255);

COMMENT ON COLUMN competence.source_domain IS 'Ebene 4/5: Quelle der Validierung (z.B. "Fachbuch: UX Design Patterns" oder "Modulhandbuch: TH Köln")';

-- Ebene 6: Rollen-Kontext
ALTER TABLE competence
ADD COLUMN IF NOT EXISTS role_context VARCHAR(255);

COMMENT ON COLUMN competence.role_context IS 'Ebene 6: Rollen-Kontext (z.B. "UX Designer", "Java Developer") für kontextsensitive Bewertung';

-- =========================================================
-- 2. JOB_POSTING-TABELLE: Idempotenz & Segmentierung
-- =========================================================

-- Ebene 7: Idempotenz (SHA-256 Hash)
ALTER TABLE job_posting
ADD COLUMN IF NOT EXISTS raw_text_hash TEXT;

COMMENT ON COLUMN job_posting.raw_text_hash IS 'Ebene 7: SHA-256 Hash des Rohtexts für Idempotenz (verhindert doppelte Einträge)';

-- UNIQUE Constraint für Hash (verhindert Duplikate)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'job_posting_raw_text_hash_unique'
    ) THEN
        ALTER TABLE job_posting
        ADD CONSTRAINT job_posting_raw_text_hash_unique UNIQUE (raw_text_hash);
    END IF;
END $$;

-- Ebene 6: Segmentierung (Aufgaben vs. Anforderungen)
ALTER TABLE job_posting
ADD COLUMN IF NOT EXISTS is_segmented BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN job_posting.is_segmented IS 'Ebene 6: Zeigt an, ob die Stellenanzeige segmentiert wurde (Aufgaben vs. Anforderungen)';

-- =========================================================
-- 3. INDICES FÜR PERFORMANCE
-- =========================================================

-- Index für Hash-Suche (Idempotenz-Check)
CREATE INDEX IF NOT EXISTS idx_job_posting_raw_text_hash
ON job_posting(raw_text_hash);

-- Index für Zeitreihen-Analyse (Datum-Filter)
CREATE INDEX IF NOT EXISTS idx_job_posting_posting_date
ON job_posting(posting_date);

-- Index für Rollen-Filter
CREATE INDEX IF NOT EXISTS idx_competence_role_context
ON competence(role_context);

-- Index für Level-Filter (Ebenen-Analyse)
CREATE INDEX IF NOT EXISTS idx_competence_level
ON competence(level);

-- Index für Discovery-Filter
CREATE INDEX IF NOT EXISTS idx_competence_is_discovery
ON competence(is_discovery);

-- Index für Digital-Skills-Filter
CREATE INDEX IF NOT EXISTS idx_competence_is_digital
ON competence(is_digital);

-- Composite Index für Zeitreihen-Aggregation
CREATE INDEX IF NOT EXISTS idx_job_posting_date_region
ON job_posting(posting_date, region);

-- =========================================================
-- 4. BESTEHENDE DATEN MIGRIEREN (Falls vorhanden)
-- =========================================================

-- Setze default level für bestehende Competences
UPDATE competence
SET level = 2
WHERE level IS NULL;

-- Markiere bestehende ESCO-Skills als nicht-Discovery
UPDATE competence
SET is_discovery = FALSE
WHERE is_discovery IS NULL AND esco_uri IS NOT NULL;

-- Markiere Skills ohne ESCO-URI als Discovery (falls vorhanden)
UPDATE competence
SET is_discovery = TRUE, level = 1
WHERE is_discovery IS NULL AND esco_uri IS NULL;

-- Setze is_segmented default für bestehende JobPostings
UPDATE job_posting
SET is_segmented = FALSE
WHERE is_segmented IS NULL;

-- =========================================================
-- 5. VALIDIERUNGS-CHECKS
-- =========================================================

-- Check: Level muss zwischen 1 und 5 liegen
ALTER TABLE competence
ADD CONSTRAINT competence_level_check
CHECK (level >= 1 AND level <= 5);

-- Check: is_digital nur bei ESCO-Skills (optional, kann entfernt werden)
-- ALTER TABLE competence
-- ADD CONSTRAINT competence_digital_esco_check
-- CHECK (NOT is_digital OR esco_uri IS NOT NULL);

-- =========================================================
-- 6. NEUE VIEWS FÜR ZEITREIHEN-ANALYSE
-- =========================================================

-- View: Jährliche Skill-Statistik
CREATE OR REPLACE VIEW v_yearly_skill_stats AS
SELECT
    EXTRACT(YEAR FROM jp.posting_date) AS year,
    c.esco_label,
    c.level,
    c.is_digital,
    c.role_context,
    COUNT(*) AS skill_count,
    AVG(c.confidence_score) AS avg_confidence,
    jp.region
FROM competence c
JOIN job_posting jp ON c.job_posting_id = jp.id
WHERE jp.posting_date IS NOT NULL
GROUP BY
    EXTRACT(YEAR FROM jp.posting_date),
    c.esco_label,
    c.level,
    c.is_digital,
    c.role_context,
    jp.region
ORDER BY year DESC, skill_count DESC;

COMMENT ON VIEW v_yearly_skill_stats IS 'Aggregierte Skill-Statistik pro Jahr für Zeitreihen-Analyse';

-- View: Top-10-Skills pro Jahr
CREATE OR REPLACE VIEW v_top_skills_per_year AS
WITH ranked_skills AS (
    SELECT
        EXTRACT(YEAR FROM jp.posting_date) AS year,
        c.esco_label,
        COUNT(*) AS skill_count,
        ROW_NUMBER() OVER (
            PARTITION BY EXTRACT(YEAR FROM jp.posting_date)
            ORDER BY COUNT(*) DESC
        ) AS rank
    FROM competence c
    JOIN job_posting jp ON c.job_posting_id = jp.id
    WHERE jp.posting_date IS NOT NULL
    GROUP BY EXTRACT(YEAR FROM jp.posting_date), c.esco_label
)
SELECT year, esco_label, skill_count, rank
FROM ranked_skills
WHERE rank <= 10
ORDER BY year DESC, rank ASC;

COMMENT ON VIEW v_top_skills_per_year IS 'Top-10-Skills pro Jahr für Dashboard';

-- View: Digitalisierungsrate pro Jahr
CREATE OR REPLACE VIEW v_digitalization_rate_per_year AS
SELECT
    EXTRACT(YEAR FROM jp.posting_date) AS year,
    COUNT(*) FILTER (WHERE c.is_digital = TRUE) AS digital_skills,
    COUNT(*) AS total_skills,
    ROUND(
        COUNT(*) FILTER (WHERE c.is_digital = TRUE)::NUMERIC /
        NULLIF(COUNT(*), 0) * 100,
        2
    ) AS digital_rate_percent
FROM competence c
JOIN job_posting jp ON c.job_posting_id = jp.id
WHERE jp.posting_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM jp.posting_date)
ORDER BY year DESC;

COMMENT ON VIEW v_digitalization_rate_per_year IS 'Digitalisierungsrate (% digitale Skills) pro Jahr';

-- =========================================================
-- 7. FUNKTIONEN FÜR TREND-BERECHNUNG
-- =========================================================

-- Funktion: Berechne Trend-Score (Anstieg/Rückgang)
CREATE OR REPLACE FUNCTION calculate_trend_score(
    skill_label TEXT,
    start_year INTEGER,
    end_year INTEGER
) RETURNS NUMERIC AS $$
DECLARE
    start_count INTEGER;
    end_count INTEGER;
    trend_score NUMERIC;
BEGIN
    -- Anzahl im Startjahr
    SELECT COUNT(*) INTO start_count
    FROM competence c
    JOIN job_posting jp ON c.job_posting_id = jp.id
    WHERE c.esco_label = skill_label
    AND EXTRACT(YEAR FROM jp.posting_date) = start_year;

    -- Anzahl im Endjahr
    SELECT COUNT(*) INTO end_count
    FROM competence c
    JOIN job_posting jp ON c.job_posting_id = jp.id
    WHERE c.esco_label = skill_label
    AND EXTRACT(YEAR FROM jp.posting_date) = end_year;

    -- Trend-Score berechnen (prozentuale Änderung)
    IF start_count > 0 THEN
        trend_score := ((end_count - start_count)::NUMERIC / start_count) * 100;
    ELSE
        trend_score := 0;
    END IF;

    RETURN ROUND(trend_score, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_trend_score IS 'Berechnet prozentuale Änderung eines Skills zwischen zwei Jahren';

-- =========================================================
-- 8. VERIFICATION QUERIES
-- =========================================================

-- Check: Anzahl Jobs mit Hash
SELECT COUNT(*) AS jobs_with_hash
FROM job_posting
WHERE raw_text_hash IS NOT NULL;

-- Check: Anzahl Competences mit Level
SELECT level, COUNT(*) AS count
FROM competence
GROUP BY level
ORDER BY level;

-- Check: Anzahl Discovery vs. ESCO
SELECT
    CASE
        WHEN is_discovery THEN 'Discovery (Ebene 1)'
        ELSE 'ESCO (Ebene 2+)'
    END AS type,
    COUNT(*) AS count
FROM competence
GROUP BY is_discovery;

-- Check: Digitale Skills
SELECT COUNT(*) AS digital_skills
FROM competence
WHERE is_digital = TRUE;

-- Check: Top-10-Skills gesamt
SELECT esco_label, COUNT(*) AS count
FROM competence
WHERE esco_label IS NOT NULL
GROUP BY esco_label
ORDER BY count DESC
LIMIT 10;

-- =========================================================
-- ENDE DER MIGRATION
-- =========================================================

-- Ausgabe der Migration
DO $$
BEGIN
    RAISE NOTICE '✅ Migration erfolgreich abgeschlossen!';
    RAISE NOTICE 'Neue Spalten in competence: is_discovery, level, is_digital, source_domain, role_context';
    RAISE NOTICE 'Neue Spalten in job_posting: raw_text_hash (UNIQUE), is_segmented';
    RAISE NOTICE 'Neue Indices: 7 Performance-Indices erstellt';
    RAISE NOTICE 'Neue Views: v_yearly_skill_stats, v_top_skills_per_year, v_digitalization_rate_per_year';
    RAISE NOTICE 'Neue Funktionen: calculate_trend_score()';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Nächste Schritte:';
    RAISE NOTICE '1. Kotlin-App neu starten (mit neuen Entities)';
    RAISE NOTICE '2. Python-Backend testen (POC-Version läuft)';
    RAISE NOTICE '3. Zeitreihen-Analyse implementieren (TrendAnalysisService.kt)';
END $$;
