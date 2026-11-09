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

-- Core clinical table row counts (must be > 0)
UNION ALL
SELECT 'gold.visit_occurrence row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.visit_occurrence)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.condition_occurrence row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.condition_occurrence)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.drug_exposure row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.drug_exposure)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.measurement row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.measurement)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.observation row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.observation)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.procedure_occurrence row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.procedure_occurrence)::DOUBLE AS metric_a, 0.0 AS metric_b

-- Athena vocabulary tables loaded from /athena (must be > 0)
UNION ALL
SELECT 'gold.concept row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.concept)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.concept_relationship row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.concept_relationship)::DOUBLE AS metric_a, 0.0 AS metric_b
UNION ALL
SELECT 'gold.vocabulary row count vs 0' AS check_name,
       (SELECT COUNT(*) FROM gold.vocabulary)::DOUBLE AS metric_a, 0.0 AS metric_b

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
