select * from {{ source('mimiciv_icu', 'inputevents') }}
