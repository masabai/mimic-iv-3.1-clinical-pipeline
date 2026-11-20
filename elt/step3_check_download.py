"""Step 3: Pre-ingestion smoke checks — validates file counts, SHA-256 hashes, and column schemas."""
import os
import sys
import re
import time
import gzip
import hashlib
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# CONFIGURATION — STRICT PRE-INGESTION SMOKE GATES
# ==============================================================================
LANDING_ZONE_DIR = Path("/data")
LOGS_OUTPUT_DIR = Path("/app/elt/validation")
LOGS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Total expected file volume counts (including data tables)
EXPECTED_FILE_COUNTS = {"hosp": 22, "icu": 9}


# ==============================================================================
# 1: FILE COUNT VALIDATION
# ==============================================================================
def verify_file_counts():
    """Checks that the download directory contains the correct number of data tables."""
    print("\n================================================================== ")
    print("[SMOKE CHECK 1/3] VERIFYING LANDING ZONE FILE VOLUMES")
    print("==================================================================")
    
    for module, expected in EXPECTED_FILE_COUNTS.items():
        module_path = LANDING_ZONE_DIR / module
        if not module_path.exists():
            raise FileNotFoundError(f"[FAIL] Target module path not found on server: {module_path}")
            
        found_files = list(module_path.glob("*.csv.gz"))
        print(f"[INVENTORY] Module '{module}': Found {len(found_files)} of {expected} tables.")
        
        if len(found_files) != expected:
            raise ValueError(f"[FAIL] Incomplete download in '{module}'. Expected {expected}, got {len(found_files)}.")
    print("[PASS] File counts match.")


# ==============================================================================
# 2: MULTI-THREADED SHA-256 MANIFEST SUMS CHECK
# ==============================================================================
def parse_sha256_manifest():
    """Parses manifest checksum pairs from the landing path."""
    manifest_file = LANDING_ZONE_DIR / "SHA256SUMS.txt"
    if not manifest_file.exists():
        print(f"[WARN] Manifest SHA256SUMS.txt missing in {LANDING_ZONE_DIR}. Skipping hash checks.")
        return {} #avoids crashing if the file is missing
        
    hash_map = {}
    # example => 5ec6c252aae1f035de05c2053ad1279a138ee00d22d1569a712a1df7e31371c2 icu/procedureevents.csv.gz
    # \s+ -> 1 or more space, (.+)-> remaining file path, ^ -> start, $ -> end
    pattern = re.compile(r"^([a-fA-F0-9]{64})\s+(.+)$")
    with open(manifest_file, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                sha_val, relative_path = match.groups()
                clean_rel_path = Path(relative_path.replace("/", os.sep))# makes the file path compatible with os
                hash_map[clean_rel_path] = sha_val
    return hash_map


def stream_verify_file_hash(args):
    """Streams files in 8MB chunks to check cryptographic signatures without memory spikes."""
    file_path, expected_hash = args
    sha256_engine = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(8192 * 1024), b""): #b"" -> empty byte string - no more bytes to read
                sha256_engine.update(byte_block)
        
        if sha256_engine.hexdigest() == expected_hash:
            print(f"[HASH PASS] {file_path.name}")
            return True
        print(f"[HASH FAIL] Mismatch on target asset: {file_path.name}")
        return False
    except Exception as e:
        print(f"[HASH ERROR] Could not read file {file_path.name}: {e}")
        return False


def verify_cryptographic_hashes():
    """Coordinates parallel worker threads to validate extraction signatures."""
    print("\n==================================================================")
    print("[SMOKE CHECK 2/3] RUNNING CRYPTOGRAPHIC MANIFEST CHECKS")
    print("==================================================================")
    
    manifest_map = parse_sha256_manifest()
    if not manifest_map:
        return
        
    tasks = []
    for rel_path, expected_hash in manifest_map.items():
        absolute_target = LANDING_ZONE_DIR / rel_path
        if absolute_target.exists():
            tasks.append((absolute_target, expected_hash))
            
    print(f"[SYSTEM] Dispatching {len(tasks)} parallel validation hash streams...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(stream_verify_file_hash, tasks))
        
    if not all(results):
        raise ValueError("[FAIL] Extraction payload corrupted. Checksum gates blocked loading phase.")
    print("[PASS] All landing zone assets match official cryptographic keys.")


# ==============================================================================
# 3: HEADER SCHEMA LOOKUP
# ==============================================================================
def verify_column_headers():
    """Inspects only the first line of each compressed file to dump schema maps."""
    print("\n==================================================================")
    print("[SMOKE CHECK 3/3] EXTRACTING METADATA & COLUMN SCHEMAS")
    print("==================================================================")
    
    schema_catalog = {}
    
    for module in EXPECTED_FILE_COUNTS.keys():
        module_path = LANDING_ZONE_DIR / module
        for file_path in module_path.glob("*.csv.gz"):
            try:
                # Open with gzip streaming mode, reading only the first text line
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    header_line = f.readline().strip()
                    columns = header_line.split(",") if header_line else []
                    
                schema_catalog[file_path.name] = {
                    "module": module,
                    "column_count": len(columns),
                    "columns": columns
                }
                print(f"[SCHEMA CAPTURED] {file_path.name} (Columns: {len(columns)})")
            except Exception as e:
                print(f"[SCHEMA ERROR] Failed parsing file metadata for {file_path.name}: {e}")
                
    # Save the catalog structure to a clean json log for portfolio evidence
    output_log = LOGS_OUTPUT_DIR / f"landing_zone_schema_snapshot.json"
    with open(output_log, "w", encoding="utf-8") as f:
        json.dump(schema_catalog, f, indent=2)
    print(f"[PASS] Complete column catalog layout saved to: {output_log.name}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        verify_file_counts()           # Check 1: Volumetric File Count 
        verify_cryptographic_hashes()  # Check 2: File Content hash check
        verify_column_headers()        # Check 3: Extract Column Names & Counts
        print("\n==================================================================")
        print("[STEP 3] PASS PRE-INGESTION CHECKS PASSED - READY FOR LOAD STEP")
        print("==================================================================")
        
        sys.exit(0)  # <--- EXPLICITLY RETURN STATUS 0 (SUCCESS) TO PREFECT (for next step)
        
    except Exception as err:
        print(f"\n[PIPELINE TERMINATED] Ingestion halted by smoke validation check:\n{err}")
        
        sys.exit(1)  # <--- EXPLICITLY RETURN STATUS 1 (FAILURE) TO PREFECT (for next step)
