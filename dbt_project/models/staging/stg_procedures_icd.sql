select * from {{ source('mimiciv_hosp', 'procedures_icd') }}
