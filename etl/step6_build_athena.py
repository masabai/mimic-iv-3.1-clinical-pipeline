
import duckdb
import zipfile
import tempfile
from pathlib import Path

DB_PATH = Path("/duckdb/mimic4.db")
CSV_DIR = Path("/athena")

con = duckdb.connect(str(DB_PATH))
con.execute("CREATE SCHEMA IF NOT EXISTS athena;")


def table_exists(table_name):
    return con.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'athena'
          AND table_name = ?
    """, [table_name]).fetchone()[0] > 0


def load_csv_file(table_name, csv_path):
    if table_exists(table_name):
        print(f"SKIP: athena.{table_name} already exists")
        return

    # Escape SQL path
    csv_path = str(csv_path).replace("'", "''")

    try:
        con.execute(f"""
            CREATE TABLE athena."{table_name}" AS
            SELECT * FROM read_csv_auto('{csv_path}');
        """)

    except duckdb.ConversionException:
        con.execute(f"""
            CREATE TABLE athena."{table_name}" AS
            SELECT * FROM read_csv_auto(
                '{csv_path}',
                all_varchar=true
            );
        """)

    count = con.execute(
        f'SELECT COUNT(*) FROM athena."{table_name}"'
    ).fetchone()[0]

    print(f"LOADED: athena.{table_name} ({count:,} rows)")


# STEP 1: Existing extracted CSV files
for csv_file in CSV_DIR.rglob("*.csv"):
    load_csv_file(csv_file.stem, csv_file)


# STEP 2: CSV files inside ZIP archives
for zip_file in CSV_DIR.glob("*.zip"):

    print(f"\nScanning ZIP: {zip_file.name}")

    with zipfile.ZipFile(zip_file, "r") as archive:

        for member in archive.namelist():

            if not member.lower().endswith(".csv"):
                continue

            table_name = Path(member).stem

            if table_exists(table_name):
                print(f"SKIP: athena.{table_name} already exists")
                continue

            print(f"Loading from ZIP: {table_name}")

            with archive.open(member) as source:
                with tempfile.NamedTemporaryFile(
                    suffix=".csv",
                    mode="wb",
                    delete=True
                ) as temp:

                    while True:
                        chunk = source.read(8 * 1024 * 1024)
                        if not chunk:
                            break
                        temp.write(chunk)

                    temp.flush()

                    load_csv_file(table_name, temp.name)


# STEP 3: Custom mappings
con.execute("""
    CREATE TABLE IF NOT EXISTS athena.custom_mappings AS
    SELECT * FROM read_csv_auto('data/custom_mappings/*.csv');
""")

print("\n[STEP 6: VOCABULARY LOADED]")
print(f"DuckDB database: {DB_PATH}")

con.close()
