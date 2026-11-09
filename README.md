
This project provides an automated, containerized orchestration layer for Sutton et al.'s dbt_mimic_omop pipeline (BioNLP 2026). It optimizes memory execution ceilings and mounts isolated thread paths to allow the full 100+ GB transformation to execute seamlessly on standard 16GB consumer laptops via Docker Desktop and Prefect."

### 🛡️ Data Governance & Schema Validity

To ensure the clinical accuracy of the final OMOP Common Data Model, this pipeline deliberately avoids custom, unverified SQL transformations. 

* **Logic Layer:** Reuses the peer-reviewed, medically validated dbt transformation logic from Sutton et al. (BioNLP 2026) to prevent inaccurate clinical concepts or corrupted concept mapping rates.
* **Platform Layer (My Contribution):** Engineered the end-to-end containerized automation wrapper (Docker + Prefect) required to ingest the 100+ GB raw dataset, resolve upstream multi-threaded DuckDB locks, scale down memory barriers to 6GB, and run automated QA data assertions.

## 🛠️ System Bottlenecks & Lessons Learned (Engineering Case Study)

Building an enterprise-scale clinical data warehouse over a 100+ GB footprint on consumer-grade hardware exposed severe real-world infrastructure constraints. Below is the documentation of how these bottlenecks were systematically engineered and resolved.

### 1. Overcoming Data Gravity: From a 7-Day Download Loop to 2 Minutes
* **The Bottleneck:** Attempting to extract the raw MIMIC-IV clinical dataset via standard public network protocols (`wget`) resulted in extreme traffic throttling, dropping transmission speeds down to a crippling 6–10 KB/s. The initial download loop sat active in a `tmux` session for 7 days without finishing.
* **The Solution:** Diagnosed cloud network topology and realized the source PhysioNet buckets share an identical cloud region (`us-east-1`) with AWS infrastructure. Developed an automated 15-minute credentialed authentication handshake using the AWS CLI. 
* **The Metric:** Bypassed the public internet bottleneck completely, utilizing AWS's internal fiber network to copy the entire 100+ GB dataset natively in **under 2 minutes** for a total cloud billing cost of **$0.01**.

### 2. Multi-Threaded Engine Collisions: Resolving DuckDB Temporary Path Locks
* **The Bottleneck:** When compiling heavy gold-layer analytical tables concurrently (`threads: 2`), the pipeline repeatedly threw a cryptic database engine error: `Not implemented Error: Cannot switch temporary directory after the current one has been used`. 
* **The Solution:** Identified an internal multi-threading connection race condition inside the `dbt-duckdb` adapter framework. When parallel database connections execute massive sorting operations simultaneously, subsequent threads attempt to re-declare the `temp_directory` path while active threads hold a hardware lock. Completely removed the rigid explicit path constraints from the configuration profile, allowing DuckDB to dynamically spin up isolated, hidden thread-swapping boundaries right next to the active `.db` file.

### 3. Evading the Linux OOM Killer: Optimizing Memory Ceilings
* **The Bottleneck:** Processing complex clinical logic models (such as `condition_era` and `drug_exposure`) across 323+ million rows caused extreme parallel memory utilization spikes. Because the local environment was a repurposed 16GB RAM laptop, the combined compute load frequently triggered the Linux Out-Of-Memory (OOM) Killer, silently terminating the Docker container mid-execution without throwing a dbt traceback.
* **The Solution:** Implemented strict memory bounding gates. Throttled the DuckDB engine cache layer configuration to a hard ceiling of `memory_limit: '6GB'` inside `profiles.yml`. 
* **The Metric:** This memory profile guarantees that even under maximum `threads: 2` concurrency, the database consumes a predictable 12GB max ceiling—leaving a clean 4GB buffer for Windows/WSL2 host operations and preventing silent engine crashes. The full 88-model transformation now finishes **100% hands-free in 55 minutes**.

### 💻 Infrastructure & Salvaged Hardware Setup
This entire clinical pipeline was built, tuned, and executed headless using an old, discarded gaming laptop left behind before moving out to college dorms (the lid hinge is completely broken and cannot close). 
* **Development Machine:** 8GB RAM / 100GB Disk Windows Laptop (Used purely as an thin SSH client terminal via VS Code Remote).
* **Target Compute Node (The Salvaged Server):** Wiped/Reset 16GB RAM / 900+ GB SSD Gaming Laptop running headless Docker Desktop over WSL2 Ubuntu. 

This environment proves that with proper infrastructure orchestration and precision resource constraints, enterprise health data informatics can be fully executed on a zero-dollar consumer hardware budget.

