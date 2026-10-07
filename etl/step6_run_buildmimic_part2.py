import subprocess
import time
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

MIT_BUILD_DIR = Path(r"C:\PythonProjects\mimic-clinical-pipeline\mimic-mit-build")

INDEX_SQL_PATH = MIT_BUILD_DIR / "index.sql"
VALIDATE_SQL_PATH = MIT_BUILD_DIR / "validate.sql"

PSQL_SYSTEM_EXE = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"

TARGET_DB = "mimiciv_testing"


# ==============================================================================
# APPLY INDEX + VALIDATE
# ==============================================================================

def run_standalone_index_validate():

    start_time = time.perf_counter()

    # ==========================================================================
    # STEP 1: APPLY INDEX
    # ==========================================================================

    print(
        f"[LOADER] Step 1: Applying index script "
        f"{INDEX_SQL_PATH.name}..."
    )

    index_command = (
        f'set PGPASSWORD=123&& '
        f'"{PSQL_SYSTEM_EXE}" -X -v ON_ERROR_STOP=1 -h 10.0.0.21 '
        f'-U postgres -d {TARGET_DB} '
        f'-f "{INDEX_SQL_PATH}"'
    )

    index_result = subprocess.run(
        index_command,
        capture_output=True,
        text=True,
        shell=True
    )
    print("STDOUT:")
    print(index_result.stdout)

    print("STDERR:")
    print(index_result.stderr)

    if index_result.returncode != 0:
        print(f"❌ Index creation failed!\n{index_result.stderr}")
        return False

    print("[LOADER] Indexes applied.")

    # ==========================================================================
    # STEP 2: VALIDATE
    # ==========================================================================

    print(
        f"\n[LOADER] Step 2: Running validation "
        f"{VALIDATE_SQL_PATH.name}..."
    )

    validate_command = (
        f'set PGPASSWORD=123&& '
        f'"{PSQL_SYSTEM_EXE}" -X -e -h 10.0.0.21 '
        f'-U postgres -d {TARGET_DB} '
        f'-f "{VALIDATE_SQL_PATH}"'
    )

    validate_result = subprocess.run(
        validate_command,
        capture_output=True,
        text=True,
        shell=True
    )

    print("\nDatabase Validation Output:")
    print(validate_result.stdout)

    if validate_result.returncode != 0:
        print(f"❌ Validation failed!\n{validate_result.stderr}")
        return False

    print("\n[LOADER] Index and validation completed.")

    elapsed_time = time.perf_counter() - start_time

    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    print(
        f"\nTotal Index + Validation Time: "
        f"{hours}h {minutes}m {seconds}s"
    )

    return True


if __name__ == "__main__":
    run_standalone_index_validate()