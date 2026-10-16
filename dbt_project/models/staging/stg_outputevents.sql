select * from {{ source('mimiciv_icu', 'outputevents') }}
