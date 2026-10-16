select * from {{ source('mimiciv_icu', 'datetimeevents') }}
