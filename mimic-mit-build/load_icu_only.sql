-------------------------------------------------------------------------
-- Load data ONLY into the MIMIC-IV ICU schema (Modified)
-------------------------------------------------------------------------

\cd :mimic_data_dir

SET CLIENT_ENCODING TO 'utf8';

-- Go straight to the icu schema folder
\cd icu

-- Commented out below in case the file is missing from your directory. 
-- If you find caregiver.csv.gz later, remove the '--' from the line below and re-run.
-- \COPY mimiciv_icu.caregiver FROM PROGRAM 'gzip -dc caregiver.csv.gz' DELIMITER ',' CSV HEADER NULL '';

-- Massive ICU event tables start here
\COPY mimiciv_icu.chartevents FROM PROGRAM 'gzip -dc chartevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.datetimeevents FROM PROGRAM 'gzip -dc datetimeevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.d_items FROM PROGRAM 'gzip -dc d_items.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.icustays FROM PROGRAM 'gzip -dc icustays.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.ingredientevents FROM PROGRAM 'gzip -dc ingredientevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.inputevents FROM PROGRAM 'gzip -dc inputevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.outputevents FROM PROGRAM 'gzip -dc outputevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
\COPY mimiciv_icu.procedureevents FROM PROGRAM 'gzip -dc procedureevents.csv.gz' DELIMITER ',' CSV HEADER NULL '';
