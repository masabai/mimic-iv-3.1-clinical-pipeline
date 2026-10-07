from pathlib import Path


# ==============================================================================
# CONFIGURATION — LOCAL DATA PATH
# ==============================================================================
LOCAL_DOWNLOAD_DIR = Path(r"C:\mimiciv_full\data")

# ==============================================================================
# STEP 1 — CHECK TARGET DATA DIRECTORIES
# ==============================================================================

def check_ingestion():
    """Check whether MIMIC-IV hosp and icu data directories exist."""

    hosp_path = LOCAL_DOWNLOAD_DIR / "physionet.org/files/mimiciv/3.1/hosp"
    icu_path = LOCAL_DOWNLOAD_DIR / "physionet.org/files/mimiciv/3.1/icu"

    if hosp_path.exists() and icu_path.exists():
        print(f"[STEP 1] MIMIC-IV data detected at: {LOCAL_DOWNLOAD_DIR}")
        print(f"[STEP 1] hosp: {hosp_path}")
        print(f"[STEP 1] icu:  {icu_path}")
        print("[STEP 1] PASS: Extraction phase can be skipped.")
        return True

    print("[STEP 1] MIMIC-IV data directories are missing.")
    print(f"[STEP 1] Expected: {hosp_path}")
    print(f"[STEP 1] Expected: {icu_path}")
    return False


if __name__ == "__main__":
    check_ingestion()