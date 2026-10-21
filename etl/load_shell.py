import subprocess
import time
from pathlib import Path

# ==============================================================================
# CONFIGURATION — PIPELINE DATA PATHS (Maintained from your original logic!)
# ==============================================================================
MIT_BUILD_DIR = Path("/home/moesa/mimic/mimic-iv-3.1-clinical-pipeline")
CREATE_SQL_PATH = MIT_BUILD_DIR / "create.sql"
LOAD_GZ_SQL_PATH = MIT_BUILD_DIR / "load_gz.sql"

TARGET_DB = "mimiciv_testing"

def run_standalone_load():
    start_time = time.perf_counter()

    # STEP 1: CREATE DATABASE SCHEMAS AND TABLES
    print(f"[LOADER] Step 1: Generating empty schema targets via {CREATE_SQL_PATH.name}...")
    
    # Updated Command: We use Docker's internal psql engine directly in your container network!
    create_command = f'docker exec -i mimic_postgres psql -U postgres -d {TARGET_DB}'
    
    with open(CREATE_SQL_PATH, "r") as f:
        create_result = subprocess.run(create_command, stdin=f, capture_output=True, text=True, shell=True)
        
    if create_result.returncode != 0:
        print(f"❌ Schema creation failed!\nError Log:\n{create_result.stderr}")
        return False
    print("[LOADER] Empty schemas built.")

    # STEP 2: SEQUENTIAL PAUSE (Your brilliant safety mechanism kept intact!)
    print("\n[LOADER] Pausing sequence for 15 seconds to allow structural changes to settle...")
    time.sleep(15)

    # STEP 3: EXECUTE MIT-LAB SCRIPT AND PASS VARIABLE
    print(f"\n[LOADER] Step 2: Executing MIT-Lab data load script: {LOAD_GZ_SQL_PATH.name}...")
    
    # Inside the container, the data directory is always exactly "/landing_zone" due to your compose mount
    container_data_dir = "/landing_zone"
    
    # Updated Command: Pass the variables inside the container space cleanly
    load_command = f'docker exec -i mimic_postgres psql -U postgres -d {TARGET_DB} -v mimic_data_dir="{container_data_dir}"'

    print(f"[LOADER] Launching process with background variables...")
    
    with open(LOAD_GZ_SQL_PATH, "r") as f:
        load_result = subprocess.run(load_command, stdin=f, capture_output=True, text=True, shell=True)
    
    end_time = time.perf_counter()

    print("\nDatabase Engine Execution Output:")
    print(load_result.stdout)
    
    if load_result.returncode != 0:
        print(f"❌ Ingestion phase failed!\nError Log:\n{load_result.stderr}")
        return False
    
    print("\nBuild and data loading phases completed.")
    return True

if __name__ == "__main__":
    run_standalone_load()
