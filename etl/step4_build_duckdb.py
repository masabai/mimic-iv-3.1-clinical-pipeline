import subprocess
import sys
import time
from pathlib import Path

MIMIC_DATA_DIR = "/data"
MIMIC_DB       = "/duckdb/mimic4.db"
BUILD_SCRIPT   = "/app/mimic-code/mimic-iv/buildmimic/duckdb/build_mimic.sh"


def run_build_duckdb():
    start_time = time.perf_counter()

    print(f"[STEP 4] Building DuckDB from {MIMIC_DATA_DIR} into {MIMIC_DB}...")

    result = subprocess.run(
        ["bash", BUILD_SCRIPT, MIMIC_DATA_DIR, MIMIC_DB],
        cwd=Path(BUILD_SCRIPT).parent
    )

    elapsed = time.perf_counter() - start_time
    h, m, s = int(elapsed // 3600), int((elapsed % 3600) // 60), int(elapsed % 60)

    if result.returncode == 0:
        print(f"[STEP 4] PASS — DuckDB build complete: {MIMIC_DB}")
    else:
        print(f"[STEP 4] FAIL — return code {result.returncode}")

    print(f"[STEP 4] Time: {h}h {m}m {s}s")
    return result.returncode == 0


if __name__ == "__main__":
    success = run_build_duckdb()
    sys.exit(0 if success else 1)
