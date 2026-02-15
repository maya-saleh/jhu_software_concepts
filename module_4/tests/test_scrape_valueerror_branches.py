import pytest

@pytest.mark.db
def test_extract_fields_safe_int_float_none(monkeypatch):
    import src.scrape as scrape

    # Force conversions to fail
    monkeypatch.setattr(scrape, "safe_int", lambda s: None)
    monkeypatch.setattr(scrape, "safe_float", lambda s: None)

    record = {
        "raw_lines": [
            "Test University January 31, 2026 Accepted",
            "Fall 2026 International GPA 3.90 GRE 330 GRE V 165 GRE AW 5.0",
        ],
        "html_rows": [],
    }

    out = scrape.extract_fields(record)

    assert out["gpa"] is None
    assert out["gre_total"] is None
    assert out["gre_v"] is None
    assert out["gre_aw"] is None


@pytest.mark.db
def test_extract_fields_no_gpa_gre_present():
    import src.scrape as scrape

    record = {
        "raw_lines": [
            "Some School January 31, 2026 Accepted",
            "Fall 2026 International",   # no GPA/GRE strings
        ],
        "html_rows": [],
    }

    out = scrape.extract_fields(record)

    assert out["gpa"] is None
    assert out["gre_total"] is None
    assert out["gre_v"] is None
    assert out["gre_aw"] is None

