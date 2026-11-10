-- ==============================================================================
-- VALIDATION.SQL — Post-dbt OMOP Gold Layer QA
-- Checks row counts, concept mapping rates, referential integrity, and date logic.
-- ==============================================================================

-- Random sample to avoid full scans on large tables (296M+ rows)
CREATE TEMPORARY TABLE temp_cond AS SELECT condition_concept_id FROM gold.condition_occurrence USING SAMPLE 10000 ROWS;
CREATE TEMPORARY TABLE temp_drug AS SELECT drug_concept_id FROM gold.drug_exposure USING SAMPLE 10000 ROWS;

-- Person count must match source patients exactly (catches data loss)
SELECT 'gold.person vs mimiciv.patients' AS check_name,
       (SELECT COUNT(*) FROM gold.person)::DOUBLE AS metric_a,
       (SELECT COUNT(*) FROM mimiciv.patients)::DOUBLE AS metric_b

-- Concept mapping failure rates on sampled data (threshold: < 30%)
UNION ALL
SELECT 'Condition Concept 0 Rate (Should be < 30%)' AS check_name,
       (SELECT COUNT(CASE WHEN condition_concept_id = 0 THEN 1 END) * 100.0 / COUNT(*) FROM temp_cond)::DOUBLE AS metric_a,
       30.0 AS metric_b
UNION ALL
SELECT 'Drug Concept 0 Rate (Should be < 30%)' AS check_name,
       (SELECT COUNT(CASE WHEN drug_concept_id = 0 THEN 1 END) * 100.0 / COUNT(*) FROM temp_drug)::DOUBLE AS metric_a,
       30.0 AS metric_b

-- Vocabulary join integrity: non-zero concept_ids must resolve to a concept_name
UNION ALL
SELECT 'Vocabulary Null concept_name violations (must be 0)' AS check_name,
       (SELECT COUNT(*) FROM gold.condition_occurrence co
        LEFT JOIN gold.concept c ON co.condition_concept_id = c.concept_id
        WHERE co.condition_concept_id != 0 AND c.concept_name IS NULL)::DOUBLE AS metric_a,
       0.0 AS metric_b

-- Vocabulary join integrity: non-zero drug concept_ids must resolve to a concept_name

UNION ALL
SELECT 'Drug Vocabulary Null concept_name violations (must be 0)' AS check_name,
       (
           SELECT COUNT(*)
           FROM gold.drug_exposure de
           LEFT JOIN gold.concept c
               ON de.drug_concept_id = c.concept_id
           WHERE de.drug_concept_id != 0
             AND c.concept_id IS NULL
       )::DOUBLE AS metric_a,
       0.0 AS metric_b

-- Chronological integrity: visit start must not be after visit end
UNION ALL
SELECT 'Date Range violations in visit_occurrence (must be 0)' AS check_name,
       (SELECT COUNT(*) FROM gold.visit_occurrence
        WHERE visit_start_date > visit_end_date)::DOUBLE AS metric_a,
       0.0 AS metric_b

-- Referential integrity: every condition must link to a valid person
UNION ALL
SELECT 'Orphaned condition_occurrence records (must be 0)' AS check_name,
    COUNT(co.person_id)::DOUBLE AS metric_a,
    0.0 AS metric_b
FROM gold.condition_occurrence co
LEFT JOIN gold.person p ON co.person_id = p.person_id
WHERE p.person_id IS NULL;
