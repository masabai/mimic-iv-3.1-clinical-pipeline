# ETL Pipeline — Step Reference

All steps are orchestrated automatically by `flow/mimic_flow.py` via Prefect after `docker compose up`.

> See `setup_linux.md` for pre-requisites before running `docker compose up --build`.

---

## Pre-Docker Checklist

# Requirement
MIMIC-IV data (`hosp/`, `icu/`) +`SHA256SUMS.txt`  ===>  `~/mimic/mimiciv_data/` 

Athena vocabulary ZIP =====> `~/mimic/athena_vocab/` 
.env` filled in | project root |

---

## Pipeline Steps

### `step1_check_existing_data.py`
Checks whether `hosp/` and `icu/` directories exist and are non-empty at `/data`.
Returns `True` to skip ingestion, `False` to trigger download.

---

### `step2_ingest_aws.py`
Downloads MIMIC-IV from PhysioNet via AWS S3 and syncs `hosp/`, `icu/`, and `SHA256SUMS.txt` into `/data`.
Requires `BASE_S3_PATH`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` in `.env`.

> See `aws_physionet_setup.md` for the AWS + PhysioNet handshake setup.

**⚠️ Strongly recommended over all other methods.** AWS CLI completes in ~2 minutes at full network speed with negligible cost (~$0.01), provided your IAM user is in `us-east-1` — the same region as the PhysioNet S3 bucket.

**Alternative — manual browser download or wget:**
```bash
wget -r -N -c -np --user <PhysioNet_username> --ask-password \
     -P ~/mimic/mimiciv_data/ \
     https://physionet.org/files/mimiciv/3.1/
```

> Manual download or wget: ~21–22 hrs at 40–50 KB/s (PhysioNet transfer rate, September 2025).
> wget can degrade to 6–20 KB/s during peak hours — observed to take 7+ days without completing.

---

### `step3_check_download_gx.py`
Pre-ingestion smoke checks *(currently commented out in flow)*:
1. File count — expects 22 `hosp` + 9 `icu` files
2. SHA-256 hash verification against `SHA256SUMS.txt`
3. Column header extraction — saves schema snapshot to `etl/validation/landing_zone_schema_snapshot.json`

---

### `step4_verify_duckdb.py`
Checks whether DuckDB already contains all expected `mimiciv` and `athena` tables.
Returns `True` to skip rebuild, `False` to trigger `step5` and `step6`.

---

### `step5_build_mimic.py` (~10 mins)
Loads all MIMIC-IV `.csv.gz` files from `/data` into DuckDB under the `mimiciv` schema.
Memory tuned for 16GB RAM: `5GB limit`, `2 threads`, temp spill to `/duckdb/duckdb_temp`.

---

### `step6_build_athena.py`
Loads OHDSI Athena vocabulary files (CSV and ZIP) from `/athena` into DuckDB under the `athena` schema.
Also loads custom OMOP mappings from `data/custom_mappings/`.

---

### `step7_run_dbt.py` (~50 mins)
Runs dbt transformations across Bronze → Silver → Gold OMOP layers.
Builds 88 models targeting the `dbt_project/` directory using the `dev` profile.

---

### `step8_test_omop.py`
Runs post-transformation QA assertions from `etl/validation.sql` against the Gold OMOP layer.
Checks row counts and vocabulary mapping failure rates.
Exits with code `1` if any assertion fails.
