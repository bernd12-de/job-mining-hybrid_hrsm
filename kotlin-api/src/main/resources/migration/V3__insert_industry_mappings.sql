-- V3__insert_industry_mappings.sql
-- FÜGT DIE DOMÄNENREGELN FÜR DAS INDUSTRY-MAPPING HINZU (Organization Service)

-- Wir definieren den RULE_TYPE 'INDUSTRY_MAPPING'
-- rule_key: Der Name der Branche (Resultat)
-- rule_value: Das Regex-Muster, das in der Stellenanzeige gesucht wird

INSERT INTO domain_rule (rule_type, rule_key, rule_value) VALUES
                                                              ('INDUSTRY_MAPPING', 'Informationstechnologie & Software', 'IT|Software|Entwicklung|DevOps|Cloud|Informatik|Digitalisierung'),
                                                              ('INDUSTRY_MAPPING', 'Finanzen & Versicherungen', 'Finanz|Bank|Versicherung|Aktie|Treasury|Bilanz'),
                                                              ('INDUSTRY_MAPPING', 'Automobil & Maschinenbau', 'Automobil|Maschinenbau|Fertigung|Produktion|Anlage|Konstruktion'),
                                                              ('INDUSTRY_MAPPING', 'Gesundheit & Soziales', 'Klinik|Pflege|Sozial|Heim|Therapie|Krankenhaus'),
                                                              ('INDUSTRY_MAPPING', 'Handel & Logistik', 'Handel|Logistik|Einzelhandel|Lager|Supply Chain'),
                                                              ('INDUSTRY_MAPPING', 'Unbekannt/Generell', 'Marketing|Vertrieb|Verwaltung|Assistenz');
