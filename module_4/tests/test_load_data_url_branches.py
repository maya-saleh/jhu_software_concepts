import io
import json
import runpy
import builtins
import pytest


class FakeCursor:
    def __init__(self):
        self.exec_calls = []

    def execute(self, sql, params=None):
        self.exec_calls.append((sql, params))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConn:
    def __init__(self):
        self.autocommit = False
        self.cursor_obj = FakeCursor()

    def cursor(self):
        return self.cursor_obj

    def close(self):
        pass


@pytest.mark.db
def test_load_data_hits_non_dict_valueerror_and_success(monkeypatch):
    # 1) non-dict record -> hits: if not isinstance(rec, dict): continue
    non_dict = json.dumps(123)

    # 2) dict with bad url -> hits: except ValueError: continue
    bad_url = json.dumps({
        "url": "https://example.com/entry/NOT_A_NUMBER",
        "program": "X",
        "comments": "Y",
        "date_added": "January 31, 2026",
        "applicant_status": "Accepted",
        "semester_year_start": "Fall 2026",
        "citizenship": "International",
    })

    # 3) dict with good url -> hits: try block success, runs cur.execute(...)
    good_url = json.dumps({
        "url": "https://example.com/entry/333",
        "program": "Test U - CS",
        "comments": "ok",
        "date_added": "January 31, 2026",
        "applicant_status": "Accepted",
        "semester_year_start": "Fall 2026",
        "citizenship": "International",
    })

    fake_file = io.StringIO("\n".join([non_dict, bad_url, good_url]))

    # Make load_data read our fake JSON lines
    monkeypatch.setattr(builtins, "open", lambda *a, **k: fake_file)

    # Force it to use patched connect path (no real DB)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Patch psycopg.connect inside src.load_data
    import src.load_data as ld
    fake_conn = FakeConn()
    monkeypatch.setattr(ld.psycopg, "connect", lambda *a, **k: fake_conn)

    # Run the module main block
    runpy.run_module("src.load_data", run_name="__main__")

    # Only the good_url record should get to execute()
    assert len(fake_conn.cursor_obj.exec_calls) == 1
