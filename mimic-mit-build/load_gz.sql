-----------------------------------------
-- Load data into the MIMIC-IV schemas --
-----------------------------------------

-- To run from a terminal:
--  psql "dbname=mimiciv_testing user=postgres" -v mimic_data_dir=<PATH TO DATA DIR> -f load_gz.sql
\cd :mimic_data_dir

-- making sure that all tables are empty and correct encoding is defined -utf8- 
SET CLIENT_ENCODING TO 'utf8';

-- hosp schema
\cd hosp
\COPY mimiciv_hosp.admissions FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc admissions.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.d_hcpcs FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc d_hcpcs.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.diagnoses_icd FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc diagnoses_icd.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.d_icd_diagnoses FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc d_icd_diagnoses.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.d_icd_procedures FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc d_icd_procedures.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.d_labitems FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc d_labitems.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.drgcodes FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc drgcodes.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.emar_detail FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc emar_detail.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.emar FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc emar.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.hcpcsevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc hcpcsevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.labevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc labevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.microbiologyevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc microbiologyevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.omr FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc omr.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.patients FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc patients.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.pharmacy FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc pharmacy.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.poe_detail FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc poe_detail.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.poe FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc poe.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.prescriptions FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc prescriptions.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.procedures_icd FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc procedures_icd.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.provider FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc provider.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.services FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc services.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_hosp.transfers FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc transfers.csv.gz' DELIMITER ',' CSV HEADER NULL '';

-- icu schema
\cd ../icu

\COPY mimiciv_icu.caregiver FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc caregiver.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.chartevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc chartevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.datetimeevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc datetimeevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.d_items FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc d_items.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.icustays FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc icustays.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.ingredientevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc ingredientevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.inputevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc inputevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.outputevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc outputevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.procedureevents FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc procedureevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
