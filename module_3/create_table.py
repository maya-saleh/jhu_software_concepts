import psycopg

conn = psycopg.connect(
    dbname="postgres",
    user="postgres",
    password="methJHU2026",
    host="localhost",
    port=5432,
)

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
print("applicants table created.")
