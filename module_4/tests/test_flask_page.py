import pytest


@pytest.mark.web
def test_app_factory_creates_app():
    # Update this import if your create_app lives somewhere else.
    from src.app import create_app

    app = create_app({"TESTING": True})
    assert app is not None


@pytest.mark.web
def test_get_analysis_returns_200():
    from src.app import create_app

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.get("/analysis")
    assert resp.status_code == 200

    html = resp.get_data(as_text=True)
    assert "Analysis" in html
    assert "Answer" in html


