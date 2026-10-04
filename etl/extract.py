import os
import subprocess
import time

# ==============================================================================
# CONFIGURATIONS (FULL MIMIC-IV v3.1 CREDENTIALED EXTRACT VIA NATIVE WGET)
# ==============================================================================
PHYSIONET_USER = "maye2026"   
PHYSIONET_PASS = "xxxx"       

# Target output directory
LOCAL_DOWNLOAD_DIR = r"C:\PythonProjects\data"
os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)

def run_wget_extract():
    print("==================================================================")
    print("PIPELINE PHASE: NATIVE WGET EXTRACTOR (MIMIC-IV v3.1 FULL)")
    print("==================================================================")
    print(f"Target Directory : {LOCAL_DOWNLOAD_DIR}")
    print("==================================================================\n")
    
    start_time = time.time()
    
    # Official absolute URL tree
    target_url = "https://physionet.org/files/mimiciv/3.1/"
    
    # Constructing the exact parameters from the PhysioNet documentation
    # -r (recursive), -np (no parent), -c (continue partial downloads)
    # --directory-prefix maps it directly to your C drive project data space
    wget_command = [
        "wget",
        "-r",
        "-N",
        "-c",
        "-np",
        f"--user={PHYSIONET_USER}",
        f"--password={PHYSIONET_PASS}",
        f"--directory-prefix={LOCAL_DOWNLOAD_DIR}",
        "--no-check-certificate",
        target_url
    ]
    
    try:
        print("Launching background network stream process...")
        
        # Popen pipes the live network download logs straight to the console
        process = subprocess.Popen(
            wget_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True
        )
        
        # Read and display the real-time download status streams
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                cleaned_line = line.strip()
                if cleaned_line:
                    print(f"[WGET STREAM] {cleaned_line}")
                    
        return_code = process.poll()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, wget_command)
            
        print("\n==================================================================")
        print("EXTRACT COMPLETE: All version 3.1 streams successfully landed.")
        print(f"Total Pipeline Runtime: {(time.time() - start_time) / 60:.2f} minutes")
        print("==================================================================")
        
    except Exception as error:
        print(f"\nExtraction Step Failed: {str(error)}")
        raise error

if __name__ == "__main__":
    run_wget_extract()
