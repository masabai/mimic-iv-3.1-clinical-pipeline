import os
import sys
from pathlib import Path
import duckdb

MIMIC_DB = os.getenv("MIMIC_DB", "/duckdb/mimic4.db")
CSV_DIR = Path("/data")

# 1. Hardcoded Athena tables (since they live inside the zip archive)
ATHENA_TABLES = [
    "athena.CONCEPT",
    "athena.CONCEPT_CLASS",
    "athena.CONCEPT_RELATIONSHIP",
    "athena.DOMAIN",
    "athena.RELATIONSHIP",
    "athena.VOCABULARY",
    "athena.CONCEPT_ANCESTOR",
    "athena.CONCEPT_SYNONYM",
    "athena.DRUG_STRENGTH",
    "athena.custom_mappings"
]
 

# Dynamically scan 'hosp' and 'icu' subdirectories for MIMIC tables
# (avoids hardcoding — picks up any new tables added in future MIMIC releases)
MIMIC_TABLES = []
for module in ["hosp", "icu"]:
    module_dir = CSV_DIR / module
    if module_dir.is_dir():
        # Captures file names like 'patients.csv.gz' and extracts 'patients'
        for file_path in module_dir.glob("*.csv.gz"):
            table_name = file_path.name.split(".")[0]
            MIMIC_TABLES.append(f"mimiciv.{table_name}")

# 3. Combine both lists dynamically
EXPECTED_TABLES = ATHENA_TABLES + MIMIC_TABLES


def verify_duckdb():
    print(f"[STEP 5] Verifying DuckDB schema: {MIMIC_DB}")

    # CHANGE 1: Missing database is an expected condition.
    # Return False instead of attempting a read-only connection.
    if not os.path.isfile(MIMIC_DB):
        print(
            "[STEP 5] Database does not exist yet — "
            "proceeding to loader."
        )
        return False

    con = None

    try:
        con = duckdb.connect(MIMIC_DB, read_only=True)

        rows = con.execute("""
            SELECT table_schema || '.' || table_name
            FROM information_schema.tables
            WHERE table_schema IN ('mimiciv', 'athena')
        """).fetchall()

        # FIXED: Extract the raw string from the 1-element tuple row
        tables = {row[0] for row in rows}
        missing = [table for table in EXPECTED_TABLES if table not in tables]

        # CHANGE 2: An incomplete database returns False.
        if missing:
            print(f"[STEP 4:VERIFY DUCKDB] FAIL — missing tables: {missing}")
            return False

        print(
            f"[STEP 4: VERIFY DUCKDB] PASS — "
            f"all {len(EXPECTED_TABLES)} expected tables found"
        )

        for table in EXPECTED_TABLES:
            count = con.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"[STEP 4:VERIFY DUCKDB] {table}: {count:,} rows")

        return True

    # CHANGE 3: Catch DuckDB errors instead of showing a traceback.
    except duckdb.Error as exc:
        print(f"[STEP 5] Verification failed: {exc}")
        return False

    except Exception as exc:
        print(f"[STEP 5] Unexpected verification error: {exc}")
        return False

    finally:
        if con is not None:
            con.close()


if __name__ == "__main__":
    # Standalone execution: exit 0 on PASS, 1 on FAIL.
    sys.exit(0 if verify_duckdb() else 1)
