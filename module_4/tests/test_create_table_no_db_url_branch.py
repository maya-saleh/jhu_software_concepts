import pytest

@pytest.mark.db
def test_create_table_get_conn_fallback_branch(monkeypatch):
    import src.create_table as ct

    # Force fallback branch (no DATABASE_URL)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    called = {}

    def fake_connect(*args, **kwargs):
        # record what create_table tried to connect with
        called["args"] = args
        called["kwargs"] = kwargs
        return object()  # any dummy object is fine because we only call get_conn()

    monkeypatch.setattr(ct.psycopg, "connect", fake_connect)

    conn = ct.get_conn()
    assert conn is not None

    # Optional sanity checks that it used the fallback kwargs (adjust if yours differ)
    assert called["kwargs"]["dbname"] == "postgres"
    assert called["kwargs"]["user"] == "postgres"
    assert called["kwargs"]["host"] == "localhost"
    assert called["kwargs"]["port"] == 5432
