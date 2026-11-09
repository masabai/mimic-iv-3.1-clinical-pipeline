"""Prefect flow orchestrating the full MIMIC-IV pipeline: ingest → load → dbt → QA."""
import subprocess
from pathlib import Path
from prefect import flow, task
from notify_slack_channel import send_slack, on_task_failure

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PROJECT_ROOT = Path("/app")
LOCAL_DOWNLOAD_DIR = "/data"
PYTHON_EXE = "python3"

DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"
DBT_PROFILES_DIR = DBT_PROJECT_DIR

# ==============================================================================
# CHECK DATA ALREADY DOWNLOADED
# ==============================================================================
@task(name="Step 1: Check MIMIC-IV data", on_failure=[on_task_failure])
def check_ingestion():
    """Returns True if hosp/ and icu/ data already exists at /data, skipping download."""
    script_path = PROJECT_ROOT / "elt" / "step1_check_existing_data.py"

    result = subprocess.run(
        [PYTHON_EXE, str(script_path)],
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0

# ==============================================================================
# CHECK Database
# ==============================================================================
@task(name="Step 4: Check Duckdb loaded", on_failure=[on_task_failure])
def verify_duckdb():
    """Returns True if DuckDB already contains all expected mimiciv and athena tables."""
    script_path = PROJECT_ROOT / "elt" / "step4_verify_duckdb.py"

    print("\n[PIPELINE] Checking if DuckDB is valid...")
    result = subprocess.run(
        [PYTHON_EXE, str(script_path)],
        cwd=PROJECT_ROOT
    )
    return result.returncode == 0

# ==============================================================================
# RUN ELT STEPS
# ==============================================================================
@task(on_failure=[on_task_failure], task_run_name="{script_name}")
def run_step(script_name):
    """Executes a single elt/ script as a subprocess and raises on non-zero exit code."""
    script_path = PROJECT_ROOT / "elt" / script_name

    print(f"\n[PREFECT] Running {script_name}...")

    result = subprocess.run(
        [PYTHON_EXE, str(script_path)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_name} failed with return code "
            f"{result.returncode}"
        )

    print(f"[PREFECT] {script_name} completed.")

# ==============================================================================
# PIPELINE
# ==============================================================================
@flow(name="MIMIC-IV Clinical Pipeline")
def mimiciv_pipeline():
        
    if check_ingestion():
        print("Data exists — skip extraction.")
    else:
        print("[PIPELINE] Data not found — starting AWS ingestion...")
        run_step("step2_ingest_aws.py")

    run_step("step3_check_download_gx.py")
    
    if verify_duckdb():
        print("[STEP 4] DuckDB already exists — skipping build.")
        run_step("step4_verify_duckdb.py")
    else:
        print("[PIPELINE] DuckDB missing or invalid — starting loader.")
        run_step("step5_build_mimic.py")
        run_step("step6_build_athena.py")
        
        # Verify the database after loading.
        run_step("step4_verify_duckdb.py")
    
    # run dbt
    print("[STEP 7] Building models.....")
    run_step("step7_run_dbt.py")
    
    # NEW STEP: Test the 88 generated dbt models and Gold OMOP targets
    print("[STEP 8] Running Quality Assurance on Gold OMOP Layer.....")
    run_step("step8_test_omop.py")
        
    
    print("\n[PREFECT] All steps completed successfully.")

# ==============================================================================
# RUN
# ==============================================================================
if __name__ == "__main__":
    try:
        print("Starting MIMIC-IV pipeline...")
        
        mimiciv_pipeline()
        send_slack(":large_green_circle: *MIMIC-IV Pipeline — All Steps Passed* :white_check_mark:")
        
    except Exception as err:
        send_slack(f":rotating_light: *MIMIC Pipeline — Pipeline Crashed*\n```{err}```")
        print(f"\n[PIPELINE ERROR] Automation flow terminated unexpectedly:\n{err}")
        raise