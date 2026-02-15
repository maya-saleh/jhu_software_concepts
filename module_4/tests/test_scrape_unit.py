import pytest
import urllib.request

import src.scrape as scrape


@pytest.mark.db
def test_build_survey_url():
    assert scrape.build_survey_url(3).endswith("?page=3")


@pytest.mark.db
def test_scrape_one_uses_urlopen(monkeypatch):
    # Fake urlopen() response object
    class FakeResp:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def read(self): return b"<html>ok</html>"

    def fake_urlopen(req, timeout=30):
        return FakeResp()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    html = scrape.scrape_one("https://example.com")
    assert "ok" in html


@pytest.mark.db
def test_parse_and_extract_fields():
    html = """
    <html><body><table>
      <tr>
        <td>
          <a href="/result/111">link</a>
          MIT Computer Science Accepted January 31, 2026 Total comments
        </td>
      </tr>
      <tr><td>Fall 2026 International GPA 3.90 GRE 330 GRE V 165 GRE AW 5.0</td></tr>
      <tr><td>Open options This is a comment See More</td></tr>

      <tr>
        <td>
          <a href="/result/222">link</a>
          Stanford Computer Science Rejected February 1, 2026 Total comments
        </td>
      </tr>
      <tr><td>Fall 2026 American GPA 3.50 GRE 320 GRE V 160 GRE AW 4.0</td></tr>
      <tr><td>Another comment</td></tr>
    </table></body></html>
    """

    records = scrape.parse_survey_page(html)
    assert len(records) == 2

    one = scrape.extract_fields(records[0])
    assert one["entry_url"].startswith("https://www.thegradcafe.com/result/")
    assert one["date_added"] == "January 31, 2026"
    assert one["status"] == "Accepted"
    assert one["start_term"] == "Fall 2026"
    assert one["citizenship"] == "International"
    assert one["gpa"] == 3.9
    assert one["gre_total"] == 330
    assert one["gre_v"] == 165
    assert one["gre_aw"] == 5.0
    assert one["comments"] is not None


@pytest.mark.db
def test_scrape_recent_pages_no_network(monkeypatch):
    # Make scrape_one return deterministic HTML (no internet)
    html = """
    <html><body><table>
      <tr><td><a href="/result/111">link</a> MIT Accepted January 31, 2026 Total comments</td></tr>
      <tr><td>Fall 2026 International GPA 3.90 GRE 330 GRE V 165 GRE AW 5.0</td></tr>
      <tr><td>Comment</td></tr>
    </table></body></html>
    """
    monkeypatch.setattr(scrape, "scrape_one", lambda url: html)
    monkeypatch.setattr(scrape.time, "sleep", lambda s: None)  # no sleeping

    entries = scrape.scrape_recent_pages(pages=2, sleep_s=0.0)
    assert len(entries) == 2  # 1 record per page * 2 pages
    assert entries[0]["source_page"] in (1, 2)
    assert entries[1]["source_page"] in (1, 2)
