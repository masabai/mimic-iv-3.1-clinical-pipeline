import duckdb
import subprocess
import sys
from pathlib import Path

# ==============================================================================
# 1. PATH CONFIGURATIONS (Copy these exactly from your working step7 script)
# ==============================================================================
DB_PATH = Path("/duckdb/mimic4.db")
CURRENT_FILE_DIR = Path(__file__).resolve().parent  # /app/etl
PROJECT_ROOT = CURRENT_FILE_DIR.parent              # /app
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"     # /app/dbt_project
# Direct single-line declaration using the Path operator
SQL_SCRIPT_PATH = Path("/app/etl/validation.sql")


def run_pipeline_validation_script():
    print(f"[QA] Reading verification rules from {SQL_SCRIPT_PATH.name}...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    
    try:
        # Load your multi-statement SQL script text
        with open(SQL_SCRIPT_PATH, 'r') as file:
            raw_sql = file.read()
            
        # DuckDB handles multiple semi-colon statements seamlessly using execute()
        print("[QA] Executing quick clinical data assertions...")
        results = con.execute(raw_sql).fetchall()
        
        print("\n================== PIPELINE VALIDATION MATRIX ==================")
        for label, metric_a, metric_b in results:
            print(f" Check: {label.ljust(45)} | Result: {metric_a:,} | Reference: {metric_b:,}")
            
            # Target count verification rule
            if "vs" in label and metric_a != metric_b:
                raise AssertionError(f"CRITICAL DATA LOSS: Count mismatch found in '{label}'!")
                
            # Concept 0 floor threshold verification rule
            if "Rate" in label and metric_a > metric_b:
                raise AssertionError(f"VOCABULARY CRASH: Mapping failure rate too high in '{label}'!")
                
        print("================================================================\n")
        print("[QA SUCCESS] All external automated checks passed successfully.")
    finally:
        con.close()

if __name__ == "__main__":
    try:
        run_pipeline_validation_script()
    except Exception as e:
        print(f"\n[QA FAILURE] Pipeline stopping due to test failure:\n{e}")
        sys.exit(1)
