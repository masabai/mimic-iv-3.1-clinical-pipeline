select * from {{ source('mimiciv_hosp', 'omr') }}
