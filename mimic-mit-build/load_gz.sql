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
\COPY mimiciv_hosp.provider FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc provider.csv.gz' DELIMITER ',' CSV HEADER NULL '';

-- icu schema
\cd ../icu

\COPY mimiciv_icu.d_items FROM PROGRAM '"C:\Program Files\Git\usr\bin\gzip.exe" -dc d_items.csv.gz' DELIMITER ',' CSV HEADER NULL '';
