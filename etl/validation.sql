-- ==============================================================================
-- VALIDATION.SQL
-- ==============================================================================

-- ==============================================================================
-- VALIDATION.SQL (Final Production Copy)
-- ==============================================================================

-- 1. Create temporary, sampled tables instantly to bypass slow dbt view logic
CREATE TEMPORARY TABLE temp_cond AS SELECT condition_concept_id FROM gold.condition_occurrence LIMIT 10000;
CREATE TEMPORARY TABLE temp_drug AS SELECT drug_concept_id FROM gold.drug_exposure LIMIT 10000;

-- 2. Execute the rapid validation metrics matrix with aligned data types
SELECT 'gold.person vs mimiciv.patients' AS check_name, 
       (SELECT COUNT(*) FROM gold.person)::DOUBLE AS metric_a,
       (SELECT COUNT(*) FROM mimiciv.patients)::DOUBLE AS metric_b
UNION ALL
SELECT 'gold.visit_occurrence baseline rowcount' AS check_name, 
       (SELECT COUNT(*) FROM gold.visit_occurrence)::DOUBLE AS metric_a,
       2922008.0 AS metric_b -- Aligned to match decimal/double output
UNION ALL
SELECT 'Condition Concept 0 Rate (Should be < 30%)' AS check_name,
       (SELECT COUNT(CASE WHEN condition_concept_id = 0 THEN 1 END) * 100.0 / COUNT(*) FROM temp_cond)::DOUBLE AS metric_a,
       30.0 AS metric_b
UNION ALL
SELECT 'Drug Concept 0 Rate (Should be < 30%)' AS check_name,
       (SELECT COUNT(CASE WHEN drug_concept_id = 0 THEN 1 END) * 100.0 / COUNT(*) FROM temp_drug)::DOUBLE AS metric_a,
       30.0 AS metric_b;
