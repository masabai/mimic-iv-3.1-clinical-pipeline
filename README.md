# MIMIC-IV 3.1 Clinical Pipeline

A fully automated, Dockerised ELT pipeline that transforms raw MIMIC-IV clinical data into a queryable OMOP CDM Gold layer using DuckDB and dbt.

---

## What It Does

1. Checks if MIMIC-IV data already exists locally — skips download if so
2. Optionally downloads MIMIC-IV from PhysioNet via AWS S3 (approximately 2 minutes)
3. Loads all MIMIC-IV CSV.gz files into DuckDB under the `mimiciv` schema
4. Loads OHDSI Athena vocabulary into DuckDB under the `athena` schema
5. Runs 88 dbt models across Bronze → Silver → Gold OMOP layers (~50 mins)
6. Runs post-build QA assertions against the Gold OMOP layer
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

- 16GB RAM, 200GB+ free disk
- Ubuntu / WSL2 on Windows
- Docker + Docker Compose
- PhysioNet credentialled access to MIMIC-IV
- AWS account linked to PhysioNet (for S3 download) — see `elt/AWS_PHYSIONET_SETUP.md`
- OHDSI Athena vocabulary bundle — see `elt/SETUP.md`

---

## Quick Start

```bash
git clone https://github.com/masabai/mimic-iv-3.1-clinical-pipeline.git
cd mimic-iv-3.1-clinical-pipeline
cp .env.example .env
# fill in .env with your AWS credentials and Slack webhook
docker compose up --build
```

> Everything after `docker compose up` is fully automated by the pipeline.

---

## Pre-Docker Checklist

| Requirement | Location |
|---|---|
| MIMIC-IV data (`hosp/`, `icu/`, `SHA256SUMS.txt`) | `~/mimic/mimiciv_data/` |
| Athena vocabulary ZIP | `~/mimic/athena_vocab/` |
| `.env` filled in | project root |

> Rename `.env.example` → `.env` before starting. See `elt/SETUP.md` for full setup instructions.

---

## Project Structure

```
mimic-iv-3.1-clinical-pipeline/
├── elt/                        # Pipeline steps (step1–step8)
│   ├── step1_check_existing_data.py
│   ├── step2_ingest_aws.py
│   ├── step3_check_download_gx.py
│   ├── step4_verify_duckdb.py
│   ├── step5_build_mimic.py
│   ├── step6_build_athena.py
│   ├── step7_run_dbt.py
│   ├── step8_test_omop.py
│   ├── validation.sql          # Gold layer QA assertions
│   ├── SETUP.md                # Full setup guide
│   └── AWS_PHYSIONET_SETUP.md  # AWS + PhysioNet handshake guide
├── flow/
│   ├── mimic_flow.py           # Prefect orchestration flow
│   └── notify_slack_channel.py # Slack notifications
├── dbt_project/                # dbt models (Bronze → Silver → Gold)
│   └── models/
├── data/
│   └── custom_mappings/        # 21 CogStack OMOP custom mapping CSVs
├── docker-compose.yml
├── Dockerfile
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
[Step 7] Run dbt — build 88 models across Bronze → Silver → Gold OMOP
       ▼
[Step 8] QA assertions on Gold OMOP layer
       ▼
Slack notification — success or failure
```

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
| `SLACK_WEBHOOK_URL` | Slack incoming webhook (optional) |

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
- [dbt-duckdb](https://github.com/duckdb/dbt-duckdb)
