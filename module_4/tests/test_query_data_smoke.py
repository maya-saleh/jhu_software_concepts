import os
import pytest
import psycopg
import src.query_data as qd


@pytest.mark.db
def test_query_data_main_runs(capsys):
    # Ensure DB is reachable
    db_url = os.environ["DATABASE_URL"]

    # Make sure applicants table exists
    with psycopg.connect(db_url) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applicants (
                p_id BIGINT PRIMARY KEY,
                program TEXT,
                comments TEXT,
                date_added DATE,
                url TEXT,
                status TEXT,
                term TEXT,
                us_or_international TEXT,
                gpa DOUBLE PRECISION,
                gre INTEGER,
                gre_v INTEGER,
                gre_aw DOUBLE PRECISION,
                degree TEXT,
                llm_generated_program TEXT,
                llm_generated_university TEXT
            );
        """)

    # Run main() (it prints output)
    qd.main()
    out = capsys.readouterr().out

    # Basic smoke assertions that it printed expected headings
    assert "Q1" in out
    assert "Q2" in out
