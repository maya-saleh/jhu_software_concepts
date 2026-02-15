import pytest

@pytest.mark.buttons
def test_pull_data_skips_bad_urls_and_inserts_good(monkeypatch):
    from src.app import create_app
    import src.app as app_module
    import src.scrape as scrape

    # Fake scrape data to hit:
    # 1) if not url: continue
    # 2) ValueError on p_id parse: continue
    # 3) one good url to hit cur.execute + upserted += 1
    fake_rows = [
        {"entry_url": None},  # hits: if not url -> continue
        {"entry_url": "https://example.com/entry/NOTANINT"},  # hits: ValueError -> continue
        {  # hits: good row path
            "entry_url": "https://example.com/entry/123",
            "program_university_raw": "Test U",
            "comments": "hi\x00",  # hits clean_text NUL removal
            "date_added": "January 31, 2026",  # hits parse_date success
            "status": "Accepted",
            "start_term": "Fall 2026",
            "citizenship": "International",
            "gpa": 3.9,
            "gre_total": 330,
            "gre_v": 165,
            "gre_aw": 5.0,
        },
    ]
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda *a, **k: fake_rows)

    # Fake DB conn + cursor so no real DB required
    class FakeCursor:
        def execute(self, *a, **k): return None
        def __enter__(self): return self
        def __exit__(self, *a): return False

    class FakeConn:
        autocommit = True
        def cursor(self): return FakeCursor()
        def close(self): return None

    monkeypatch.setattr(app_module, "get_db_conn", lambda: FakeConn())

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.post("/pull-data")
    assert resp.status_code == 200
