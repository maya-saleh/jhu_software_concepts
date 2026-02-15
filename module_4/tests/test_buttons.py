import pytest


@pytest.mark.buttons
def test_post_pull_data_returns_200_when_not_busy(monkeypatch):
    from src.app import create_app
    import src.scrape as scrape

    # Fake scraper: return no records quickly (no network)
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda pages=10, sleep_s=0.75: [])

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.post("/pull-data")

    assert resp.status_code in (200, 202)
@pytest.mark.buttons
def test_post_update_analysis_returns_200_when_not_busy():
    from src.app import create_app

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.post("/update-analysis")

    assert resp.status_code == 200
@pytest.mark.buttons
def test_busy_gating_update_analysis_returns_409(monkeypatch):
    from src.app import create_app
    import src.app as app_module

    app = create_app({"TESTING": True})
    client = app.test_client()

    # Force busy state AFTER app creation (create_app resets it when TESTING=True)
    monkeypatch.setattr(app_module, "pull_data_running", True)

    resp = client.post("/update-analysis")
    assert resp.status_code == 409
    assert resp.get_json() == {"busy": True}
@pytest.mark.buttons
def test_busy_gating_pull_data_returns_409(monkeypatch):
    from src.app import create_app
    import src.app as app_module

    app = create_app({"TESTING": True})
    client = app.test_client()

    # Force busy AFTER app creation
    monkeypatch.setattr(app_module, "pull_data_running", True)

    resp = client.post("/pull-data")
    assert resp.status_code == 409
    assert resp.get_json() == {"busy": True}
