from pathlib import Path


# ==============================================================================
# CONFIGURATION
# ==============================================================================
LOCAL_DOWNLOAD_DIR = Path("/data")   # mapped from /home/moesa/mimiciv_data in docker-compose


# ==============================================================================
# STEP 1 — CHECK DATA DIRECTORIES EXIST
# ==============================================================================
def check_ingestion():
    hosp_path = LOCAL_DOWNLOAD_DIR / "hosp"
    icu_path  = LOCAL_DOWNLOAD_DIR / "icu"

    hosp_ok = hosp_path.exists() and any(hosp_path.iterdir())
    icu_ok  = icu_path.exists()  and any(icu_path.iterdir())

    if hosp_ok and icu_ok:
        print(f"[STEP 1] PASS — data found at {LOCAL_DOWNLOAD_DIR}")
        print(f"[STEP 1] hosp: {hosp_path}")
        print(f"[STEP 1] icu:  {icu_path}")
        return True

    print("[STEP 1] FAIL — hosp or icu directory missing or empty")
    print(f"[STEP 1] Expected: {hosp_path}")
    print(f"[STEP 1] Expected: {icu_path}")
    return False


if __name__ == "__main__":
    check_ingestion()
