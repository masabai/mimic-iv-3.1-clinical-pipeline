import os
# pip install python-dotenv

#from dotenv import load_dotenv
import subprocess
import time
from pathlib import Path

# ==============================================================================
# CONFIGURATIONS (AUTOMATED INGESTION FLOW VIA MIT SHELL SCRIPT)
# ==============================================================================
PHYSIONET_USER = os.getenv("PHYSIONET_USER")
PHYSIONET_PASS = os.getenv("PHYSIONET_PASS")

# Path in Linux environment
LOCAL_DOWNLOAD_DIR = "/home/moesa/mimiciv_full/data"
MIT_SCRIPT_PATH = "/home/moesa/mimic/mimic-iv-3.1-clinical-pipeline/mimic-mit-build/download_data.sh"

os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)

def run_mit_shell_extract():
    print("==================================================================")
    print("PIPELINE PHASE: INGESTION VIA MIT LAB SHELL WRAPPER")
    print("==================================================================")
    
    # The MIT script usage requires: ./download_data.sh [destination] [username]
    # Pass Linux download directory and username directly to it.
    # Pass the password directly via standard input stream using echo
    ingest_command = [
        "bash", 
        MIT_SCRIPT_PATH, 
        LOCAL_DOWNLOAD_DIR, 
        PHYSIONET_USER
    ]
    
    try:
        print("Launching MIT shell script process...")
        
        # Password into the environment variables so wget can find it natively,
        # or it will prompt cleanly in the stream.
        process_env = os.environ.copy()
        process_env["PHYSIONET_USER"] = PHYSIONET_USER
        process_env["WGET_PASSWORD"] = PHYSIONET_PASS

        
        # Popen pipes the live network download logs straight to the console
        process = subprocess.Popen(
            ingest_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, # Block stdin interference entirely
            text=True,
            bufsize=1,
            shell=False,
            env=process_env
        )
        
        # Read and display the real-time download status streams
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                cleaned_line = line.strip()
                if cleaned_line:
                    print(f"[MIT SCRIPT STREAM] {cleaned_line}")
                    
        return_code = process.poll()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, ingest_command)
            
        print("\n==================================================================")
        print("EXTRACT COMPLETE")
        print("==================================================================")
        
    except Exception as error:
        print(f"\nExtraction Step Failed: {str(error)}")
        raise error

if __name__ == "__main__":
    start_time = time.perf_counter()
    print("Starting ingestion flow.......")
    
    run_mit_shell_extract()        
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"\nTotal time to ingest: {elapsed_time:.2f} seconds")
