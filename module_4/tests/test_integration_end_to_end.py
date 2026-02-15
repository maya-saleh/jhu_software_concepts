import os
import pytest
import psycopg


@pytest.mark.integration
def test_end_to_end_pull_update_render(monkeypatch):
    from src.app import create_app
    import src.scrape as scrape

    # Fake scraper returns multiple records
    fake_rows = [
        {
            "entry_url": "https://example.com/entry/333",
            "program_university_raw": "End2End U - CS",
            "comments": "e2e",
            "date_added": "January 31, 2026",
            "status": "Accepted",
            "start_term": "Fall 2026",
            "citizenship": "International",
            "gpa": 3.8,
            "gre_total": 328,
            "gre_v": 164,
            "gre_aw": 5.0,
        },
        {
            "entry_url": "https://example.com/entry/444",
            "program_university_raw": "End2End U2 - CS",
            "comments": "e2e2",
            "date_added": "February 1, 2026",
            "status": "Rejected",
            "start_term": "Fall 2026",
            "citizenship": "American",
            "gpa": 3.6,
            "gre_total": 322,
            "gre_v": 161,
            "gre_aw": 4.0,
        },
    ]
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda pages=10, sleep_s=0.75: fake_rows)

    # Clear DB table
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute("DELETE FROM applicants;")

    app = create_app({"TESTING": True})
    client = app.test_client()

    # pull -> rows in DB
    r1 = client.post("/pull-data")
    assert r1.status_code == 200

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        count = conn.execute("SELECT COUNT(*) FROM applicants;").fetchone()[0]
        assert count == 2

    # update-analysis succeeds when not busy
    r2 = client.post("/update-analysis")
    assert r2.status_code == 200

    # render shows Analysis + Answer label (basic)
    r3 = client.get("/analysis")
    assert r3.status_code == 200
    html = r3.get_data(as_text=True)
    assert "Analysis" in html
    assert "Answer" in html
