import os
import pytest
import psycopg


@pytest.mark.db
def test_pull_inserts_rows_into_db(monkeypatch):
    # IMPORTANT: set this to your local test database URL
    # Example format:
    # postgresql://postgres:YOURPASSWORD@localhost:5432/postgres
    os.environ["DATABASE_URL"] = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:YOURPASSWORD@localhost:5432/postgres",
    )

    from src.app import create_app
    import src.scrape as scrape

    # Fake scraper returns 2 records (no internet)
    fake_rows = [
        {
            "entry_url": "https://example.com/entry/111",
            "program_university_raw": "Test University - CS",
            "comments": "hello",
            "date_added": "January 31, 2026",
            "status": "Accepted",
            "start_term": "Fall 2026",
            "citizenship": "International",
            "gpa": 3.9,
            "gre_total": 330,
            "gre_v": 165,
            "gre_aw": 5.0,
        },
        {
            "entry_url": "https://example.com/entry/222",
            "program_university_raw": "Another University - CS",
            "comments": "world",
            "date_added": "February 1, 2026",
            "status": "Rejected",
            "start_term": "Fall 2026",
            "citizenship": "American",
            "gpa": 3.5,
            "gre_total": 320,
            "gre_v": 160,
            "gre_aw": 4.0,
        },
    ]
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda pages=10, sleep_s=0.75: fake_rows)

    # Clear table first
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute("DELETE FROM applicants;")

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.post("/pull-data")
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}

    # Verify rows inserted
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        count = conn.execute("SELECT COUNT(*) FROM applicants;").fetchone()[0]
        assert count == 2
@pytest.mark.db
def test_duplicate_pull_does_not_create_duplicates(monkeypatch):
    import src.scrape as scrape
    from src.app import create_app
    import psycopg
    import os

    # Same fake data as before (same p_id values)
    fake_rows = [
        {
            "entry_url": "https://example.com/entry/111",
            "program_university_raw": "Test University - CS",
            "comments": "hello",
            "date_added": "January 31, 2026",
            "status": "Accepted",
            "start_term": "Fall 2026",
            "citizenship": "International",
            "gpa": 3.9,
            "gre_total": 330,
            "gre_v": 165,
            "gre_aw": 5.0,
        },
        {
            "entry_url": "https://example.com/entry/222",
            "program_university_raw": "Another University - CS",
            "comments": "world",
            "date_added": "February 1, 2026",
            "status": "Rejected",
            "start_term": "Fall 2026",
            "citizenship": "American",
            "gpa": 3.5,
            "gre_total": 320,
            "gre_v": 160,
            "gre_aw": 4.0,
        },
    ]
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda pages=10, sleep_s=0.75: fake_rows)

    # Reset table
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute("DELETE FROM applicants;")

    app = create_app({"TESTING": True})
    client = app.test_client()

    # Pull twice with the same rows
    assert client.post("/pull-data").status_code == 200
    assert client.post("/pull-data").status_code == 200

    # Still only 2 rows because ON CONFLICT(p_id) upserts
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        count = conn.execute("SELECT COUNT(*) FROM applicants;").fetchone()[0]
        assert count == 2
@pytest.mark.db
def test_get_analysis_results_returns_expected_keys():
    from src.app import get_analysis_results

    results = get_analysis_results()

    expected_keys = {
        "q1", "q2", "q3_counts", "q3_avgs", "q4", "q5", "q6",
        "q7", "q8", "q9", "q10a", "q10b",
    }
    assert expected_keys.issubset(results.keys())
