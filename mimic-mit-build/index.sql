SELECT COUNT(DISTINCT subject_id) AS patients_with_I_codes
FROM mimiciv_hosp.diagnoses_icd
WHERE icd_version = 10
  AND icd_code LIKE 'I%';