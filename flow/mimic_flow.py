import time
import subprocess
from pathlib import Path
from prefect import flow, task


# ==============================================================================
# CONFIGURATION
# ==============================================================================

PROJECT_ROOT = Path(r"C:\PythonProject\mimic-demo")

PYTHON_EXE = (
    r"C:\Users\sawyn\AppData\Local\Programs\Python\Python311\python.exe"
)


# ==============================================================================
# CHECK DATA ALREADY DOWNLOADED
# ==============================================================================

@task(name="Step 1: Check MIMIC-IV data")
def check_ingestion():

    script_path = PROJECT_ROOT / "etl" / "step1_check_existing_data.py"

    result = subprocess.run(
        [PYTHON_EXE, str(script_path)],
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0


# ==============================================================================
# RUN STEPS
# ==============================================================================

@task
def run_step(script_name):
    script_path = PROJECT_ROOT / "etl" / script_name
    
    print(f"\n[PREFECT] Running {script_name}...")
    
    result = subprocess.run(
        [PYTHON_EXE, str(script_path)],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_name} failed with return code {result.returncode}"
        )

    print(f"[PREFECT] {script_name} completed.")


# ==============================================================================
# PIPELINE
# ==============================================================================

@flow(name="MIMIC-IV Clinical Pipeline")
def mimic_demo_pipeline():

    exists = check_ingestion()

    if exists:
        print("Data exists — skip extraction.")
    else:
        run_step("step2_extract_demo.py")

    run_step("step3_check_download_gx.py")
    run_step("step4_verify_schemas.py")
    run_step("step5_run_buildmimic_part1.py")
    run_step("step6_run_buildmimic_part2.py")
    print("\n[PREFECT] All steps completed successfully.")
    


# ==============================================================================
# RUN
# ==============================================================================

if __name__ == "__main__":
    
    try:
        
        start_time = time.perf_counter()
        print("Starting MIMIC-IV pipeline.......")
    
        mimic_demo_pipeline()
        
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        print(f"\nTotal Process Time to run pipeline: {hours}h {minutes}m {seconds}s")
    
    except Exception as err:
            print(f"\n[PIPELINE ERROR] Automation flow terminated unexpectedly:\n{err}")