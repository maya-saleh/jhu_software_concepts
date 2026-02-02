import json
import re
import os

INPUT_PATH = "module_2/applicant_data_full.json"
OUTPUT_PATH = "module_2/llm_extend_applicant_data.json"


def load_data(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(path: str, data: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def infer_degree(raw: str) -> str | None:
    raw = (raw or "").strip()
    if re.search(r"\bphd\b", raw, re.IGNORECASE):
        return "PhD"
    if re.search(r"\bmasters\b|\bms\b|\bma\b|\bmeng\b|\bmsc\b", raw, re.IGNORECASE):
        return "Masters"
    return None


def split_university_program(raw: str) -> tuple[str | None, str | None]:
    """
    Improved heuristic split:
    1) Remove degree token to get 'before_degree'
    2) Handle common "University of X" (and similar) patterns first
    3) Otherwise anchor on University/College/Institute/etc.
    4) Fallback: first 3 words as university
    """
    raw = (raw or "").strip()
    if not raw:
        return None, None

    # Remove trailing degree token from the region we split on
    m_deg = re.search(r"\b(PhD|Masters|MS|MA|MEng|MSc)\b", raw, re.IGNORECASE)
    before_degree = raw[:m_deg.start()].strip() if m_deg else raw

    # Special-case common "X of Y" institution names
    # Examples:
    # - University of Washington
    # - University of Southern California
    # - The University of Texas at Austin
    # - Institute of Technology (less common but helps)
    of_patterns = [
        r"^(The\s+)?University\s+of\s+(?:[A-Z][A-Za-z&.\-]*)(?:\s+[A-Z][A-Za-z&.\-]*){0,4}",
        r"^(The\s+)?College\s+of\s+(?:[A-Z][A-Za-z&.\-]*)(?:\s+[A-Z][A-Za-z&.\-]*){0,4}",
        r"^(The\s+)?Institute\s+of\s+(?:[A-Z][A-Za-z&.\-]*)(?:\s+[A-Z][A-Za-z&.\-]*){0,4}",
        r"^(The\s+)?School\s+of\s+(?:[A-Z][A-Za-z&.\-]*)(?:\s+[A-Z][A-Za-z&.\-]*){0,4}",
    ]

    for pat in of_patterns:
        m = re.search(pat, before_degree)
        if m:
            university = m.group(0).strip()
            program = before_degree[len(university):].strip() or None
            return university, program

    # Anchor split on common institution words (works for "Ohio State University", "MIT", etc.)
    uni_anchor = re.search(
        r".*\b(University|College|Institute|School|Technolog(y|ies)|Polytechnic)\b",
        before_degree
    )
    if uni_anchor:
        university = uni_anchor.group(0).strip()
        program = before_degree[len(university):].strip() or None
        return university, program

    # Fallback: first 3 words as university
    parts = before_degree.split()
    if len(parts) <= 3:
        return before_degree, None

    university = " ".join(parts[:3])
    program = " ".join(parts[3:]).strip() or None
    return university, program


def clean_data(rows: list[dict]) -> list[dict]:
    cleaned: list[dict] = []

    for r in rows:
        status = r.get("status")
        decision_date = r.get("decision_date")  # like "18 Jan"
        date_added = r.get("date_added")        # like "February 01, 2026"
        raw = (r.get("program_university_raw") or "").strip()

        acceptance_date = None
        rejection_date = None
        waitlist_date = None

        if status == "Accepted":
            acceptance_date = decision_date
        elif status == "Rejected":
            rejection_date = decision_date
        elif status == "Waitlisted":
            waitlist_date = decision_date

        degree = infer_degree(raw)
        university, program_name = split_university_program(raw)

        out = {
            # Required categories (first-pass values; improved later by llm_hosting)
            "program_name": program_name,
            "university": university,

            # Keep original for traceability (your assignment explicitly wants this)
            "program_university_raw": raw,

            # Not yet scraped from HTML rows in this version; placeholders for now
            "comments": r.get("comments"),
            "entry_url": r.get("entry_url"),

            # Existing / derived
            "date_added": date_added,
            "applicant_status": status,

            "acceptance_date": acceptance_date,
            "rejection_date": rejection_date,
            "waitlist_date": waitlist_date,

            "start_term": r.get("start_term"),

            # Citizenship
            "citizenship": r.get("citizenship"),

            # Degree
            "degree": degree,

            # Metrics (some present now, GRE fields will be parsed later)
            "gpa": r.get("gpa"),
            "gre_total": r.get("gre_total"),
            "gre_v": r.get("gre_v"),
            "gre_aw": r.get("gre_aw"),

            # Provenance
            "source_page": r.get("source_page"),
        }

        cleaned.append(out)

    return cleaned


def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Missing input file: {INPUT_PATH}")

    rows = load_data(INPUT_PATH)
    cleaned = clean_data(rows)
    save_data(OUTPUT_PATH, cleaned)

    print("Loaded:", len(rows))
    print("Wrote cleaned:", len(cleaned))
    print("Output:", OUTPUT_PATH)


if __name__ == "__main__":
    main()