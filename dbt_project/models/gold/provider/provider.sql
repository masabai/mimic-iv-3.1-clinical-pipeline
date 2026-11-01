
{% set relationship_sources = [
    ref("stg__provider"),
    ref("stg__caregiver"),
] %}

{% for rel in relationship_sources %}
    SELECT
        hash(provider_id) AS provider_id,
        CAST(NULL AS VARCHAR(255)) AS provider_name,
        CAST(NULL AS VARCHAR(20)) AS npi,
        CAST(NULL AS VARCHAR(20)) AS dea,
        CAST(NULL AS INTEGER) AS specialty_concept_id,
        CAST(NULL AS INTEGER) AS care_site_id,
        CAST(NULL AS INTEGER) AS year_of_birth,
        CAST(NULL AS INTEGER) AS gender_concept_id,
        CAST(provider_id AS VARCHAR(50)) AS provider_source_value,
        CAST(NULL AS VARCHAR(50)) AS specialty_source_value,
        CAST(NULL AS INTEGER) AS specialty_source_concept_id,
        CAST(NULL AS VARCHAR(50)) AS gender_source_value,
        CAST(NULL AS INTEGER) AS gender_source_concept_id
    FROM
        {{ rel }}

    {% if not loop.last %}
        UNION ALL
    {% endif %}
{% endfor %}
