import pytest
import src.scrape as scrape

@pytest.mark.db
def test_safe_int_and_safe_float_cover_error_branches():
    assert scrape.safe_int("123") == 123
    assert scrape.safe_int("nope") is None     # covers ValueError
    assert scrape.safe_int(None) is None       # covers TypeError

    assert scrape.safe_float("3.14") == 3.14
    assert scrape.safe_float("nope") is None   # covers ValueError
    assert scrape.safe_float(None) is None     # covers TypeError
