"""Step 7: Runs dbt to build all 88 Bronze → Silver → Gold OMOP models against DuckDB."""
import subprocess
import sys
from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent  # /app/etl
PROJECT_ROOT = CURRENT_FILE_DIR.parent              # /app
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"     # /app/dbt_project

def execute_dbt_build():
    print(f"\n[PREFECT] Target Project Directory: {DBT_PROJECT_DIR}")
    print("[PREFECT] Running dbt build transforms...")

    # Run with text=True and capture output to force errors into the main terminal logs
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt.cli.main",
            "run",
            "--project-dir", str(DBT_PROJECT_DIR),
            "--profiles-dir", str(DBT_PROJECT_DIR),
            "--target", "dev",
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )

    # Print whatever dbt processed out to the console logs
    if result.stdout:
        print(f"[DBT STDOUT]\n{result.stdout}")
    if result.stderr:
        print(f"[DBT STDERR]\n{result.stderr}")

    if result.returncode != 0:
        print(f"[STEP 7: RUN DBT ]ERROR dbt run failed with return code {result.returncode}")
        sys.exit(result.returncode)

    print("STEP 7: RUN DBT ]PASS dbt run transformations completed.")
    sys.exit(0)

if __name__ == "__main__":
    execute_dbt_build()
