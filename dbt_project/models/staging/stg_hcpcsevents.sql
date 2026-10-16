select * from {{ source('mimiciv_hosp', 'hcpcsevents') }}
