import pytest

@pytest.mark.db
def test_app_helper_branches(monkeypatch):
    import src.app as app

    class FakeConn:
        def close(self): 
            return None

    # get_db_conn: DATABASE_URL branch
    monkeypatch.setenv("DATABASE_URL", "postgresql://fake")
    monkeypatch.setattr(app.psycopg, "connect", lambda *a, **k: FakeConn())
    assert app.get_db_conn() is not None

    # get_db_conn: fallback branch
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(app.psycopg, "connect", lambda *a, **k: FakeConn())
    assert app.get_db_conn() is not None

    # parse_date branches
    assert app.parse_date(None) is None
    assert app.parse_date("") is None
    assert app.parse_date("not a date") is None
    assert str(app.parse_date("2026-01-31")) == "2026-01-31"

    # clean_text branches
    assert app.clean_text(None) is None
    assert app.clean_text("") is None
    assert app.clean_text(" \x00 hi \x00 ") == "hi"
