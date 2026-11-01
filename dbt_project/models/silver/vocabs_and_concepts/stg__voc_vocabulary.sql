select *
from {{ source('athena', 'VOCABULARY') }}
where vocabulary_concept_id < 2000000000
