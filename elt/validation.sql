
-- ==============================================================================
-- VALIDATION.SQL — Post-dbt OMOP Gold Layer QA
-- FULL-TABLE mapping rates and Gold layer integrity checks.
-- ==============================================================================

-- 1. Person count must match source patients exactly
SELECT 'gold.person vs mimiciv.patients' AS check_name,
       (SELECT COUNT(*) FROM gold.person)::DOUBLE AS metric_a,
       (SELECT COUNT(*) FROM mimiciv.patients)::DOUBLE AS metric_b

-- 2. FULL-TABLE condition concept 0 rate
UNION ALL
SELECT 'Condition Concept 0 Rate (FULL TABLE)' AS check_name,
       (
           SELECT
               COUNT(*) FILTER (WHERE condition_concept_id = 0)
               * 100.0 / NULLIF(COUNT(*), 0)
           FROM gold.condition_occurrence
       )::DOUBLE AS metric_a,
       30.0 AS metric_b

-- 3. FULL-TABLE drug concept 0 rate
UNION ALL
SELECT 'Drug Concept 0 Rate (FULL TABLE)' AS check_name,
       (
           SELECT
               COUNT(*) FILTER (WHERE drug_concept_id = 0)
               * 100.0 / NULLIF(COUNT(*), 0)
           FROM gold.drug_exposure
       )::DOUBLE AS metric_a,
       30.0 AS metric_b

-- 4. Condition vocabulary resolution
UNION ALL
SELECT 'Condition Vocabulary Missing concept IDs (must be 0)' AS check_name,
       (
           SELECT COUNT(*)
           FROM gold.condition_occurrence co
           LEFT JOIN gold.concept c
             ON co.condition_concept_id = c.concept_id
           WHERE co.condition_concept_id != 0
             AND c.concept_id IS NULL
       )::DOUBLE AS metric_a,
       0.0 AS metric_b

-- 5. Drug vocabulary resolution
UNION ALL
SELECT 'Drug Vocabulary Missing concept IDs (must be 0)' AS check_name,
       (
           SELECT COUNT(*)
           FROM gold.drug_exposure de
           LEFT JOIN gold.concept c
             ON de.drug_concept_id = c.concept_id
           WHERE de.drug_concept_id != 0
             AND c.concept_id IS NULL
       )::DOUBLE AS metric_a,
       0.0 AS metric_b

-- 6. Visit date-range integrity
UNION ALL
SELECT 'Date Range violations in visit_occurrence (must be 0)' AS check_name,
       (
           SELECT COUNT(*)
           FROM gold.visit_occurrence
           WHERE visit_start_date > visit_end_date
       )::DOUBLE AS metric_a,
       0.0 AS metric_b

-- 7. Condition records must link to a valid person
UNION ALL
SELECT 'Orphaned condition_occurrence records (must be 0)' AS check_name,
       COUNT(*)::DOUBLE AS metric_a,
       0.0 AS metric_b
FROM gold.condition_occurrence co
LEFT JOIN gold.person p
  ON co.person_id = p.person_id
WHERE p.person_id IS NULL;
