-- =====================================================
-- JOB MINING - PostgreSQL Database Schema
-- Version: 1.0
-- Für: Geo-Dashboard mit Jahr/Berufs-Filtern
-- =====================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- Optional für Geo-Queries

-- =====================================================
-- 1. LOCATIONS (Städte mit Geo-Koordinaten)
-- =====================================================
DROP TABLE IF EXISTS locations CASCADE;
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(2) DEFAULT 'DE',
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(city, country)
);

CREATE INDEX idx_locations_city ON locations(city);
CREATE INDEX idx_locations_country ON locations(country);

-- Sample Data
INSERT INTO locations (city, country, latitude, longitude, region) VALUES
    ('Berlin', 'DE', 52.5200, 13.4050, 'Berlin'),
    ('München', 'DE', 48.1351, 11.5820, 'Bayern'),
    ('Hamburg', 'DE', 53.5511, 9.9937, 'Hamburg'),
    ('Köln', 'DE', 50.9375, 6.9603, 'Nordrhein-Westfalen'),
    ('Frankfurt', 'DE', 50.1109, 8.6821, 'Hessen'),
    ('Stuttgart', 'DE', 48.7758, 9.1829, 'Baden-Württemberg'),
    ('Düsseldorf', 'DE', 51.2277, 6.7735, 'Nordrhein-Westfalen'),
    ('Leipzig', 'DE', 51.3397, 12.3731, 'Sachsen'),
    ('Dresden', 'DE', 51.0504, 13.7373, 'Sachsen'),
    ('Dortmund', 'DE', 51.5136, 7.4653, 'Nordrhein-Westfalen'),
    ('Remote', 'REMOTE', NULL, NULL, 'Remote')
ON CONFLICT (city, country) DO NOTHING;

-- =====================================================
-- 2. JOBS (Stellenanzeigen)
-- =====================================================
DROP TABLE IF EXISTS jobs CASCADE;
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    role VARCHAR(100),  -- 'Software Developer', 'Data Scientist', etc.
    description TEXT,
    location_id INTEGER REFERENCES locations(id),
    posted_at TIMESTAMP NOT NULL,
    year INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM posted_at)) STORED,
    source VARCHAR(50),  -- 'python', 'kotlin', 'api', 'scraper'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_role ON jobs(role);
CREATE INDEX idx_jobs_year ON jobs(year);
CREATE INDEX idx_jobs_location ON jobs(location_id);
CREATE INDEX idx_jobs_posted_at ON jobs(posted_at);

-- =====================================================
-- 3. SKILLS (Kompetenzen-Master-Liste)
-- =====================================================
DROP TABLE IF EXISTS skills CASCADE;
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),  -- 'Programming', 'Framework', 'Tool', 'Soft Skill'
    is_digital BOOLEAN DEFAULT FALSE,
    esco_uri VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_category ON skills(category);

-- Sample Skills
INSERT INTO skills (name, category, is_digital) VALUES
    ('Python', 'Programming', TRUE),
    ('Java', 'Programming', TRUE),
    ('JavaScript', 'Programming', TRUE),
    ('Docker', 'Tool', TRUE),
    ('Kubernetes', 'Tool', TRUE),
    ('Git', 'Tool', TRUE),
    ('SQL', 'Programming', TRUE),
    ('React', 'Framework', TRUE),
    ('TypeScript', 'Programming', TRUE),
    ('AWS', 'Cloud', TRUE),
    ('Machine Learning', 'AI/ML', TRUE),
    ('R', 'Programming', TRUE),
    ('TensorFlow', 'Framework', TRUE),
    ('PyTorch', 'Framework', TRUE),
    ('Pandas', 'Library', TRUE),
    ('Terraform', 'Tool', TRUE),
    ('Jenkins', 'Tool', TRUE),
    ('Linux', 'OS', TRUE),
    ('CI/CD', 'Process', TRUE),
    ('Ansible', 'Tool', TRUE),
    ('Agile', 'Methodology', FALSE),
    ('Scrum', 'Methodology', FALSE),
    ('Jira', 'Tool', TRUE),
    ('Figma', 'Tool', TRUE),
    ('Adobe XD', 'Tool', TRUE)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- 4. JOB_SKILLS (Many-to-Many: Jobs <-> Skills)
-- =====================================================
DROP TABLE IF EXISTS job_skills CASCADE;
CREATE TABLE job_skills (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    confidence DECIMAL(3, 2) DEFAULT 1.0,  -- Matching-Confidence (0.0-1.0)
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_id, skill_id)
);

CREATE INDEX idx_job_skills_job ON job_skills(job_id);
CREATE INDEX idx_job_skills_skill ON job_skills(skill_id);

-- =====================================================
-- 5. DATA_SOURCES (Tracking woher Daten kommen)
-- =====================================================
DROP TABLE IF EXISTS data_sources CASCADE;
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,  -- 'Python Backend', 'Kotlin Service', 'External API'
    source_type VARCHAR(50),  -- 'internal', 'external', 'scraper'
    last_sync TIMESTAMP,
    total_jobs_imported INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB,  -- Flexible Konfiguration
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO data_sources (source_name, source_type, is_active) VALUES
    ('Python FastAPI', 'internal', TRUE),
    ('Kotlin Spring Boot', 'internal', TRUE),
    ('External Python Client', 'external', TRUE)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 6. VIEWS (Vorberechnete Abfragen)
-- =====================================================

