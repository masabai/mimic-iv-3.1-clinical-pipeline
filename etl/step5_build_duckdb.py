import sys
import time
import duckdb
from pathlib import Path

MIMIC_DATA_DIR = Path("/data")
MIMIC_DB       = Path("/duckdb/mimic4.db")
TEMP_DIR       = Path("/duckdb/duckdb_temp")

def run_native_build():
    start_time = time.perf_counter()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"[STEP 4] Connecting to DuckDB at {MIMIC_DB}...")
    con = duckdb.connect(str(MIMIC_DB))
    
    # Strict resource limits configured for your 16GB RAM laptop
    con.execute("SET memory_limit = '6GB';")
    con.execute("SET threads = 4;")
    con.execute(f"SET temp_directory = '{TEMP_DIR}';")
    con.execute("SET max_temp_directory_size = '60GB';")
    con.execute("SET preserve_insertion_order = false;")
    
    print("[STEP 4] Resource constraints locked in (6GB RAM / 4 Cores).")
    
    # Comprehensive schema map for all MIMIC-IV 3.1 clinical tables
    schemas = {
        "mimiciv_hosp": [
            "admissions", "d_hcpcs", "d_icd_diagnoses", "d_icd_procedures",
            "d_labitems", "diagnoses_icd", "drgcodes", "hcpcsevents",
            "labevents", "microbiologyevents", "omr", "patients",
            "pharmacy", "poe", "poe_ids", "prescriptions",
            "procedures_icd", "provider", "services", "transfers"
        ],
        "mimiciv_icu": [
            "chartevents", "d_items", "datetimeevents", 
            "icustays", "ingredientevents", "inputevents", 
            "outputevents", "procedureevents"
        ]
    }
    
    success = True
    try:
        for schema, tables in schemas.items():
            print(f"\n[STEP 4] Initializing Schema: {schema}")
            con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
            
            # Resolves "mimiciv_hosp" -> "hosp" and "mimiciv_icu" -> "icu"
            dir_name = schema.split("_")[-1]
            
            for table in tables:
                csv_path = MIMIC_DATA_DIR / dir_name / f"{table}.csv"
                
                # Fall back to compressed file syntax if uncompressed is missing
                if not csv_path.exists():
                    csv_path = MIMIC_DATA_DIR / dir_name / f"{table}.csv.gz"
                
                if csv_path.exists():
                    print(f"[STEP 4] Loading {schema}.{table} from {csv_path.name}...")
                    # DuckDB streams the CSV block-by-block and automatically manages disk spillover
                    con.execute(f"CREATE TABLE {schema}.{table} AS SELECT * FROM read_csv_auto('{csv_path}', sample_size=-1);")
                else:
                    print(f"[STEP 4] WARNING — Skipping {table}: File not found at {csv_path}")
                    
        print("\n[STEP 4] PASS — DuckDB native load completed successfully.")
    except Exception as e:
        print(f"\n[STEP 4] FAIL — Engine Error: {str(e)}", file=sys.stderr)
        success = False
    finally:
        con.close()

    elapsed = time.perf_counter() - start_time
    h, m, s = int(elapsed // 3600), int((elapsed % 3600) // 60), int(elapsed % 60)
    print(f"[STEP 4] Time: {h}h {m}m {s}s")
    return success

if __name__ == "__main__":
    success = run_native_build()
    sys.exit(0 if success else 1)
