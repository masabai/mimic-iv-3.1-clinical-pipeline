select * from {{ source('mimiciv_hosp', 'poe_detail') }}
