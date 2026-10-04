import subprocess
import time
from pathlib import Path

# ==============================================================================
# CONFIGURATION — PIPELINE DATA PATHS
# ==============================================================================
# The root folders: 'hosp' and 'icu' subdirectories
LOCAL_DOWNLOAD_DIR = Path(r"C:\PythonProjects\data\mimic-iv-3.1")
MIT_BUILD_DIR = Path(r"C:\PythonProjects\mimic-clinical-pipeline\mimic-mit-build")

CREATE_SQL_PATH = MIT_BUILD_DIR / "create.sql"
LOAD_GZ_SQL_PATH = MIT_BUILD_DIR / "load_gz.sql"

PSQL_SYSTEM_EXE = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"
TARGET_DB = "mimiciv_testing"

# ==============================================================================
# RUN SEQUENTIAL TARGET LOAD PHASE
# ==============================================================================
def run_standalone_load():
    # Capture start time of the entire migration pipeline
    start_time = time.perf_counter()

    
    # STEP 1: CREATE DATABASE SCHEMAS AND TABLES
    print(f"[LOADER] Step 1: Generating empty schema targets via {CREATE_SQL_PATH.name}...")
    create_command = f'set PGPASSWORD=123&& "{PSQL_SYSTEM_EXE}" -X -U postgres -d {TARGET_DB} -f "{CREATE_SQL_PATH}"'
    
    create_result = subprocess.run(create_command, capture_output=True, text=True, shell=True)
    if create_result.returncode != 0:
        print(f"❌ Schema creation failed!\nError Log:\n{create_result.stderr}")
        return False
    print("[LOADER] Empty schemas built.")

    # STEP 2: SEQUENTIAL PAUSE
    print("\n[LOADER] Pausing sequence for 15 seconds to allow structural changes to settle...")
    time.sleep(15)

    # STEP 3: EXECUTE MIT-LAB SCRIPT AND PASS VARIABLE
    print(f"\n[LOADER] Step 2: Executing MIT-Lab data load script: {LOAD_GZ_SQL_PATH.name}...")
    
    # Convert path backslashes to double-escaped format so \cd works natively on Windows
    escaped_data_dir = str(LOCAL_DOWNLOAD_DIR).replace('\\', '\\\\')
    
    # FIX: Replaced .as_posix() with the escaped Windows string representation
    load_command = (
        f'set PGPASSWORD=123&& '
        f'"{PSQL_SYSTEM_EXE}" -X -e -U postgres -d {TARGET_DB} '
        f'-v mimic_data_dir="{escaped_data_dir}" '
        f'-f "{LOAD_GZ_SQL_PATH}"'
    )

    print(f"[LOADER] Launching process with background variables...")
    
    # Pass the working directory so relative file commands resolve instantly
    load_result = subprocess.run(
        load_command, 
        shell=True,
        cwd=LOCAL_DOWNLOAD_DIR
    )
    
    end_time = time.perf_counter()

    # Output the exact response logs from psql
    print("\nDatabase Engine Execution Output:")
    print(load_result.stdout)
    
    
    # Check return code and ensure stderr actually exists before searching it
    if load_result.returncode != 0 or (load_result.stderr and "ERROR:" in load_result.stderr):
        print(f"❌ Ingestion phase failed!\nError Log:\n{load_result.stderr}")
        return False
    
    print("\n Build and data loading phases completed.")
        
    
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    print(f"\nTotal Process Time: {hours}h {minutes}m {seconds}s")

    return True

if __name__ == "__main__":
    run_standalone_load()
