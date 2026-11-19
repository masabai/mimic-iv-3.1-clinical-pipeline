"""Step 1: Checks that MIMIC-IV hosp/ and icu/ data directories exist and are non-empty at /data."""
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
LOCAL_DOWNLOAD_DIR = Path("/data")   # mapped from /home/moesa/mimiciv_data in docker-compose

# ==============================================================================
# STEP 1 — CHECK DATA DIRECTORIES EXIST
# ==============================================================================
def check_ingestion() -> bool:
    hosp_path = LOCAL_DOWNLOAD_DIR / "hosp"
    icu_path  = LOCAL_DOWNLOAD_DIR / "icu"

    # 1. Check directories first (fail fast if either folder is missing)
    if not (hosp_path.is_dir() and icu_path.is_dir()):
        print("[STEP 1: CHECK EXISTING DATA] FAIL — hosp or icu directory missing")
        return False

    # 2. Only scan files once if both directories exist
    hosp_files = [f for f in hosp_path.glob("*.csv*") if f.stat().st_size > 0]
    icu_files  = [f for f in icu_path.glob("*.csv*") if f.stat().st_size > 0]

    if len(hosp_files) >= 22 and len(icu_files) >= 9:
        print(f"[STEP 1: CHECK EXISTING DATA] PASS — data found at {LOCAL_DOWNLOAD_DIR}")
        return True
    

    print(f"[STEP 1: CHECK EXISTING DATA] FAIL — incomplete files (hosp: {len(hosp_files)}/22, icu: {len(icu_files)}/9)")
    return False

if __name__ == "__main__":
    check_ingestion()
