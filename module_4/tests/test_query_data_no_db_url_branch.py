import runpy
import pytest

@pytest.mark.db
def test_query_data_uses_no_database_url_branch(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Important: patch connect in the module *when it runs as __main__*
    import src.query_data as qd

    class FakeCursor:
        def __init__(self):
            self._fetchone_vals = iter([
                (0,), (0,), (0,0,0,0,0,0,0,0),
                (0,), (0,), (0,), (0,), (0,), (0,),
            ])
        def execute(self, *a, **k): return None
        def fetchone(self): return next(self._fetchone_vals)
        def fetchall(self): return []
        def __enter__(self): return self
        def __exit__(self, *a): return False

    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): return None

    monkeypatch.setattr(qd.psycopg, "connect", lambda *a, **k: FakeConn())

    runpy.run_module("src.query_data", run_name="__main__")
