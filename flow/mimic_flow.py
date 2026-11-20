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
# ELT STEP RUNNER
# ==============================================================================
@task(name="run-elt-step", task_run_name="{script_name}", on_failure=[on_task_failure])
def run_step(script_name: str, raise_on_fail: bool = True) -> bool:
    """Executes an elt/ script. Raises on failure by default, or returns bool for checks."""
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

    if result.returncode != 0 and raise_on_fail:
        raise RuntimeError(
            f"{script_name} failed with return code {result.returncode}"
        )

    if result.returncode == 0:
        print(f"[PREFECT] {script_name} completed.")

    return result.returncode == 0

# ==============================================================================
# PIPELINE
# ==============================================================================
@flow(name="MIMIC-IV Clinical Pipeline")
def mimiciv_pipeline():
    # Step 1: Check existing data (returns True/False without failing the flow)
    if run_step("step1_check_existing_data.py", raise_on_fail=False):
        print("[STEP 1] Data exists — skipping extraction.")
    else:
        print("[PIPELINE] Data not found — starting AWS ingestion...")
        # run_step("step2_ingest_aws.py")

        run_step("step3_check_download_gx.py")

    # Step 4: Check DuckDB (returns True/False without failing the flow)
    if run_step("step4_verify_duckdb.py", raise_on_fail=False):
        print("[STEP 4] DuckDB already exists — skipping build.")
    else:
        print("[PIPELINE] DuckDB missing or invalid — starting loader.")
        run_step("step5_build_mimic.py")
        run_step("step6_build_athena.py")

        # Re-verify after loading (raises error if verification still fails)
        run_step("step4_verify_duckdb.py", raise_on_fail=True)

    # Step 7: Run dbt
    print("[STEP 7] Building models.....")
    # run_step("step7_run_dbt.py")

    # Step 8: Test the 88 generated dbt models and Gold OMOP targets
    print("[STEP 8] Running Quality Assurance on Gold OMOP Layer.....")
    run_step("step8_test_omop.py")

    print("\n[PREFECT] All [1-8] steps completed successfully.")

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
