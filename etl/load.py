import subprocess
import time
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
LOCAL_DOWNLOAD_DIR = Path(r"C:\data\mimic-iv-3.1")
MIT_BUILD_DIR = Path(r"C:\PythonProjects\mimic-clinical-pipeline\mimic-mit-build")

CREATE_SQL_PATH = MIT_BUILD_DIR / "create.sql"
LOAD_GZ_SQL_PATH = MIT_BUILD_DIR / "load_gz.sql"

PSQL_SYSTEM_EXE = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"
TARGET_DB = "mimiciv_testing"

# ==============================================================================
# EXECUTION SEQUENCE
# ==============================================================================
def run_standalone_load():
    # 1. CREATE SCHEMA & TABLES STEP
    print(f"[LOADER] Step 1: Creating empty database schemas and tables from {CREATE_SQL_PATH.name}...")
    create_command = f'set PGPASSWORD=123&& "{PSQL_SYSTEM_EXE}" -X -U postgres -d {TARGET_DB} -f "{CREATE_SQL_PATH}"'
    
    create_result = subprocess.run(create_command, capture_output=True, text=True, shell=True)
    
    if create_result.returncode != 0:
        print(f"❌ Schema creation failed!\nError Log:\n{create_result.stderr}")
        return False
    print("[LOADER] Tables created successfully.")

    # 2. SEQUENTIAL BREAK (Cool-down block)
    print("\n[LOADER] Pausing sequence for 15 seconds to allow structural changes to settle...")
    time.sleep(15)

    # 3. BULK DATA INGESTION STEP
    print(f"\n[LOADER] Step 2: Starting bulk data ingestion from {LOAD_GZ_SQL_PATH.name}...")
    load_command = (
        f'set PGPASSWORD=123&& '
        f'"{PSQL_SYSTEM_EXE}" -X -U postgres -d {TARGET_DB} '
        f'-v mimic_data_dir="{LOCAL_DOWNLOAD_DIR.as_posix()}" '
        f'-f "{LOAD_GZ_SQL_PATH}"'
    )
    
    load_result = subprocess.run(load_command, capture_output=True, text=True, shell=True)
    
    if load_result.returncode != 0:
        print(f"❌ Ingestion failed!\nError Log:\n{load_result.stderr}")
        return False
    
    print("[LOADER] Ingestion step complete. Output details:")
    print(load_result.stdout)
    print("\n🎉 Build and data loading phases completed cleanly.")
    return True

if __name__ == "__main__":
    run_standalone_load()
