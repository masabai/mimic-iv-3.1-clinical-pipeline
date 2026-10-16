select * from {{ source('mimiciv_hosp', 'diagnoses_icd') }}
