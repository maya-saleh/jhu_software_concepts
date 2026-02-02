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
    raw = (raw or "").strip()
    if not raw:
        return None, None

    # Remove degree token from the region we split on
    m_deg = re.search(r"\b(PhD|Masters|MS|MA|MEng|MSc)\b", raw, re.IGNORECASE)
    before_degree = raw[:m_deg.start()].strip() if m_deg else raw
    tokens = before_degree.split()

    # words that are very likely part of a PROGRAM, not part of the institution name
    discipline_words = {
        "Engineering", "Science", "Sciences", "Physics", "Chemistry", "Biology", "Biomedical",
        "Computer", "Computing", "Mathematics", "Math", "Statistics", "Economics", "Business",
        "Management", "Public", "Health", "Nursing", "Education", "Psychology", "Sociology",
        "Political", "Policy", "Law", "Medicine", "Medical", "Geology", "Geophysics", "Astronomy",
        "Civil", "Mechanical", "Electrical", "Industrial", "Aerospace", "Chemical", "Materials",
        "Data", "Information", "Neuroscience"
    }

    def is_cap(tok: str) -> bool:
        # allow A&M, UCLA, MIT, St., McGill, etc.
        return bool(re.match(r"^[A-Z][A-Za-z&.\-]*$", tok)) or tok.isupper()

    # Special handling: (The) University/College/Institute/School of X [at Y]
    starters = {"University", "College", "Institute", "School"}

    i = 0
    if len(tokens) >= 4 and tokens[0] == "The" and tokens[1] in starters and tokens[2] == "of":
        i = 1  # skip "The"

    if len(tokens) >= i + 3 and tokens[i] in starters and tokens[i + 1] == "of":
        j = i + 2  # start after "of"

        # build a candidate place-name with up to 3 capitalized tokens
        cap_count = 0
        while j < len(tokens) and cap_count < 3 and is_cap(tokens[j]):
            j += 1
            cap_count += 1

        # optional: "at <Cap> <Cap>"
        if j < len(tokens) and tokens[j] == "at":
            j2 = j + 1
            cap2 = 0
            while j2 < len(tokens) and cap2 < 2 and is_cap(tokens[j2]):
                j2 += 1
                cap2 += 1
            if cap2 > 0:
                j = j2

        # Now BACK OFF if we swallowed the program
        # Case A: program would be empty
        # Case B: university ends with a discipline word (likely program)
        while j > i + 2:
            university_candidate = " ".join(tokens[i:j]).strip()
            program_candidate = " ".join(tokens[j:]).strip() or None

            last_word = university_candidate.split()[-1] if university_candidate else ""
            if program_candidate is None or last_word in discipline_words:
                j -= 1
                continue

            return university_candidate, program_candidate

        # If we backed off all the way, fall through

    # Anchor split on institution words elsewhere (works for "Ohio State University ...")
    uni_anchor = re.search(
        r".*\b(University|College|Institute|School|Technolog(y|ies)|Polytechnic)\b",
        before_degree
    )
    if uni_anchor:
        university = uni_anchor.group(0).strip()
        program = before_degree[len(university):].strip() or None
        return university, program

    # Fallback: first 3 words as university
    if len(tokens) <= 3:
        return before_degree, None
    university = " ".join(tokens[:3])
    program = " ".join(tokens[3:]).strip() or None
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
            "comments": None,
            "entry_url": None,

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
            "gre_total": None,
            "gre_v": None,
            "gre_aw": None,

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