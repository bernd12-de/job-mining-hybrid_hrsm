-- V4__insert_job_role_mappings.sql
-- FÜGT DIE DOMÄNENREGELN FÜR DAS JOB-ROLE-MAPPING HINZU (Role Service)

-- Wir definieren den RULE_TYPE 'ROLE_MAPPING'
-- rule_key: Die klassifizierte Rolle (Resultat, z.B. 'Software-Entwicklung')
-- rule_value: Das Regex-Muster, das in den Titeln/im Text gesucht wird

INSERT INTO domain_rule (rule_type, rule_key, rule_value) VALUES
                                                              ('ROLE_MAPPING', 'Software-Entwicklung', 'Entwickler|Developer|Programmierer|Coding|Frontend|Backend|Full-Stack|DevOps'),
                                                              ('ROLE_MAPPING', 'UX & Design', 'UX|User Experience|Usability|UI|Interaction Design|Designer|Researcher|Usability Expert|UX Specialist'),
                                                              ('ROLE_MAPPING', 'Data & Analytics', 'Data Scientist|Analyst|BI|Business Intelligence|Statistik|KI|Machine Learning'),
                                                              ('ROLE_MAPPING', 'Projektmanagement', 'Projektleiter|Projektmanager|PMO|Scrum Master|Product Owner|Agile Coach'),
                                                              ('ROLE_MAPPING', 'Führungskraft/Management', 'Leiter|Manager|Head of|Geschäftsführer|CFO|CTO'),
                                                              ('ROLE_MAPPING', 'Vertrieb & Beratung', 'Vertrieb|Consultant|Berater|Account Manager|Sales'),
                                                              ('ROLE_MAPPING', 'Administrativ/Support', 'Assistent|Sekretär|Kauffrau|Admin');
