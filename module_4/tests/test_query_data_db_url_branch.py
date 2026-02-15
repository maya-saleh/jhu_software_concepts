import runpy
import pytest

@pytest.mark.db
def test_query_data_uses_database_url_branch(monkeypatch):
    import src.query_data as qd

    monkeypatch.setenv("DATABASE_URL", "postgresql://fake")

    class FakeCursor:
        def __init__(self):
            self._fetchone_vals = iter([
                (0,),                      # Q1
                (0,),                      # Q2
                (0, 0, 0, 0, 0, 0, 0, 0),   # Q3 (8 values)
                (0,),                      # Q4
                (0,),                      # Q5
                (0,),                      # Q6
                (0,),                      # Q7
                (0,),                      # Q8
                (0,),                      # Q9
            ])

        def execute(self, *args, **kwargs):
            return None

        def fetchone(self):
            return next(self._fetchone_vals)

        def fetchall(self):
            return []  # Q10/Q11 loops

        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False

    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): return None

    monkeypatch.setattr(qd.psycopg, "connect", lambda *a, **k: FakeConn())

    runpy.run_module("src.query_data", run_name="__main__")
