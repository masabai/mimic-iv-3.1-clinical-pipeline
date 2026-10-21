import os
import subprocess
from pathlib import Path

PHYSIONET_USER = os.getenv("PHYSIONET_USER")
PHYSIONET_PASS = os.getenv("PHYSIONET_PASS")

# Portable container/WSL data paths
LOCAL_DOWNLOAD_DIR = Path("/home/moesa/mimiciv_full/data")
MIT_SCRIPT_PATH = Path("/home/moesa/mimic/mimic-iv-3.1-clinical-pipeline/mimic-mit-build/download_data.sh")

def check_existing_data():
    """Checks if the MIMIC-IV dataset is already present in the folder structure."""
    hosp_path = LOCAL_DOWNLOAD_DIR / "hosp"
    icu_path = LOCAL_DOWNLOAD_DIR / "icu"
    
    # Count how many compressed data tables exist in the target subfolders
    if hosp_path.exists() and icu_path.exists():
        file_count = len(list(hosp_path.glob("*.csv.gz"))) + len(list(icu_path.glob("*.csv.gz")))
        if file_count >= 34:
            print(f"[SKIP] Found {file_count} dataset files safely organized on disk. Skipping download phase entirely.")
            return True
            
    print("[INGESTION NEEDED] Data structure incomplete. Preparing hands-free download...")
    return False

def run_automated_ingest():
    if check_existing_data():
        return # Exit cleanly and let Prefect fire up the Postgres load layer next
        
    LOCAL_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    ingest_command = [
        "bash", 
        str(MIT_SCRIPT_PATH), 
        str(LOCAL_DOWNLOAD_DIR), 
        PHYSIONET_USER
    ]
    
    process_env = os.environ.copy()
    process_env["PHYSIONET_USER"] = PHYSIONET_USER
    process_env["WGET_PASSWORD"] = PHYSIONET_PASS # Read natively by wget without stdin crashing
    
    process = subprocess.Popen(
        ingest_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, # Safe, non-blocking standard input
        text=True,
        bufsize=1,
        shell=False,
        env=process_env
    )
    
    # Stream live download metrics to your pipeline console
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(f"[AUTOMATED INGEST] {line.strip()}")
            
    if process.poll() != 0:
        raise RuntimeError("PhysioNet download engine failed.")

if __name__ == "__main__":
    run_automated_ingest()
