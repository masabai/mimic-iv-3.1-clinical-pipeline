
import os
import sys
import time
import gzip
import zlib
import hashlib
import json
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# CONFIGURATION — STRICT PRE-INGESTION SMOKE GATES
# ==============================================================================

# Linux / WSL2 paths
LANDING_ZONE_DIR = Path(
    os.environ.get(
        "MIMIC_LANDING_ZONE",
        "/home/moesa/mimiciv_full/data"
    )
).expanduser().resolve()

LOGS_OUTPUT_DIR = Path(
    os.environ.get(
        "MIMIC_VALIDATION_LOGS",
        "/home/moesa/mimic/mimic-iv-3.1-clinical-pipeline/etl/validation"
    )
).expanduser()

MIT_SCRIPT_PATH = Path(
    "/home/moesa/mimic/mimic-iv-3.1-clinical-pipeline/"
    "mimic-mit-build/download_data.sh"
)

EXPECTED_FILE_COUNTS = {"hosp": 22, "icu": 9}
EXPECTED_TOTAL_FILES = sum(EXPECTED_FILE_COUNTS.values())

CHUNK_SIZE = 8 * 1024 * 1024  # 8 MiB
MAX_WORKERS = 4

LOGS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[CONFIG] Landing zone: {LANDING_ZONE_DIR}")
print(f"[CONFIG] Logs directory: {LOGS_OUTPUT_DIR}")
print(f"[CONFIG] Download script exists: {MIT_SCRIPT_PATH.is_file()}")


# ==============================================================================
# HELPERS
# ==============================================================================

def discover_csv_files():
    """Find compressed CSV files in either flat or hosp/icu directory layout."""

    if not LANDING_ZONE_DIR.is_dir():
        raise FileNotFoundError(
            f"[FAIL] Landing zone does not exist: {LANDING_ZONE_DIR}"
        )

    hosp_dir = LANDING_ZONE_DIR / "hosp"
    icu_dir = LANDING_ZONE_DIR / "icu"

    if hosp_dir.is_dir() and icu_dir.is_dir():
        layout = "nested"
        files = {
            "hosp": sorted(hosp_dir.glob("*.csv.gz")),
            "icu": sorted(icu_dir.glob("*.csv.gz")),
        }
    else:
        layout = "flat"
        files = sorted(LANDING_ZONE_DIR.glob("*.csv.gz"))

    return layout, files


def write_json(filename, payload):
    """Write JSON atomically so an interrupted run does not leave a partial log."""

    output_path = LOGS_OUTPUT_DIR / filename
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    temp_path.replace(output_path)
    print(f"[LOG] Saved: {output_path}")


# ==============================================================================
# 1. FILE INVENTORY
# ==============================================================================

def verify_file_counts():
    """Validate table counts for nested or flat data layouts."""

    print("\n" + "=" * 70)
    print("[SMOKE CHECK 1/4] VERIFYING LANDING-ZONE FILE INVENTORY")
    print("=" * 70)

    layout, discovered = discover_csv_files()

    if layout == "nested":
        total = 0

        for module, expected in EXPECTED_FILE_COUNTS.items():
            found = discovered[module]
            actual = len(found)
            total += actual

            print(
                f"[INVENTORY] {module}: "
                f"{actual} of {expected} expected CSV.GZ files"
            )

            if actual != expected:
                raise ValueError(
                    f"[FAIL] {module}: expected {expected}, found {actual}"
                )

        all_files = discovered["hosp"] + discovered["icu"]

    else:
        all_files = discovered
        actual = len(all_files)

        print(f"[INVENTORY] Layout: flat")
        print(f"[INVENTORY] CSV.GZ files found: {actual}")
        print(f"[INVENTORY] Configured expected total: {EXPECTED_TOTAL_FILES}")

        if actual != EXPECTED_TOTAL_FILES:
            raise ValueError(
                f"[FAIL] Flat layout: expected {EXPECTED_TOTAL_FILES} "
                f"CSV.GZ files, found {actual}. "
                "Check the expected count before proceeding."
            )

    print(f"[PASS] Inventory count validated: {len(all_files)} files")
    return layout, all_files


