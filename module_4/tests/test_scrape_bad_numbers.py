import pytest
import src.scrape as s

@pytest.mark.integration
def test_extract_fields_bad_numeric_branches():
    record = {
        "raw_lines": [
            "Test University January 31, 2026 Accepted",
            "Fall 2026 International GPA X.Y GRE ABC GRE V ZZZ GRE AW Q",
        ],
        "html_rows": [],
    }

    out = s.extract_fields(record)

    # These should fail parsing and become None (hitting your ValueError branches)
    assert out["gpa"] is None
    assert out["gre_total"] is None
    assert out["gre_v"] is None
    assert out["gre_aw"] is None
