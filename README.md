# MIMIC-IV 3.1 Clinical Pipeline

A fully automated, Dockerised ELT pipeline that transforms raw MIMIC-IV clinical data into an OMOP CDM Gold layer using DuckDB and dbt. Processes 1.3 billion rows across MIMIC-IV and Athena vocabulary into a single 74GB DuckDB file on a 16GB RAM machine via DuckDB memory tuning.

> **Scope:** MIMIC-IV core modules only (hosp + icu). MIMIC-CXR (radiology images) and MIMIC-IV-Note (NLP/discharge summaries) are not included.

---

## What It Does

1. Checks if MIMIC-IV data already exists locally — skips download if so
2. Optionally downloads MIMIC-IV from PhysioNet via AWS S3 (approximately 2 minutes)
3. Loads all MIMIC-IV CSV.gz files into DuckDB under the `mimiciv` schema (approximately 10 minutes)
4. Loads OHDSI Athena vocabulary into DuckDB under the `athena` schema (approximately 50 seconds)
5. Runs 88 dbt models across Silver and Gold OMOP layers (approximately 36 mins)
6. Validates Gold OMOP tables using automated SQL data quality checks
7. Sends Slack notifications on success or failure

---

## Stack

| Component | Technology |
|---|---|
| Orchestration | Prefect 3.4 |
| Database | DuckDB 1.2.2 |
| Transformations | dbt-duckdb |
| OMOP Mappings | OHDSI Athena + CogStack custom mappings |
| Containerisation | Docker Compose |
| Notifications | Slack Webhook |

---

## Requirements

- 16GB RAM, 200GB+ free disk(~90GB for the data and database, plus ~110GB of breathing room for temp files and Docker during builds)
- Ubuntu / WSL2 on Windows
- Docker + Docker Compose
- PhysioNet credentialled access to MIMIC-IV
- AWS account linked to PhysioNet (for S3 download) — see `elt/AWS_PHYSIONET_SETUP.md`
- OHDSI Athena vocabulary bundle — see `elt/SETUP.md`

---

## Getting Started

This pipeline requires several prerequisites before `docker compose up` will work. Follow the setup guides in order:

1. [`elt/SETUP.md`](elt/SETUP.md) — Install dependencies, configure WSL2 memory, download Athena vocabulary and MIMIC-IV data
2. [`elt/AWS_PHYSIONET_SETUP.md`](elt/AWS_PHYSIONET_SETUP.md) — Link your AWS account to PhysioNet for fast S3 download (recommended)
3. [`elt/README.md`](elt/README.md) — Step reference, ingestion options, and tmux workflow for wget

Once all prerequisites are met:

```bash
git clone https://github.com/masabai/mimic-iv-3.1-clinical-pipeline.git
cd mimic-iv-3.1-clinical-pipeline
cp .env.example .env
# fill in .env — see elt/SETUP.md
docker compose up --build
```

> Everything after `docker compose up` is fully automated by the pipeline.

---

## Project Structure

```
mimic-iv-3.1-clinical-pipeline/
├── elt/                        # Pipeline steps (step1–step8)
│   ├── step1_check_existing_data.py
│   ├── step2_ingest_aws.py
│   ├── step3_check_download.py
│   ├── step4_verify_duckdb.py
│   ├── step5_build_mimic.py
│   ├── step6_build_athena.py
│   ├── step7_run_dbt.py
│   ├── step8_test_omop.py
│   ├── validation.sql          # Gold layer QA assertions
│   ├── README.md               # Step reference and ingestion options
│   ├── SETUP.md                # Full setup guide
│   └── AWS_PHYSIONET_SETUP.md  # AWS + PhysioNet handshake guide
├── flow/
│   ├── mimic_flow.py           # Prefect orchestration flow
│   └── notify_slack_channel.py # Slack notifications
├── dbt_project/                # dbt models (Silver, Gold)
│   └── models/
├── data/
│   ├── custom_mappings/        # 21 CogStack OMOP custom mapping CSVs
│   └── README.md               # Custom mappings reference
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── .env.example
```

---

## Pipeline Flow

