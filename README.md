# Clinical Data Engineering & Research Pipeline: Cardiovascular Health & Lipid Profiles

## Project Overview
Exploring a large, real-world clinical dataset out of curiosity and a research initiative designed to analyze cardiovascular outcomes relative to body mass index (BMI), blood pressure, blood glucose control, and lipid panels (evaluating the online debate surrounding "low fat vs high fat" ).

**Also using it as a personal laboratory** to understand what happens when working with hundreds of thousands or millions of records—from memory and loading limits to query performance, indexing, and discovering interesting patterns in cardiovascular and lipid-related data.

---

## Project Objectives

### 1. Medical Research & Clinical Analysis
*   **Evaluate Online Dietary Debates:** Dig into a real-world clinical database to test online health claims regarding low-fat vs. high-fat diets, tracking how LDL changes independently versus how it changes alongside broader lipid profiles (Triglycerides, HDL, and Total Cholesterol ratios).

*   **Cohort Cross-Referencing:** Isolate patients with heart/cardiac diagnoses and track their corresponding biometric indicators, analyzing health metrics specifically for patients with out-of-range BMIs.
*   **Targeted Clinical Metric Mapping:**
    *   **Cardiovascular:** Blood Pressure (BP) medications and diagnostic codes.
    *   **Metabolic:** A1c medications and glucose markers.
    *   **Biometrics:** BMI categories (filtering for custom < 18.5 or > 24.5 thresholds).
    *   **Lipids:** Complete lipid profiles (LDL, HDL, Triglycerides).

### 2. Infrastructure & Big Data Engineering
*   **Scale Testing Environment:** Build and optimize a containerized workflow capable of scaling from local demo environments to the full clinical database.
*   **Modern Workspace Containerization:** Deploy a modular local environment using Docker to securely manage memory configuration and isolate database services.
*   **Pipeline Orchestration:** Implement Apache Airflow to handle data ingestion and scheduling, managing worker concurrency configurations locally to prevent out-of-memory (OOM) errors.

### 3. Database Performance & Analytics
*   **Query Optimization:** Practice strategic performance tuning, indexing strategy execution, and database optimization techniques on high-volume tables (e.g., OMR and Lab Events).
*   **Execution Auditing:** Utilize query execution plans (`EXPLAIN ANALYZE`) to ensure efficient indexing and eliminate expensive sequential scans on large datasets.

### 4. Data Quality & Transformation
*   **Modular Modeling:** Leverage `dbt` (data build tool) to split complex clinical database schemas into clean, isolated intermediate views for systematic categorical analysis.
*   **Automated Data Validation:** Implement automated data quality frameworks (`Great Expectations` or `Soda Core`) to perform range checks, programmatically catching and filtering out extreme data entry errors (e.g., typos like a 4649.4 BMI).

### 5. Advanced Interfaces (Future Milestone)
*   **Natural Language to SQL:** Build a lightweight text-to-SQL interface using an LLM framework to easily query patient demographics and lipid trends using natural language rather than manual SQL strings.
