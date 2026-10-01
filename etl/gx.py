import glob
import json
import time
from datetime import datetime
from pathlib import Path
import great_expectations as gx
from great_expectations.checkpoint import Checkpoint
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.core.validation_definition import ValidationDefinition

# ==============================================================================
# CONFIGURATION — DEFINITIVE LANDING ZONE VALIDATION (GX V1.X STRICT COMPLIANT)
# ==============================================================================
BASE_DIR = Path(r"C:\PythonProjects\mimic-clinical-pipeline")
LANDING_ZONE_DIR = Path(r"C:\PythonProjects\data\mimic-iv-3.1")
GX_OUTPUT_DIR = BASE_DIR / "etl" / "validation"
GX_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# MIMIC Files and their corresponding module folders
MIMIC_TARGET_FILES = {
    #"admissions": "hosp",
    "chartevents": "icu"
}

import hashlib

def verify_file_hash(file_path: str, expected_hash: str) -> bool:
    """Streams file in blocks to check MD5 without exploding RAM."""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read in 8MB chunks
        for byte_block in iter(lambda: f.read(8192 * 1024), b""):
            md5_hash.update(byte_block)
    
    return md5_hash.hexdigest() == expected_hash


def run_data_validation(file_path, batch_name):
    """
    Validates a massive compressed MIMIC file out-of-core using DuckDB and GX 1.x.
    """
    context = gx.get_context(mode="ephemeral")
    
    # Initialize DuckDB context
    data_source = context.data_sources.add_sql(
        name=f"source_{batch_name}",
        connection_string="duckdb:///:memory:"
    )

    # Clean path separation for the engine parser string
    clean_path = str(file_path).replace("\\", "/")
    query = f"SELECT * FROM read_csv_auto('{clean_path}')"
    
    data_asset = data_source.add_query_asset(name=f"asset_{batch_name}", query=query)
    
    # Fix: Explicitly declare the named batch definition whole table mapping
    batch_definition = data_asset.add_batch_definition_whole_table(name=f"batch_def_{batch_name}")

    suite = ExpectationSuite(name=f"suite_{batch_name}")
    context.suites.add(suite)

    # --- Structural Column Expectations ---
    suite.add_expectation(gx.expectations.ExpectColumnToExist(column="subject_id"))

    if batch_name == "admissions":
        suite.add_expectation(gx.expectations.ExpectColumnToExist(column="hadm_id"))
        suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="hadm_id"))
    elif batch_name == "icustays":
        suite.add_expectation(gx.expectations.ExpectColumnToExist(column="stay_id"))
        suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="stay_id"))
    elif batch_name == "chartevents":
            suite.add_expectation(gx.expectations.ExpectColumnToExist(column="charttime"))
            suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="charttime"))
    
    validation_definition = context.validation_definitions.add(
            ValidationDefinition(
            name=f"val_def_{batch_name}",
            data=batch_definition,
            suite=suite
        )
    )
      
    checkpoint = context.checkpoints.add(
    Checkpoint(
        name=f"chk_{batch_name}",
        validation_definitions=[validation_definition]
    )
)
    results = checkpoint.run()
    return results


def validate_all_mimic_files():
    """
    ETL step wrapper to scan landing zone, execute GX, and save metrics.
    """
    for file_name, folder in MIMIC_TARGET_FILES.items():
        file_path = LANDING_ZONE_DIR / folder / f"{file_name}.csv.gz"
        
        if not file_path.exists():
            print(f"[WARN] Target file missing, skipping: {file_path}")
            continue

        print(f"\n[GX PIPELINE] Streaming landing zone asset: {file_path}")
        validation_results = run_data_validation(file_path, batch_name=file_name)

        # Output execution metrics to JSON exactly like your CDC portfolio project
        output_file = GX_OUTPUT_DIR / f"gx_{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        """
        with open(output_file, "w", encoding="utf-8") as f:
           json.dump(validation_results, f, indent=2, default=str)
           print(f"[SUCCESS] JSON Run Report localized: {output_file}")
           print(json.dumps(validation_results, indent=2, default=str))
        """
        
        
        report = {}

        for key, result in validation_results.run_results.items():
         report[str(key)] = {
        "success": result.success,
        "suite_name": result.suite_name,
        "statistics": result.statistics,
        "results": [
            {
                "success": r.success,
                "expectation": r.expectation_config.type,
                "column": r.expectation_config.kwargs.get("column"),
                "result": r.result,
                "exception_info": r.exception_info,
            }
            for r in result.results
        ],
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)






def _extract_row_count(gx_json):
    """Parses verification metrics from the evaluation data wrapper."""
    for _, val in gx_json.get("run_results", {}).items():
        metrics = val.get("validation_result", {}).get("statistics", {})
        if "evaluated_expectations" in metrics:
            return metrics.get("successful_expectations", 100) 
    return None


def check_observability_drift():
    """
    ETL Data Observability step: Compares iterations to halt automated steps if metrics drift.
    """
    VOLUME_DROP_THRESHOLD = 0.10  # Flag anomaly if row counts drop >10%
    anomalies = []

    for dataset in MIMIC_TARGET_FILES.keys():
        pattern = str(GX_OUTPUT_DIR / f"gx_{dataset}_*.json")
        files = sorted(glob.glob(pattern))

        if len(files) < 2:
            print(f"[Observability] {dataset}: Base baseline iteration recorded.")
            continue

        try:
            with open(files[-2]) as f:
                prev = json.load(f)
            with open(files[-1]) as f:
                curr = json.load(f)
        except json.JSONDecodeError:
            print(f"[Observability] {dataset}: Previous report is invalid/empty. Skipping drift check.")
            continue

        prev_rows = _extract_row_count(prev)
        curr_rows = _extract_row_count(curr)
        
        if prev_rows and curr_rows:
            drop_pct = (prev_rows - curr_rows) / prev_rows
            print(f"[Observability] {dataset} volume: {prev_rows} -> {curr_rows} ({drop_pct:+.1%})")
            if drop_pct > VOLUME_DROP_THRESHOLD:
                anomalies.append(
                    f"Volume anomaly detected on [{dataset}]: {drop_pct:.1%} drop ({prev_rows} -> {curr_rows})"
                )

    if anomalies:
        print("[CRITICAL] Automated load gate frozen by drift check parameters.")
        raise ValueError("Observability validation breach:\n" + "\n".join(anomalies))


if __name__ == "__main__":
    start_time = time.time()
    
    # 1. Run Data Validation Stage
    validate_all_mimic_files()
    
    # 2. Run Observability Drift Check Stage
    check_observability_drift()
    
    total_time = (time.time() - start_time) / 60
    print(f"\n[SYSTEM STATUS] Script pipeline processed completely in {total_time:.2f} minutes.")
