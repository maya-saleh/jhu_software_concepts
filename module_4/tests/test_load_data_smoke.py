import io
import os
import builtins
import pytest
import psycopg

import src.load_data as ld


@pytest.mark.db
def test_load_data_main_upserts_rows(monkeypatch, capsys):
    db_url = os.environ["DATABASE_URL"]

    # Ensure table exists
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
        conn.execute("TRUNCATE applicants;")

    # Fake JSONL file content (2 lines)
    fake_jsonl = "\n".join([
        '{"program":"X Univ","comments":"hi","date_added":"2026-01-31","url":"https://example.com/result/1001","applicant_status":"Accepted","semester_year_start":"Fall 2026","citizenship":"International","gpa":"3.90","gre":"330","gre_v":"165","gre_aw":"5.0","masters_or_phd":"PhD","llm-generated-program":"Computer Science","llm-generated-university":"X University"}',
        '{"program":"Y Univ","comments":"yo","date_added":"February 1, 2026","url":"https://example.com/result/1002","applicant_status":"Rejected","semester_year_start":"Fall 2026","citizenship":"American","gpa":"3.50","gre":"320","gre_v":"160","gre_aw":"4.0","masters_or_phd":"MS","llm-generated-program":"Computer Science","llm-generated-university":"Y University"}',
        ""
    ])

    # Patch open() used inside load_data.main() to return our fake JSONL
    def fake_open(path, mode="r", encoding=None):
        return io.StringIO(fake_jsonl)

    monkeypatch.setattr(builtins, "open", fake_open)

    # Run
    ld.main()

    # Assert rows inserted
    with psycopg.connect(db_url) as conn:
        n = conn.execute("SELECT COUNT(*) FROM applicants;").fetchone()[0]
        assert n == 2

    out = capsys.readouterr().out
    assert "Upserted" in out