-- View: Job-Counts pro Stadt
CREATE OR REPLACE VIEW v_jobs_per_location AS
SELECT
    l.id as location_id,
    l.city,
    l.country,
    l.latitude,
    l.longitude,
    j.year,
    j.role,
    COUNT(j.id) as job_count
FROM locations l
LEFT JOIN jobs j ON l.id = j.location_id
GROUP BY l.id, l.city, l.country, l.latitude, l.longitude, j.year, j.role;

-- View: Top Skills pro Beruf
CREATE OR REPLACE VIEW v_top_skills_per_role AS
SELECT
    j.role,
    j.year,
    s.name as skill,
    COUNT(*) as count
FROM jobs j
JOIN job_skills js ON j.id = js.job_id
JOIN skills s ON js.skill_id = s.id
WHERE j.role IS NOT NULL
GROUP BY j.role, j.year, s.name
ORDER BY j.role, j.year, count DESC;

-- =====================================================
-- 7. FUNCTIONS (Stored Procedures)
-- =====================================================

-- Function: Get Geo-Heatmap Data
CREATE OR REPLACE FUNCTION get_geo_heatmap(
    p_year INTEGER DEFAULT NULL,
    p_role VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    location VARCHAR,
    lat DECIMAL,
    lon DECIMAL,
    country VARCHAR,
    count BIGINT,
    color VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.city::VARCHAR,
        l.latitude,
        l.longitude,
        l.country::VARCHAR,
        COUNT(j.id)::BIGINT,
        CASE
            WHEN COUNT(j.id) > 1000 THEN '#e74c3c'
            WHEN COUNT(j.id) > 500 THEN '#e67e22'
            WHEN COUNT(j.id) > 200 THEN '#f39c12'
            ELSE '#27ae60'
        END::VARCHAR as color
    FROM locations l
    LEFT JOIN jobs j ON l.id = j.location_id
    WHERE (p_year IS NULL OR j.year = p_year)
      AND (p_role IS NULL OR j.role = p_role)
    GROUP BY l.city, l.latitude, l.longitude, l.country
    HAVING COUNT(j.id) > 0
    ORDER BY COUNT(j.id) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get Top Skills for Role
CREATE OR REPLACE FUNCTION get_top_skills(
    p_role VARCHAR,
    p_year INTEGER DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    skill VARCHAR,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.name::VARCHAR,
        COUNT(*)::BIGINT
    FROM jobs j
    JOIN job_skills js ON j.id = js.job_id
    JOIN skills s ON js.skill_id = s.id
    WHERE j.role = p_role
      AND (p_year IS NULL OR j.year = p_year)
    GROUP BY s.name
    ORDER BY COUNT(*) DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. SAMPLE DATA (für Testing)
-- =====================================================

-- Sample Jobs (2020-2025)
DO $$
DECLARE
    v_location_id INTEGER;
    v_job_id UUID;
    v_skill_id INTEGER;
    v_year INTEGER;
    v_role VARCHAR;
BEGIN
    -- Loop durch Jahre und Rollen
    FOR v_year IN 2020..2025 LOOP
        FOREACH v_role IN ARRAY ARRAY['Software Developer', 'Data Scientist', 'DevOps Engineer', 'Project Manager', 'UI/UX Designer'] LOOP
            -- 50-100 Jobs pro Jahr/Rolle
            FOR i IN 1..(50 + (RANDOM() * 50)::INT) LOOP
                -- Zufällige Location
                SELECT id INTO v_location_id FROM locations WHERE city != 'Remote' ORDER BY RANDOM() LIMIT 1;

                -- Job einfügen
                INSERT INTO jobs (title, role, location_id, posted_at, source)
                VALUES (
                    v_role || ' (' || v_year || ')',
                    v_role,
                    v_location_id,
                    (v_year || '-' || (1 + FLOOR(RANDOM() * 12))::INT || '-' || (1 + FLOOR(RANDOM() * 28))::INT)::DATE,
                    'sample_data'
                )
                RETURNING id INTO v_job_id;

                -- 3-7 zufällige Skills pro Job
                FOR j IN 1..(3 + FLOOR(RANDOM() * 5)::INT) LOOP
                    SELECT id INTO v_skill_id FROM skills ORDER BY RANDOM() LIMIT 1;
                    INSERT INTO job_skills (job_id, skill_id, confidence)
                    VALUES (v_job_id, v_skill_id, 0.8 + (RANDOM() * 0.2))
                    ON CONFLICT DO NOTHING;
                END LOOP;
            END LOOP;
        END LOOP;
    END LOOP;
END $$;

-- =====================================================
-- 9. PERFORMANCE INDEXES
-- =====================================================

-- Composite Indexes für häufige Queries
CREATE INDEX idx_jobs_year_role ON jobs(year, role);
CREATE INDEX idx_jobs_location_year ON jobs(location_id, year);

-- =====================================================
-- 10. GRANTS (Optional: für verschiedene User)
-- =====================================================

-- Readonly User für Dashboard
-- CREATE USER dashboard_reader WITH PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE jobmining TO dashboard_reader;
-- GRANT USAGE ON SCHEMA public TO dashboard_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO dashboard_reader;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO dashboard_reader;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check Data
SELECT 'Locations', COUNT(*) FROM locations
UNION ALL
SELECT 'Jobs', COUNT(*) FROM jobs
UNION ALL
SELECT 'Skills', COUNT(*) FROM skills
UNION ALL
SELECT 'Job_Skills', COUNT(*) FROM job_skills;

-- Test Function
SELECT * FROM get_geo_heatmap(2025, 'Software Developer');
SELECT * FROM get_top_skills('Data Scientist', 2024, 10);