```
docker compose up
       │
       ▼
[Step 1] Check if MIMIC-IV data exists at /data
       │ exists → skip download
       │ missing → [Step 2] Download from PhysioNet S3 via AWS CLI
       ▼
[Step 3] Pre-ingestion smoke checks (file count, SHA-256, column headers)
       ▼
[Step 4] Verify DuckDB — check if mimiciv + athena tables already loaded
       │ exists → skip build
       │ missing → [Step 5] Load MIMIC-IV CSV.gz → DuckDB mimiciv schema
       │           [Step 6] Load Athena vocab + custom mappings → athena schema
       ▼
[Step 7] Run dbt — build 88 models across Silver and Gold OMOP
       ▼
[Step 8] Validate Gold OMOP layer
       ▼
Slack notification — success or failure (skipped if SLACK_WEBHOOK_URL is not set)
```

**Orchestration Lifecycle — Step Ownership**

```
MIMIC-IV Orchestration Lifecycle
├── [MY SYSTEM]             Step 1: State Inspection (Local File Scan)
├── [MY SYSTEM]             Step 2: High-Performance AWS Cloud Ingestion
├── [MY SYSTEM]             Step 3: Pre-Ingestion Data Quality Smoke Tests
├── [MY SYSTEM]             Step 4: Database State & Table Volume Check
├── [COGSTACK — MODIFIED]   Step 5: Raw MIMIC-IV Schema Loader
├── [COGSTACK — MODIFIED]   Step 6: OHDSI Athena Vocabulary Schema Loader
├── [COGSTACK — PATCHED]    Step 7: 88-Model dbt Silver and Gold Transformations
└── [MY SYSTEM]             Step 8: Post-Build Relational Quality Assertions
```

> Steps 1, 2, 3, 4, and 8 are original work.
>
> Step 5 is derived from CogStack's [`load_mimic_to_duckdb.py`](https://github.com/CogStack/dbt_mimic_omop/blob/main/load_mimic_to_duckdb.py) — modified to add a DB config section and restructure the loader.
>
> Step 6 is derived from CogStack's [`load_vocabularies_to_duckdb.py`](https://github.com/CogStack/dbt_mimic_omop/blob/main/load_vocabularies_to_duckdb.py) — modified to add a pre-check before loading.
>
> Step 7 uses the CogStack dbt models with upstream bug fixes applied — 2 issues were raised and resolved. See [CogStack issues](https://github.com/CogStack/dbt_mimic_omop/issues/).

---

## Data Ingestion Options

**Recommended — AWS CLI (~2 minutes):**
Requires PhysioNet + AWS account handshake. See `elt/AWS_PHYSIONET_SETUP.md`.

**Alternative — wget (20+ hours):**
Use tmux to survive disconnects — see `elt/README.md` for the full tmux workflow.

**Manual browser download:**
Download from https://physionet.org/content/mimiciv/3.1/ and copy to `~/mimic/mimiciv_data/`.
Make sure `SHA256SUMS.txt` is included.

> If not using AWS CLI, comment out `run_step("step2_ingest_aws.py")` in `flow/mimic_flow.py` before running.

---

## Environment Variables

| Variable | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |
| `AWS_DEFAULT_REGION` | `us-east-1` |
| `BASE_S3_PATH` | PhysioNet S3 access point URL |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook (optional — leave blank to disable notifications) |

---

## Monitoring

- Prefect UI: http://localhost:4201
- Live logs: `docker compose logs -f`
- Slack alerts fire on task failure and pipeline completion

---

## References

- [MIMIC-IV](https://physionet.org/content/mimiciv/3.1/)
- [OHDSI Athena](https://athena.ohdsi.org)
- [CogStack dbt_mimic_omop](https://github.com/CogStack/dbt_mimic_omop)
  - 11 of 88 models failed on first run during development. Two issues were raised and fixed upstream — see [CogStack issues](https://github.com/CogStack/dbt_mimic_omop/issues/). These fixes are already applied in this pipeline.
- [dbt-duckdb](https://github.com/duckdb/dbt-duckdb)

---

## Citation

This pipeline builds on the dbt MIMIC-IV OMOP work by CogStack. If you use this pipeline in your research, please cite the original work:

```bibtex
@inproceedings{sutton2026fast,
  title={Fast, Accurate, and Local Conversion of MIMIC-IV to OMOP with DBT},
  author={Sutton, Adam and Moller-Grell, Niko and Searle, Thomas and Dobson, Richard},
  booktitle={BioNLP 2026},
  pages={992--996},
  year={2026}
}
```


