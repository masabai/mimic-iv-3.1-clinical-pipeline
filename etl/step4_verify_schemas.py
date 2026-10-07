# step4_verify_postgres.py
import psycopg

DB_CONFIG = {
    "host": "10.0.0.21",
    "port": 5432,
    "dbname": "mimiciv_testing",
    "user": "postgres",
    "password": "123",
}

def verify_postgres():
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()

            if result != (1,):
                raise RuntimeError("PostgreSQL connection test failed.")

    print("[VERIFY] PostgreSQL connection: PASS")
    return True


if __name__ == "__main__":
    verify_postgres()