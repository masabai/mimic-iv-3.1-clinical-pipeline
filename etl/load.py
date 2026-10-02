import subprocess
import time
from pathlib import Path

# ==============================================================================
# CONFIGURATION — PIPELINE DATA PATHS
# ==============================================================================
# The root folder that CONTAINS your 'hosp' and 'icu' subdirectories
LOCAL_DOWNLOAD_DIR = Path(r"C:\PythonProjects\data")
# Update this to the exact folder on the server that holds the 'hosp' and 'icu' subdirectories
#LOCAL_DOWNLOAD_DIR = Path(r"C:\PythonProjects\data")

MIT_BUILD_DIR = Path(r"C:\PythonProjects\mimic-clinical-pipeline\mimic-mit-build")

CREATE_SQL_PATH = MIT_BUILD_DIR / "create.sql"
LOAD_GZ_SQL_PATH = MIT_BUILD_DIR / "load_gz.sql"

PSQL_SYSTEM_EXE = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"
TARGET_DB = "mimiciv_testing"

# ==============================================================================
# RUN SEQUENTIAL TARGET LOAD PHASE
# ==============================================================================
def run_standalone_load():
    # STEP 1: CREATE DATABASE SCHEMAS AND TABLES
    print(f"[LOADER] Step 1: Generating empty schema targets via {CREATE_SQL_PATH.name}...")
    create_command = f'set PGPASSWORD=123&& "{PSQL_SYSTEM_EXE}" -X -U postgres -d {TARGET_DB} -f "{CREATE_SQL_PATH}"'
    
    create_result = subprocess.run(create_command, capture_output=True, text=True, shell=True)
    if create_result.returncode != 0:
        print(f"❌ Schema creation failed!\nError Log:\n{create_result.stderr}")
        return False
    print("[LOADER] Empty schemas built cleanly.")

    # STEP 2: SEQUENTIAL COOL-DOWN PAUSE
    print("\n[LOADER] Pausing sequence for 15 seconds to allow structural changes to settle...")
    time.sleep(15)

    # STEP 3: EXECUTE MIT-LAB SCRIPT AND PASS VARIABLE
    print(f"\n[LOADER] Step 2: Executing official MIT data load script: {LOAD_GZ_SQL_PATH.name}...")
    
    # CRITICAL FIX: Convert path backslashes to double-escaped format so \cd works on Windows
    escaped_data_dir = str(LOCAL_DOWNLOAD_DIR).replace('\\', '\\\\')
    
    # We pass the exact variable matching the \cd :mimic_data_dir statement in the SQL file
 
     # Using .as_posix() ensures the path transfers cleanly as 'C:/PythonProjects/data'
    load_command = (
        f'set PGPASSWORD=123&& '
        f'"{PSQL_SYSTEM_EXE}" -X -U postgres -d {TARGET_DB} '
        f'-v mimic_data_dir="{LOCAL_DOWNLOAD_DIR.as_posix()}" '
        f'-f "{LOAD_GZ_SQL_PATH}"'
    )

 
 
    
    print(f"[LOADER] Launching process with background variables...")
    load_result = subprocess.run(load_command, capture_output=True, text=True, shell=True)
    
    # Output the exact response logs from psql
    print("\nDatabase Engine Execution Output:")
    print(load_result.stdout)
    
    if load_result.returncode != 0 or "ERROR:" in load_result.stderr:
        print(f"❌ Ingestion phase failed!\nError Log:\n{load_result.stderr}")
        return False
        
    print("\n🎉 Build and data loading phases completed cleanly.")
    return True

if __name__ == "__main__":
    run_standalone_load()
