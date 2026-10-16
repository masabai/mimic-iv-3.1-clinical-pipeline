select * from {{ source('mimiciv_hosp', 'drgcodes') }}
