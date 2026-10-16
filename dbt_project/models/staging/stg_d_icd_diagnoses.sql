select * from {{ source('mimiciv_hosp', 'd_icd_diagnoses') }}
