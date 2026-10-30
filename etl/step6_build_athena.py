import duckdb
import zipfile
import sys
from pathlib import Path

try:
    DB_PATH = Path("/duckdb/mimic4.db")
    ZIP_DIR = Path("/athena")
    
    # 1. Identify the compressed zip file
    zip_files = list(ZIP_DIR.glob("*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No vocabulary zip archive discovered inside container path: {ZIP_DIR}")
    ZIP_PATH = zip_files[0]
    
    # 2. Automatically unzip everything hands-free if not already extracted
    # This matches CogStack's strategy but automates it completely
    unzip_target_dir = ZIP_DIR / "unpacked"
    if not unzip_target_dir.exists():
        print(f"[ATHENA LOAD] Extracting zipped archive hands-free to {unzip_target_dir}...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(unzip_target_dir)
        print("[ATHENA LOAD] Extraction complete.")

    # 3. Connect to DuckDB database instance and apply resource constraints
    con = duckdb.connect(str(DB_PATH))
    con.execute("SET memory_limit = '6GB'; SET threads = 4;")
    con.execute("SET temp_directory = '/duckdb/duckdb_temp'; SET max_temp_directory_size = '60GB';")
    con.execute("SET preserve_insertion_order = false; CREATE SCHEMA IF NOT EXISTS athena;")

    # 4. Target the extracted files exactly like CogStack's layout
    target_tables = ["CONCEPT", "CONCEPT_RELATIONSHIP", "VOCABULARY", "CONCEPT_CLASS", "DOMAIN", "RELATIONSHIP"]
    
    # Find all extracted items (handles both lowercase and uppercase variations gracefully)
    extracted_files = list(unzip_target_dir.glob("*"))
    
    for tbl in target_tables:
        # Match the text file inside the unpacked folder
        m_file = next((f for f in extracted_files if f.name.upper() in (tbl, f"{tbl}.CSV")), None)
        if not m_file:
            print(f"[ATHENA LOAD] Warning: {tbl} missing from unpacked directory.")
            continue
            
        print(f"[ATHENA LOAD] Ingesting {tbl} into database table athena.{tbl.lower()}...")
        con.execute(f"DROP TABLE IF EXISTS athena.{tbl.lower()};")
        
        # Ingest standard plain-text flat files using the exact tab delimiter rule
        con.execute(f"""
            CREATE TABLE athena.{tbl.lower()} AS 
            SELECT * FROM read_csv_auto(
                '{str(m_file)}', 
                delim='\\t', 
                header=True, 
                all_varchar=True, 
                quote='', 
                escape=''
            );
        """)
        print(f"[ATHENA LOAD] Successfully loaded athena.{tbl.lower()}")

    con.close()
    print("[ATHENA LOAD] Complete vocabulary core suite fully loaded.")

except Exception as err:
    print(f"\n[ATHENA CRITICAL FAILURE] Execution halted: {str(err)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
