import pytest
import src.load_data as ld


@pytest.mark.db
def test_load_data_helpers_edge_cases():
    # parse_date edge cases
    assert ld.parse_date(None) is None
    assert ld.parse_date("") is None
    assert ld.parse_date("not a date") is None
    assert ld.parse_date("2026-01-31").isoformat() == "2026-01-31"
    assert ld.parse_date("02/01/2026").isoformat() == "2026-02-01"

    # to_float edge cases
    assert ld.to_float(None) is None
    assert ld.to_float("") is None
    assert ld.to_float("GPA: 3.90") == 3.9
    assert ld.to_float("3.75/4.00") == 3.75
    assert ld.to_float("nope") is None

    # clean_text edge cases
    assert ld.clean_text(None) is None
    assert ld.clean_text("") is None
    assert ld.clean_text(" \x00 hi \x00 ") == "hi"
