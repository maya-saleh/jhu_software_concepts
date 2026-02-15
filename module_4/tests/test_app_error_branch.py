import pytest

@pytest.mark.buttons
def test_pull_data_handles_exception(monkeypatch):
    import src.scrape as scrape
    from src.app import create_app

    # Force the scraper to raise so your except block runs
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(scrape, "scrape_recent_pages", boom)

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.post("/pull-data")
    # your route currently returns JSON ok/busy codes; accept either
    assert resp.status_code in (200, 409)
