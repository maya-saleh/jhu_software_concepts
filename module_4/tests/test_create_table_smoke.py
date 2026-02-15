import os
import pytest
import psycopg

import src.create_table as ct


@pytest.mark.db
def test_create_table_runs(monkeypatch):
    # Use your test DB
    db_url = os.environ["DATABASE_URL"]

    # Monkeypatch psycopg.connect inside create_table.py to use DATABASE_URL
    real_connect = psycopg.connect
    monkeypatch.setattr(ct.psycopg, "connect", lambda *args, **kwargs: real_connect(db_url))


    # Run the function / script entrypoint your file provides
    # If your create_table.py has a function, call it.
    # If it only runs SQL at import-time, then importing already executed it.
    if hasattr(ct, "create_table"):
        ct.create_table()

    # Assert the table exists
    with psycopg.connect(db_url) as conn:
        exists = conn.execute(
            "SELECT to_regclass('public.applicants');"
        ).fetchone()[0]
        assert exists == "applicants"
