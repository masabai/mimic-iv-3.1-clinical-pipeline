import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# CONFIGURATIONS
# ==============================================================================

PHYSIONET_USER = "maye2026"

BASE_URL = "https://physionet.org/files/mimiciv/3.1/"

LOCAL_DOWNLOAD_DIR = r"C:\PythonProjects\data"

CONCURRENCY_STREAMS = 8

FILES_TO_DOWNLOAD = [
    "hosp/d_labitems.csv.gz"
]
# ==============================================================================
# DOWNLOAD
# ==============================================================================

def download_file(remote_rel_path):

    remote_url = f"{BASE_URL.rstrip('/')}/{remote_rel_path}"

    local_file_path = os.path.join(
        LOCAL_DOWNLOAD_DIR,
        remote_rel_path.replace("/", os.sep)
    )

    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

    print(f"[START] Downloading: {remote_rel_path}")

    start = time.time()

    password = os.environ.get("PHYSIONET_PASS")

    if not password:
        print("[ERROR] PHYSIONET_PASS is not set.")
        return

    try:
        subprocess.run(
            [
                "wget.exe",
                "--user", PHYSIONET_USER,
                "--password", password,
                "-c",
                "-O", local_file_path,
                remote_url
            ],
            check=True
        )

        duration = time.time() - start

        print(
            f"[SUCCESS] Completed: {remote_rel_path} "
            f"in {duration / 60:.2f} minutes"
        )

    except subprocess.CalledProcessError as e:

        print(
            f"[ERROR] wget failed for {remote_rel_path} "
            f"(exit code {e.returncode})"
        )


# ==============================================================================
# PIPELINE
# ==============================================================================

def run_pipeline():

    print("==================================================================")
    print("PIPELINE PHASE: WGET CONCURRENT EXTRACTOR (MIMIC-IV v3.1)")
    print("==================================================================")
    print(f"Source Endpoint  : {BASE_URL}")
    print(f"Target Directory : {LOCAL_DOWNLOAD_DIR}")
    print(f"Parallel Workers : {CONCURRENCY_STREAMS}")
    print("Downloader       : wget.exe")
    print("==================================================================\n")

    start_time = time.time()

    with ThreadPoolExecutor(
        max_workers=CONCURRENCY_STREAMS
    ) as executor:

        list(
            executor.map(
                download_file,
                FILES_TO_DOWNLOAD
            )
        )

    print("\n==================================================================")
    print("EXTRACT COMPLETE: Ingestion downloads finished.")
    print(
        f"Total Pipeline Runtime: "
        f"{(time.time() - start_time) / 60:.2f} minutes"
    )
    print("==================================================================")


if __name__ == "__main__":
    run_pipeline()