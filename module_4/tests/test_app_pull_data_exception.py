import pytest

@pytest.mark.buttons
def test_pull_data_exception_hits_except_and_finally(monkeypatch):
    from src.app import create_app
    import src.app as app_module
    import src.scrape as scrape

    # Make scrape raise so we hit:
    # except Exception as e:
    # finally: pull_data_running = False
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda *a, **k: (_ for _ in ()).throw(Exception("boom")))

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.post("/pull-data")
    assert resp.status_code == 200

    # confirm finally ran
    assert app_module.pull_data_running is False
