import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import time
import os
import json
from datetime import datetime

TEST_URL = "https://www.thegradcafe.com/survey/index.php"  

def build_survey_url(page_num: int) -> str:
    return f"https://www.thegradcafe.com/survey/index.php?page={page_num}"
    
def scrape_one(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JHU-Module2-Scraper/1.0)"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    return html
    
def parse_survey_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    starts = []
    for idx, row in enumerate(rows):
        t = row.get_text(" ", strip=True).lower()
        if "total comments" in t:
            starts.append(idx)

    records = []
    for k, start_idx in enumerate(starts):
        end_idx = starts[k + 1] if k + 1 < len(starts) else len(rows)
        chunk_rows = rows[start_idx:end_idx]

        # Save both: readable lines + the actual bs4 row objects
        chunk_text = [r.get_text(" ", strip=True) for r in chunk_rows]

        records.append({
            "raw_lines": chunk_text,
            "html_rows": chunk_rows,   # keep the actual <tr> elements
        })

    return records

def extract_fields(record: dict) -> dict:
    raw_lines = record.get("raw_lines", [])
    html_rows = record.get("html_rows", [])

    main = raw_lines[0] if len(raw_lines) > 0 else ""
    details = raw_lines[1] if len(raw_lines) > 1 else ""

    # ---- entry_url: first link that looks like /result/<id> ----
    entry_url = None
    if html_rows:
        a_tags = html_rows[0].find_all("a", href=True)
        for a in a_tags:
            href = a["href"]
            if "/result/" in href:
                if href.startswith("http"):
                    entry_url = href
                else:
                    entry_url = "https://www.thegradcafe.com" + href
                break

    # ---- comments: usually in later rows in the chunk (not always present) ----
    comments = None
    if len(raw_lines) >= 3:
        # Many chunks have a comment-only line; join the leftover lines
        leftover = " ".join(raw_lines[2:]).strip()
        if leftover:
            # remove repeated UI words if they show up
            leftover = re.sub(r"\b(Open options|See More|Report|Total comments)\b", "", leftover, flags=re.IGNORECASE).strip()
            comments = leftover or None

    # ---- Date added: Month DD, YYYY ----
    m_date = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2},\s+\d{4}",
        main
    )
    date_added = m_date.group(0) if m_date else None

    # ---- Status + decision date fragment ----
    m_status = re.search(
        r"\b(Accepted|Rejected|Wait listed|Waitlisted|Interview)\b\s+on\s+(\d{1,2}\s+[A-Za-z]{3})",
        main,
        re.IGNORECASE
    )
    status = None
    decision_date = None
    if m_status:
        status = m_status.group(1).replace("Wait listed", "Waitlisted").title()
        decision_date = m_status.group(2)

    # ---- Term ----
    m_term = re.search(r"\b(Fall|Spring|Summer|Winter)\s+\d{4}\b", details)
    start_term = m_term.group(0) if m_term else None

    # ---- Citizenship ----
    citizenship = None
    if re.search(r"\bInternational\b", details, re.IGNORECASE):
        citizenship = "International"
    elif re.search(r"\bAmerican\b", details, re.IGNORECASE):
        citizenship = "American"

    # ---- GPA ----
    m_gpa = re.search(r"\bGPA\s*([0-4]\.\d{1,2})\b", details)
    gpa = float(m_gpa.group(1)) if m_gpa else None

    # ---- GRE (common patterns: "GRE 330", "GRE V 160", "GRE AW 4.5") ----
    gre_total = None
    gre_v = None
    gre_aw = None

    m_gre_total = re.search(r"\bGRE\s*([2-3]\d{2})\b", details, re.IGNORECASE)
    if m_gre_total:
        gre_total = int(m_gre_total.group(1))

    m_gre_v = re.search(r"\bGRE\s*V\s*(\d{3})\b", details, re.IGNORECASE)
    if m_gre_v:
        gre_v = int(m_gre_v.group(1))

    m_gre_aw = re.search(r"\bGRE\s*AW\s*([0-6](?:\.\d)?)\b", details, re.IGNORECASE)
    if m_gre_aw:
        gre_aw = float(m_gre_aw.group(1))

    # ---- Program+University raw ----
    program_university_raw = main
    if date_added and date_added in main:
        program_university_raw = main.split(date_added)[0].strip()

    return {
        "program_university_raw": program_university_raw,
        "date_added": date_added,
        "status": status,
        "decision_date": decision_date,
        "start_term": start_term,
        "citizenship": citizenship,
        "gpa": gpa,
        "gre_total": gre_total,
        "gre_v": gre_v,
        "gre_aw": gre_aw,
        "comments": comments,
        "entry_url": entry_url,
    }

def scrape_pages(start_page: int, end_page: int, output_path: str, sleep_s: float = 0.75, checkpoint_every: int = 25) -> list[dict]:
    entries = load_existing(output_path)

    # resume: figure out the last completed page (based on max source_page)
    last_page = 0
    if entries:
        last_page = max(e.get("source_page", 0) for e in entries if isinstance(e, dict))
    page = max(start_page, last_page + 1)

    print(f"Starting scrape at page {page} (last_page={last_page}, already_saved={len(entries)})")

    while page <= end_page:
        url = build_survey_url(page)

        try:
            html = scrape_one(url)
            records = parse_survey_page(html)
            for rec in records:
                entry = extract_fields(rec)
                entry["source_page"] = page
                entries.append(entry)
            print(f"page {page}: +{len(records)} records (running_total {len(entries)})")
        except Exception as e:
            print(f"ERROR on page {page}: {e}  (skipping)")
        
        # checkpoint save
        if (page % checkpoint_every) == 0:
            save_entries(output_path, entries)
            print(f"Checkpoint saved at page {page} -> {output_path}")

        time.sleep(sleep_s)
        page += 1

    save_entries(output_path, entries)
    print(f"Final save -> {output_path} (entries={len(entries)})")
    return entries

def scrape_until_target(target_entries: int, output_path: str, start_page: int = 1,
                        sleep_s: float = 0.75, checkpoint_every: int = 25) -> list[dict]:
    entries = load_existing(output_path)

    last_page = 0
    if entries:
        last_page = max(e.get("source_page", 0) for e in entries if isinstance(e, dict))

    page = max(start_page, last_page + 1)
    print(f"Starting scrape at page {page} (last_page={last_page}, already_saved={len(entries)})")
    print(f"Target entries: {target_entries}")

    while len(entries) < target_entries:
        url = build_survey_url(page)

        try:
            html = scrape_one(url)
            records = parse_survey_page(html)

            for rec in records:
                entry = extract_fields(rec["raw_lines"])
                entry["source_page"] = page
                entries.append(entry)

            print(f"page {page}: +{len(records)} records (running_total {len(entries)})")

        except Exception as e:
            print(f"ERROR on page {page}: {e}  (skipping)")

        if (page % checkpoint_every) == 0:
            save_entries(output_path, entries)
            print(f"Checkpoint saved at page {page} -> {output_path}")

        time.sleep(sleep_s)
        page += 1

    save_entries(output_path, entries)
    print(f"Target reached. Final save -> {output_path} (entries={len(entries)})")
    return entries

def load_existing(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_entries(path: str, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def main():
    html = scrape_one(build_survey_url(1))
    records = parse_survey_page(html)
    entry0 = extract_fields(records[0])
    print(entry0)

if __name__ == "__main__":
     main()