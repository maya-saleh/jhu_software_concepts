import os
import psycopg


def get_conn():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg.connect(db_url)

    # fallback for local dev only
    return psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="methJHU2026",
        host="localhost",
        port=5432,
    )


def create_table():
    conn = get_conn()
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS applicants (
                p_id INTEGER PRIMARY KEY,
                program TEXT,
                comments TEXT,
                date_added DATE,
                url TEXT,
                status TEXT,
                term TEXT,
                us_or_international TEXT,
                gpa DOUBLE PRECISION,
                gre DOUBLE PRECISION,
                gre_v DOUBLE PRECISION,
                gre_aw DOUBLE PRECISION,
                degree TEXT,
                llm_generated_program TEXT,
                llm_generated_university TEXT
            );
        """)

    conn.close()
    return True


def main():
    create_table()
    print("applicants table created.")


if __name__ == "__main__":
    main()
