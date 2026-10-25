
import os
import sys
import duckdb

MIMIC_DB = os.getenv("MIMIC_DB", "/duckdb/mimic4.db")

EXPECTED_TABLES = [
    # hosp
    "mimiciv_hosp.admissions",
    "mimiciv_hosp.patients",
    "mimiciv_hosp.transfers",
    "mimiciv_hosp.diagnoses_icd",
    "mimiciv_hosp.procedures_icd",
    "mimiciv_hosp.labevents",
    "mimiciv_hosp.prescriptions",
    "mimiciv_hosp.pharmacy",
    "mimiciv_hosp.omr",
    # icu
    "mimiciv_icu.chartevents",
    "mimiciv_icu.icustays",
    "mimiciv_icu.inputevents",
    "mimiciv_icu.outputevents",
]


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
            WHERE table_schema IN ('mimiciv_hosp', 'mimiciv_icu')
        """).fetchall()

        tables = {row[0] for row in rows}
        missing = [table for table in EXPECTED_TABLES if table not in tables]

        # CHANGE 2: An incomplete database returns False.
        if missing:
            print(f"[STEP 5] FAIL — missing tables: {missing}")
            return False

        print(
            f"[STEP 5] PASS — "
            f"all {len(EXPECTED_TABLES)} expected tables found"
        )

        for table in EXPECTED_TABLES:
            count = con.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"[STEP 5] {table}: {count:,} rows")

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
