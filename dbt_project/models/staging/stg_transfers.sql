select * from {{ source('mimiciv_hosp', 'transfers') }}
