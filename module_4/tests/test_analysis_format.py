import re
import pytest


@pytest.mark.analysis
def test_analysis_page_has_answer_labels_and_two_decimal_percentages():
    from src.app import create_app

    app = create_app({"TESTING": True})
    client = app.test_client()

    resp = client.get("/analysis")
    assert resp.status_code == 200

    html = resp.get_data(as_text=True)

    # At least one Answer label exists
    assert "Answer" in html

    # Find any percent-like occurrences
    any_percent = re.findall(r"\b\d+(?:\.\d+)?%\b", html)

    # If percentages exist, they must all be exactly two decimals (e.g., 39.28%)
    if any_percent:
        bad = [p for p in any_percent if not re.fullmatch(r"\d+\.\d{2}%", p)]
        assert bad == [], f"Percentages not formatted with two decimals: {bad}"

