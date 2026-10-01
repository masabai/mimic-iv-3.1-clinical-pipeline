import os
import time
from concurrent.futures import ThreadPoolExecutor
import requests

# ==============================================================================
# CONFIGURATIONS (PRODUCTION PYTHON MULTI-THREADED EXTRACT)
# ==============================================================================
PHYSIONET_USER = "maye2026"
PHYSIONET_PASS = os.environ.get("PHYSIONET_PASS")#, "xxxxxxxx")  # Replace with real password if not in env

LOCAL_DOWNLOAD_DIR = r"C:\PythonProjects\data"
TARGET_MODULES = ["hosp", "icu"]

# Pull 8 files concurrently to maximize network bandwidth safely
MAX_WORKERS = 8


def get_remote_file_list():
    """Fetches the official file map directly from the PhysioNet REST API."""
    print("[ETL] Requesting manifest from official PhysioNet API mapping...")
    file_urls = []
    
    # Official API endpoint for looking up dataset maps safely
    api_url = "https://physionet.org"
    
    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Walk through the official manifest payload
            for item in data.get("files", []):
                path = item.get("path", "")
                # Only extract files belonging to our targeted ETL modules (hosp/icu)
                if any(path.startswith(f"{module}/") for module in TARGET_MODULES):
                    # Ensure we are skipping folder references and only taking data files
                    if path.endswith(('.csv.gz', '.parquet', '.json', '.txt', '.gz')):
                        file_urls.append(f"https://physionet.org{path}")
        else:
            print(f"[ERROR] API lookup failed with HTTP status code: {response.status_code}")
            
    except Exception as e:
        print(f"[CRITICAL] Could not reach PhysioNet API catalog endpoint: {e}")
            
    print(f"[ETL] Discovered {len(file_urls)} valid files ready for extraction mapping.")
    return file_urls


def download_file_native(file_url):
    """Downloads a single data asset streaming it directly to disk storage."""
    filename = file_url.split("/")[-1]
    # Dynamically extract whether it belongs to hosp or icu folder structures
    subfolder = "hosp" if "/hosp/" in file_url else "icu"
    
    # Keep the exact directory tree structured identically to PhysioNet
    target_dir = os.path.join(LOCAL_DOWNLOAD_DIR, "physionet.org", "files", "mimiciv", "3.1", subfolder)
    os.makedirs(target_dir, exist_ok=True)
    local_path = os.path.join(target_dir, filename)

    # ETL Idempotency Rule: Skip files already fully localized on disk
    if os.path.exists(local_path):
        if os.path.getsize(local_path) > 0:
            print(f"[SKIPPED] {subfolder}/{filename} (Asset already exists)")
            return True

    try:
        # stream=True keeps memory footprints tiny during automated cron execution
        with requests.get(file_url, auth=(PHYSIONET_USER, PHYSIONET_PASS), stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=16384): # Increased block size to 16KB for better disk write execution
                    if chunk:
                        f.write(chunk)
        print(f"[DOWNLOADED] {subfolder}/{filename}")
        return True
    except Exception as e:
        print(f"[FAILED] {filename} - Network Connection Error: {e}")
        # Clean up stale partial download files so it retries cleanly on the next run
        if os.path.exists(local_path):
            try: os.remove(local_path)
            except: pass
        return False


def run_pipeline_extract():
    start_time = time.time()
    print("==================================================================")
    print("PIPELINE PHASE: PURE PYTHON MULTI-THREADED EXTRACT (MIMIC-IV v3.1)")
    print("==================================================================")
    
    # 1. Fetch data file urls directly from API
    urls = get_remote_file_list()
    if not urls:
        print("[CRITICAL] Extraction terminated: No target manifest assets mapped.")
        return

    # 2. Run the multi-threaded extraction pool
    print(f"[ETL] Initializing concurrent workers (Total Workers: {MAX_WORKERS})...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(download_file_native, urls))

    # 3. Pipeline Run Summary Output
    elapsed_minutes = (time.time() - start_time) / 60
    print("\n==================================================================")
    print("ETL EXTRACT STEP COMPLETED")
    print(f"Total Pipeline Runtime: {elapsed_minutes:.2f} minutes")
    print(f"Success Rate: {sum(results)}/{len(urls)} files extracted successfully.")
    print("==================================================================")


if __name__ == "__main__":
    run_pipeline_extract()
