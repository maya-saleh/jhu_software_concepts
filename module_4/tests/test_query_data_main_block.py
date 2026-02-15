import os
import runpy
import pytest


@pytest.mark.db
def test_query_data_main_block_runs():
    # Runs the module as if: python -m src.query_data
    # (Uses DATABASE_URL you already set)
    runpy.run_module("src.query_data", run_name="__main__")
