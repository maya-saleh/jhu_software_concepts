import io
import os
import runpy
import builtins
import pytest


@pytest.mark.db
def test_load_data_main_block_runs_without_db_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Make file read safe (0 records)
    monkeypatch.setattr(builtins, "open", lambda *a, **k: io.StringIO(""))

    runpy.run_module("src.load_data", run_name="__main__")
