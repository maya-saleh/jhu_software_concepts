import runpy
import pytest
import src.scrape as scrape

@pytest.mark.db
def test_extract_fields_hits_more_branches():
    # Build a record chunk matching extract_fields() expectations:
    record = {
        "raw_lines": [
            # main line: has date + status + some extra
            "Test University January 31, 2026 Accepted",
            # details line: has term + citizenship + GPA/GRE
            "Fall 2026 International GPA 3.90 GRE 330 GRE V 165 GRE AW 5.0",
            # comments lines
            "Total comments hello world",
        ],
        "html_rows": [],  # leave empty -> entry_url None branch
    }

    out = scrape.extract_fields(record)

    assert out["citizenship"] == "International"
    assert out["gpa"] == 3.9
    assert out["gre_total"] == 330
    assert out["gre_v"] == 165
    assert out["gre_aw"] == 5.0
    assert out["comments"] is not None

@pytest.mark.db
def test_scrape_main_block_runs_without_network(monkeypatch):
    # Patch scrape_recent_pages so the __main__ block doesn't hit the internet
    monkeypatch.setattr(scrape, "scrape_recent_pages", lambda pages=1, sleep_s=0.75: [])
    runpy.run_module("src.scrape", run_name="__main__")
