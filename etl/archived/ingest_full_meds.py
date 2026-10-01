import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# ARCHIVED --- LOAD OK , TRANSFORMATION PART NOT NEEDED
 

def run_resilient_ingestion():
    output_dir = Path(r"C:\mimiciv_raw")
    
    python_scripts_path = Path(sys.executable).parent / "Scripts"
    executable_engine = python_scripts_path / "meds-extract-run.exe"
    
    os.environ["DATASET_DOWNLOAD_USERNAME"] = "xxxxxx"
    os.environ["DATASET_DOWNLOAD_PASSWORD"] = "xxxxxx"
    os.environ["PHYSIONET_USER"] = "your_real_username"
    os.environ["PHYSIONET_PASSWORD"] = "your_real_password"
    
    command_args = [
        str(executable_engine),
        "spec=MIMIC-IV",
        f"output_dir={output_dir}",
        "download_concurrency=4"  # Dropped from 8 to 4 to reduce server-side connection drops
    ]
    
    start_timestamp = time.time()
    print("🚀 INGESTION STEP INITIATED...")
    sys.stdout.flush()
    
    attempt = 1
    while True:
        print(f"\n🔄 Launching Ingestion Run (Attempt #{attempt})...")
        sys.stdout.flush()
        
        process = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read logs to keep the buffer clear and check for true completion
        for line in iter(process.stdout.readline, ""):
            print(f"[ENGINE LOG]: {line.strip()}")
            sys.stdout.flush()
            
        process.wait()
        
        # If it finished with 0, the entire dataset is 100% complete
        if process.returncode == 0:
            print("\n🎉 ALL FILES DOWNLOADED SUCCESSFULLY!")
            break
            
        # If it failed (exit code 1), it hit a server drop. Wait and retry.
        print(f"\n⚠️ Ingestion run interrupted by server throttle. Cooling down for 15 seconds...")
        sys.stdout.flush()
        time.sleep(15)
        attempt += 1

    # Final Runtime Metrics
    end_timestamp = time.time()
    total_seconds = int(end_timestamp - start_timestamp)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print("\n" + "=" * 60)
    print(f"⏱️ Total Execution Duration: {hours:02d} hours, {minutes:02d} minutes, {seconds:02d} seconds")
    print("=" * 60)

if __name__ == "__main__":
    run_resilient_ingestion()
