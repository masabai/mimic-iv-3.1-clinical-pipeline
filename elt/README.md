# ELTPipeline — Step Reference

All steps are orchestrated automatically by `flow/mimic_flow.py` via Prefect after `docker compose up`.

> See `SETUP.md` for pre-requisites before running `docker compose up --build`.

---

## Pre-Docker Checklist

| Requirement | Location |
|---|---|
| MIMIC-IV data (`hosp/`, `icu/`, `SHA256SUMS.txt`) | `~/mimic/mimiciv_data/` |
| Athena vocabulary ZIP | `~/mimic/athena_vocab/` |
| `.env` filled in | project root |

> Rename `.env.example` → `.env` and fill in the required values before starting.

**Ingestion method:**
- This pipeline uses **AWS CLI** (`step2_ingest_aws.py`) to pull MIMIC-IV from PhysioNet's S3 bucket. Requires `BASE_S3_PATH`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` in `.env`.
- If you are **NOT** using AWS CLI (e.g. manual download or wget), comment out the `step2_ingest_aws.py` call in `flow/mimic_flow.py` before running `docker compose up` — otherwise the pipeline will attempt an AWS download and fail.

```python
# flow/mimic_flow.py  — comment this out if not using AWS:
# run_step("step2_ingest_aws.py")
```

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

**⚠️ Strongly recommended over all other methods.** AWS CLI completes in approximately 2 minutes at full network speed with negligible cost (around $0.01), provided your IAM user is in `us-east-1` — the same region as the PhysioNet S3 bucket.


> **September 2026:** stable at 40–50 KB/s, ~21–22 hrs total.
> **October 2026 onwards:** transfer rates dropped to 6–20 KB/s with frequent disconnects — 7+ days without completing. PhysioNet released several new datasets around this time which may have increased server load.


**Alternative — wget (manual, no AWS required):**

wget takes 20+ hrs at best. If your SSH session drops, the download dies. Use tmux to keep it alive across disconnects:

```bash
# 1. Start a persistent tmux session
tmux new -s mimic

# 2. Run wget inside it
wget -r -N -c -np --user <PhysioNet_username> --ask-password \
     -P ~/mimic/mimiciv_data/ \
     https://physionet.org/files/mimiciv/3.1/

# 3. Detach safely (session keeps running): Ctrl+B then D
# 4. Reattach later to check progress
tmux attach -t mimic
```

> `-N` skips already-downloaded files, `-c` resumes partial downloads — safe to re-run after a disconnect.

---

### `step3_check_download_gx.py`
Pre-ingestion smoke checks:
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