# ==============================================================================
# 2. SHA-256 MANIFEST VALIDATION
# ==============================================================================

def parse_sha256_manifest():
    """Parse SHA256SUMS.txt, if present."""

    manifest_file = LANDING_ZONE_DIR / "SHA256SUMS.txt"

    if not manifest_file.is_file():
        print(
            f"[WARN] No SHA256SUMS.txt found in {LANDING_ZONE_DIR}. "
            "Cryptographic validation cannot be confirmed."
        )
        return None

    hash_map = {}
    pattern = re.compile(r"^([a-fA-F0-9]{64})\s+[* ]?(.+)$")

    with manifest_file.open("r", encoding="utf-8-sig") as f:
        for line in f:
            match = pattern.match(line.strip())

            if not match:
                continue

            digest, relative_path = match.groups()
            relative_path = relative_path.strip()

            # Accept Windows-style separators in manifests created on Windows.
            relative_path = relative_path.replace("\\", "/")
            hash_map[relative_path] = digest.lower()

    if not hash_map:
        raise ValueError(
            f"[FAIL] Manifest exists but no valid SHA-256 entries were found: "
            f"{manifest_file}"
        )

    print(f"[MANIFEST] Parsed {len(hash_map)} checksum entries")
    return hash_map


def resolve_manifest_path(relative_path, available_files):
    """Resolve a manifest entry using its relative path or a unique basename."""

    candidate = LANDING_ZONE_DIR / relative_path

    if candidate.is_file():
        return candidate

    basename_matches = [
        p for p in available_files if p.name == Path(relative_path).name
    ]

    if len(basename_matches) == 1:
        return basename_matches[0]

    return None


def stream_verify_file_hash(args):
    """Calculate SHA-256 in bounded-memory chunks."""

    file_path, expected_hash = args
    sha256_engine = hashlib.sha256()

    try:
        with file_path.open("rb") as f:
            for block in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_engine.update(block)

        actual_hash = sha256_engine.hexdigest()

        if actual_hash == expected_hash:
            print(f"[HASH PASS] {file_path.name}")
            return True

        print(f"[HASH FAIL] {file_path.name}: checksum mismatch")
        return False

    except OSError as exc:
        print(f"[HASH ERROR] {file_path.name}: {exc}")
        return False


def verify_cryptographic_hashes(all_files):
    """Verify every local file covered by the manifest."""

    print("\n" + "=" * 70)
    print("[SMOKE CHECK 2/4] VERIFYING SHA-256 CHECKSUMS")
    print("=" * 70)

    manifest = parse_sha256_manifest()

    if manifest is None:
        print("[WARN] SHA-256 gate skipped because no manifest is available.")
        return

    tasks = []
    missing = []

    for relative_path, expected_hash in manifest.items():
        target = resolve_manifest_path(relative_path, all_files)

        if target is None:
            missing.append(relative_path)
        else:
            tasks.append((target, expected_hash))

    if missing:
        for path in missing[:20]:
            print(f"[HASH MISSING] {path}")

        raise ValueError(
            f"[FAIL] {len(missing)} manifest entries could not be matched "
            "to local files. Check the manifest and directory layout."
        )

    if not tasks:
        raise ValueError("[FAIL] No local files matched the checksum manifest.")

    print(f"[SYSTEM] Verifying {len(tasks)} file(s), up to {MAX_WORKERS} at a time")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(stream_verify_file_hash, tasks))

    if not all(results):
        raise ValueError(
            "[FAIL] SHA-256 validation failed. Loading is blocked."
        )

    print(f"[PASS] All {len(tasks)} matched files passed SHA-256 validation.")


