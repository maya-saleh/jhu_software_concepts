import pytest
import runpy

@pytest.mark.integration
def test_app_main_block_runs(monkeypatch):
    # prevent actually starting a server
    import flask.app
    monkeypatch.setattr(flask.app.Flask, "run", lambda *a, **k: None)

    runpy.run_module("src.app", run_name="__main__")
