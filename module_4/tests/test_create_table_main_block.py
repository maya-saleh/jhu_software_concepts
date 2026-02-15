import runpy
import pytest


@pytest.mark.db
def test_create_table_main_block_runs(monkeypatch):
    # Force DATABASE_URL branch
    monkeypatch.setenv("DATABASE_URL", "postgresql://fake")

    # Fake DB objects so we don't need a real DB locally
    class FakeCursor:
        def execute(self, *args, **kwargs):
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConn:
        autocommit = True

        def cursor(self):
            return FakeCursor()

        def close(self):
            return None

    # IMPORTANT: patch the connect used by the module when it runs as __main__
    import psycopg
    monkeypatch.setattr(psycopg, "connect", lambda *a, **k: FakeConn())

    # Run module as script so __main__ executes (main() -> create_table() -> get_conn())
    runpy.run_module("src.create_table", run_name="__main__")