# ==============================================================================
# 3. FULL GZIP INTEGRITY VALIDATION
# ==============================================================================

def verify_gzip_file(file_path):
    """Read each gzip stream to EOF to verify decompression and CRC checks."""

    try:
        with gzip.open(file_path, "rb") as f:
            while f.read(CHUNK_SIZE):
                pass

        print(f"[GZIP PASS] {file_path.name}")
        return True

    except (OSError, EOFError, gzip.BadGzipFile, zlib.error) as exc:
        print(f"[GZIP FAIL] {file_path.name}: {exc}")
        return False

    except Exception as exc:
        print(f"[GZIP ERROR] {file_path.name}: {exc}")
        return False


def verify_gzip_integrity(all_files):
    """Reject any file that cannot be fully decompressed."""

    print("\n" + "=" * 70)
    print("[SMOKE CHECK 3/4] VALIDATING COMPLETE GZIP STREAMS")
    print("=" * 70)

    if not all_files:
        raise ValueError("[FAIL] No .csv.gz files found to validate.")

    # Import explicitly for the zlib.error exception handler above.
    # Full decompression checks every compressed stream, not just its header.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(verify_gzip_file, all_files))

    failures = [
        file_path.name
        for file_path, passed in zip(all_files, results)
        if not passed
    ]

    if failures:
        raise ValueError(
            f"[FAIL] {len(failures)} gzip file(s) failed integrity checks: "
            + ", ".join(failures)
        )

    print(f"[PASS] All {len(all_files)} gzip files passed full decompression.")


# ==============================================================================
# 4. CSV HEADER / SCHEMA VALIDATION
# ==============================================================================

def verify_column_headers(layout, all_files):
    """Read CSV headers and save a JSON schema catalog."""

    print("\n" + "=" * 70)
    print("[SMOKE CHECK 4/4] EXTRACTING CSV HEADERS")
    print("=" * 70)

    schema_catalog = {}
    failures = []

    for file_path in all_files:
        module = (
            file_path.parent.name
            if layout == "nested"
            else "flat"
        )

        try:
            with gzip.open(file_path, "rt", encoding="utf-8-sig", newline="") as f:
                header_line = f.readline()

            if not header_line:
                raise ValueError("Empty file or missing CSV header")

            # CSV-aware parsing handles quoted column names correctly.
            import csv
            columns = next(csv.reader([header_line]))

            if not columns or any(not column.strip() for column in columns):
                raise ValueError("Header contains an empty column name")

            schema_catalog[file_path.name] = {
                "module": module,
                "file_size_bytes": file_path.stat().st_size,
                "column_count": len(columns),
                "columns": columns,
            }

            print(
                f"[SCHEMA PASS] {file_path.name}: "
                f"{len(columns)} columns"
            )

        except Exception as exc:
            failures.append(file_path.name)
            print(f"[SCHEMA FAIL] {file_path.name}: {exc}")

    if failures:
        raise ValueError(
            "[FAIL] Could not read valid CSV headers from: "
            + ", ".join(failures)
        )

    write_json("landing_zone_schema_snapshot.json", schema_catalog)
    print(f"[PASS] Captured schemas for {len(schema_catalog)} files.")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    start_time = time.time()

    try:
        layout, all_files = verify_file_counts()
        verify_cryptographic_hashes(all_files)
        verify_gzip_integrity(all_files)
        verify_column_headers(layout, all_files)

        runtime = (time.time() - start_time) / 60

        print("\n" + "=" * 70)
        print(f"[SUCCESS] ALL SMOKE CHECKS PASSED IN {runtime:.2f} MINUTES")
        print("Ready for the PostgreSQL loading step.")
        print("=" * 70)

        sys.exit(0)

    except Exception as err:
        print(f"\n[PIPELINE TERMINATED] Smoke validation failed:\n{err}")
        print("[SAFETY] PostgreSQL loading must not proceed.")
        sys.exit(1)
