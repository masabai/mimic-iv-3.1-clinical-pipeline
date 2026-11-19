"""Step 5: Loads all MIMIC-IV CSV.gz files from /data into DuckDB under the mimiciv schema."""
import duckdb
from pathlib import Path
DB_PATH = Path("/duckdb/mimic4.db")
CSV_DIR = Path("/data")

# Connect to DuckDB (creates file if it doesn't exist)
con = duckdb.connect(str(DB_PATH))

# Memory tuning configs for your 16GB RAM laptop
#5GB-2 threds :13 mins
# To try with 8GB-4 threads
con.execute("SET memory_limit = '5GB';") 
con.execute("SET threads = 2;")
con.execute("SET temp_directory = '/duckdb/duckdb_temp';")
con.execute("SET max_temp_directory_size = '60GB';")

# Recursively load all hosp/ and icu/ CSV.gz files into mimiciv schema
for csv_file in CSV_DIR.glob("**/*.csv.gz"):
    print(csv_file)
    # Remove all extensions
    table_name = csv_file.name.replace('.csv.gz', '').replace('.', '_').replace('-', '_')
    print(f"Loading {csv_file} into table {table_name}...")
    
    con.execute(f"CREATE SCHEMA IF NOT EXISTS mimiciv;")
    try:
        con.execute(f"""
            CREATE TABLE IF NOT EXISTS mimiciv.{table_name} AS
            SELECT * FROM read_csv_auto('{csv_file}');
        """)
    except duckdb.ConversionException:
        con.execute(f"""
            CREATE TABLE IF NOT EXISTS mimiciv.{table_name} AS
            SELECT * FROM read_csv_auto('{csv_file}', all_varchar=True);
        """)

con.close()
print(f"[STEP 5: BUILD MIMIC DATA] DuckDB database created at {DB_PATH} with all tables loaded.")
