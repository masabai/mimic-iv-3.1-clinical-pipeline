select * from {{ source('mimiciv_hosp', 'provider') }}
