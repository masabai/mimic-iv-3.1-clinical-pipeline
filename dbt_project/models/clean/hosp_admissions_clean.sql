-- models/clean/hosp_admissions_clean.sql
{{ config(materialized='table') }}

SELECT
    hadm_id,
    subject_id,
    admittime,
    dischtime,
    deathtime,
    TRIM(admission_type) AS admission_type,
    TRIM(admission_location) AS admission_location,
    TRIM(discharge_location) AS discharge_location,
    TRIM(insurance) AS insurance,
    TRIM(language) AS language,
    TRIM(marital_status) AS marital_status,
    TRIM(race) AS race,
    hospital_expire_flag,
    
    -- Add a new column: custom data audit flag (Boolean logic)
    CASE 
        WHEN dischtime > admittime THEN TRUE 
        ELSE FALSE 
    END AS is_valid_chronology

FROM {{ ref('stg_admissions') }}
