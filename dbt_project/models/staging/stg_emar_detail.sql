select * from {{ source('mimiciv_hosp', 'emar_detail') }}
