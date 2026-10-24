import sys
import duckdb

MIMIC_DB = "/duckdb/mimic4.db"

EXPECTED_TABLES = [
    "admissions", "patients", "transfers", "diagnoses_icd",
    "procedures_icd", "labevents", "prescriptions", "pharmacy",
    "omr", "chartevents", "icustays", "inputevents", "outputevents",
]


def verify_duckdb():
    print(f"[STEP 5] Verifying DuckDB schema: {MIMIC_DB}")

    con = duckdb.connect(MIMIC_DB, read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}

    missing = [t for t in EXPECTED_TABLES if t not in tables]
    if missing:
        print(f"[STEP 5] FAIL — missing tables: {missing}")
        con.close()
        return False

    print(f"[STEP 5] PASS — {len(tables)} tables found")

    for table in EXPECTED_TABLES:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"[STEP 5] {table}: {count:,} rows")

    con.close()
    return True


if __name__ == "__main__":
    success = verify_duckdb()
    sys.exit(0 if success else 1)
