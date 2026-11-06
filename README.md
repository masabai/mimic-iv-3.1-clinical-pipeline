# Clinical Data Engineering & Research Pipeline: Cardiovascular Health & Lipid Profiles

## Project Overview
Exploring a large, real-world clinical dataset out of curiosity and a research initiative designed to analyze cardiovascular outcomes relative to body mass index (BMI), blood pressure, blood glucose control, and lipid panels (evaluating the online debate surrounding "low fat vs high fat" ).

**Also using it as a personal laboratory** to understand what happens when working with hundreds of thousands or millions of records—from memory and loading limits to query performance, indexing, and discovering interesting patterns in cardiovascular and lipid-related data.

---

## Quick Start

### Prerequisites
- Ubuntu
- Docker & Docker Compose
- Git

```bash
sudo apt update && sudo apt install -y git docker.io docker-compose unzip
sudo usermod -aG docker $USER && newgrp docker

git clone https://github.com/<your-github-username>/mimic-iv-3.1-clinical-pipeline.git
cd mimic-iv-3.1-clinical-pipeline
docker compose up --build
```

> See `misc/setup_linux.md` for the full step-by-step guide.

---

## Data Ingestion

MIMIC-IV requires a PhysioNet account and data use approval: https://physionet.org

**Option 1: Manual (easiest — no AWS or CLI setup)**
Download from PhysioNet, place files in `~/mimiciv_data/` with `hosp/` and `icu/` subfolders.

**Option 2: AWS S3 (~2 mins)**
Requires AWS account + IAM + PhysioNet-AWS handshake. See `misc/ingest_awscli_setup.md`.

**Option 3: wget via PhysioNet (can take days)**
Requires PhysioNet credentials in `.env`. No AWS needed.

> Set `INGEST_METHOD=manual`, `aws`, or `wget` in `.env` to select method.

---

## Project Objectives

### Infrastructure & Big Data Engineering
*   **Scale Testing Environment:** Build and optimize a containerized workflow capable of scaling from local demo environments to the full clinical database.
*   **Modern Workspace Containerization:** Deploy a modular local environment using Docker to securely manage memory configuration and isolate database services.
*   **Pipeline Orchestration:** Implement Apache Airflow to handle data ingestion and scheduling, managing worker concurrency configurations locally to prevent out-of-memory (OOM) errors.

### Database Performance & Analytics

### Transformation

- Integrated an established CogStack MIMIC-IV-to-OMOP transformation framework.
- Implemented an end-to-end orchestration workflow.
- Implemented ingestion and schema validation components.
- Integrated vocabulary and clinical data loading.
- Executed post-transformation OMOP quality assurance.
- Evaluated and adopted optimized loading implementations.

