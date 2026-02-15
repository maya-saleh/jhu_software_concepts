import urllib.request
from bs4 import BeautifulSoup
import time
import re

BASE_URL = "https://www.thegradcafe.com/survey/index.php"

def build_survey_url(page_num: int) -> str:
    """Build the GradCafe survey URL for a specific page number."""
    return f"{BASE_URL}?page={page_num}"


def scrape_one(url: str) -> str:
    """Download HTML for a single survey page and return it as text."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (JHU-Module-Scraper)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_survey_page(html: str) -> list[dict]:
    """
    Parse a survey page HTML into a list of "record chunks".
    Each record chunk is a dict:
      - raw_lines: readable text lines extracted from the record rows
      - html_rows: the actual <tr> rows for link extraction, etc.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    #GradCafe results are grouped
    starts = []
    for idx, row in enumerate(rows):
        t = row.get_text(" ", strip=True).lower()
        if "total comments" in t:
            starts.append(idx)

    records = []
    for k, start_idx in enumerate(starts):
        end_idx = starts[k + 1] if k + 1 < len(starts) else len(rows)
        chunk_rows = rows[start_idx:end_idx]

        chunk_text = [r.get_text(" ", strip=True) for r in chunk_rows]

        records.append({
            "raw_lines": chunk_text,
            "html_rows": chunk_rows,
        })

    return records

def safe_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None

def safe_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

def extract_fields(record: dict) -> dict:
    """
    Convert one parsed record into a normalized dict your Flask app can insert into Postgres.
    Keys match what app.py expects.
    """
    raw_lines = record.get("raw_lines", [])
    html_rows = record.get("html_rows", [])

    main = raw_lines[0] if len(raw_lines) > 0 else ""
    details = raw_lines[1] if len(raw_lines) > 1 else ""

    #entry_url
    entry_url = None
    if html_rows:
        a_tags = html_rows[0].find_all("a", href=True)
        for a in a_tags:
            href = a["href"]
            if "/result/" in href:
                entry_url = href if href.startswith("http") else ("https://www.thegradcafe.com" + href)
                break

    #comments
    comments = None
    if len(raw_lines) >= 3:
        leftover = " ".join(raw_lines[2:]).strip()
        if leftover:
            leftover = re.sub(
                r"\b(Open options|See More|Report|Total comments)\b",
                "",
                leftover,
                flags=re.IGNORECASE
            ).strip()
            comments = leftover or None

    #Date added
    m_date = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
        main
    )
    date_added = m_date.group(0) if m_date else None

    #Status & decision date    
    m_status = re.search(
        r"\b(Accepted|Rejected|Wait listed|Waitlisted|Interview)\b",
        main,
        re.IGNORECASE
    )
    status = m_status.group(1).replace("Wait listed", "Waitlisted").title() if m_status else None

    #Term
    m_term = re.search(r"\b(Fall|Spring|Summer|Winter)\s+\d{4}\b", details)
    start_term = m_term.group(0) if m_term else None

    #Citizenship
    citizenship = None
    if re.search(r"\bInternational\b", details, re.IGNORECASE):
        citizenship = "International"
    elif re.search(r"\bAmerican\b", details, re.IGNORECASE):
        citizenship = "American"

    #GPA
    gpa = None
    m_gpa = re.search(r"\bGPA\s*([0-4]\.\d{1,2})\b", details)
    if m_gpa:
        gpa = safe_float(m_gpa.group(1))
    

    #GRE fields
    gre_total = None
    gre_v = None
    gre_aw = None

    m_gre_total = re.search(r"\bGRE\s*([2-3]\d{2})\b", details, re.IGNORECASE)
    if m_gre_total:
        gre_total = safe_int(m_gre_total.group(1))

    m_gre_v = re.search(r"\bGRE\s*V\s*(\d{3})\b", details, re.IGNORECASE)
    if m_gre_v:
        gre_v = safe_int(m_gre_v.group(1))

    m_gre_aw = re.search(r"\bGRE\s*AW\s*([0-6](?:\.\d)?)\b", details, re.IGNORECASE)
    if m_gre_aw:
        gre_aw = safe_float(m_gre_aw.group(1))



    #Program/university
    program_university_raw = main
    if date_added and date_added in main:
        program_university_raw = main.split(date_added)[0].strip()

    return {
        "program_university_raw": program_university_raw,
        "date_added": date_added,
        "status": status,
        "start_term": start_term,
        "citizenship": citizenship,
        "gpa": gpa,
        "gre_total": gre_total,
        "gre_v": gre_v,
        "gre_aw": gre_aw,
        "comments": comments,
        "entry_url": entry_url,
    }

def scrape_recent_pages(pages: int = 5, sleep_s: float = 0.75) -> list[dict]:
    """
    Scrape the first N pages (most recent results) and return extracted entries.
    This is the function your Flask Pull Data button calls.
    """
    entries = []

    for page in range(1, pages + 1):
        url = build_survey_url(page)
        html = scrape_one(url)
        records = parse_survey_page(html)

        for rec in records:
            entry = extract_fields(rec)
            entry["source_page"] = page
            entries.append(entry)

        print(f"scrape_recent_pages: page {page} -> +{len(records)} records (total {len(entries)})")
        time.sleep(sleep_s)

    return entries



if __name__ == "__main__":
    data = scrape_recent_pages(pages=1)
    