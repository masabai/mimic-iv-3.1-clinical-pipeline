"""Post-dbt QA step: runs validation.sql against the Gold OMOP layer and asserts data quality thresholds."""
import duckdb
import sys
from pathlib import Path

DB_PATH = Path("/duckdb/mimic4.db")
CURRENT_FILE_DIR = Path(__file__).resolve().parent  # /app/elt
PROJECT_ROOT = CURRENT_FILE_DIR.parent              # /app
SQL_SCRIPT_PATH = Path("/app/elt/validation.sql")


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
            # Format rates with 2 decimal places, format counts as clean whole integers
            val_str = f"{metric_a:,.2f}%" if "Rate" in label else f"{int(metric_a):,}"
            ref_str = f"{metric_b:,.2f}%" if "Rate" in label else f"{int(metric_b):,}"
            
            # Adjusted padding from 45 to 55 so your long label names fit without wrapping text
            print(f" Check: {label.ljust(55)} | Result: {val_str.rjust(10)} | Reference: {ref_str.rjust(10)}")
            
            # Violation counts must equal 0
            if "must be 0" in label and metric_a > 0:
                raise AssertionError(f"DATA QUALITY FAILURE: '{label}' found {int(metric_a):,} violations!")

            # person count must match patients exactly
            if "vs mimiciv.patients" in label and metric_a != metric_b:
                raise AssertionError(f"CRITICAL DATA LOSS: Count mismatch found in '{label}'!")
                
            # Concept 0 floor threshold verification rule
            if "Rate" in label and metric_a > metric_b:
                raise AssertionError(f"VOCABULARY CRASH: Mapping failure rate too high in '{label}' ({metric_a:.2f}%)!")
        print("[QA SUCCESS] All external automated checks passed successfully.")
    
    finally:
        con.close()

if __name__ == "__main__":
    try:
        run_pipeline_validation_script()
    except Exception as e:
        print(f"\n[QA FAILURE] Pipeline stopping due to test failure:\n{e}")
        sys.exit(1)
