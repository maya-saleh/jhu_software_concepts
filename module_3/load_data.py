import json
from datetime import datetime
import psycopg

DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "methJHU2026"
DB_HOST = "localhost"
DB_PORT = 5432
JSON_PATH = r"llm_extend_applicant_data (1).json"

#converts date string formats into a date object
def parse_date(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


#converts GPA/GRE strings into floats
def to_float(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("GPA", "").replace(":", "").strip()
    if "/" in s:
        s = s.split("/")[0].strip()
    try:
        return float(s)
    except ValueError:
        return None

def clean_text(value):
    if value is None:
        return None
    s = str(value)
    s = s.replace("\x00", "")
    s = s.strip()
    return s if s != "" else None

def main():    
    data = []
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))    
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True   
    insert_sql = """
    INSERT INTO applicants (
        p_id, program, comments, date_added, url, status, term,
        us_or_international, gpa, gre, gre_v, gre_aw, degree,
        llm_generated_program, llm_generated_university
    )
    VALUES (
        %(p_id)s, %(program)s, %(comments)s, %(date_added)s, %(url)s, %(status)s, %(term)s,
        %(us_or_international)s, %(gpa)s, %(gre)s, %(gre_v)s, %(gre_aw)s, %(degree)s,
        %(llm_generated_program)s, %(llm_generated_university)s
    )
    ON CONFLICT (p_id) DO UPDATE SET
        program = EXCLUDED.program,
        comments = EXCLUDED.comments,
        date_added = EXCLUDED.date_added,
        url = EXCLUDED.url,
        status = EXCLUDED.status,
        term = EXCLUDED.term,
        us_or_international = EXCLUDED.us_or_international,
        gpa = EXCLUDED.gpa,
        gre = EXCLUDED.gre,
        gre_v = EXCLUDED.gre_v,
        gre_aw = EXCLUDED.gre_aw,
        degree = EXCLUDED.degree,
        llm_generated_program = EXCLUDED.llm_generated_program,
        llm_generated_university = EXCLUDED.llm_generated_university;
    """

    inserted = 0

   
    with conn.cursor() as cur:
        for rec in data:            
            if not isinstance(rec, dict):
                continue            
            row = {
                "p_id": None,
                "program": clean_text(rec.get("program")),
                "comments": clean_text(rec.get("comments")),
                "date_added": parse_date(rec.get("date_added")),
                "url": clean_text(rec.get("url")),
                "status": clean_text(rec.get("applicant_status")),
                "term": clean_text(rec.get("semester_year_start")),
                "us_or_international": clean_text(rec.get("citizenship")),
                "gpa": to_float(rec.get("gpa")),
                "gre": to_float(rec.get("gre")),
                "gre_v": to_float(rec.get("gre_v")),
                "gre_aw": to_float(rec.get("gre_aw")),
                "degree": clean_text(rec.get("masters_or_phd")),
                "llm_generated_program": clean_text(rec.get("llm-generated-program")),
                "llm_generated_university": clean_text(rec.get("llm-generated-university")),
            }
           
            url = row["url"] or ""
            try:
                row["p_id"] = int(url.rstrip("/").split("/")[-1])
            except ValueError:
                continue

            
            cur.execute(insert_sql, row)
            inserted += 1

    conn.close()
    print(f"Upserted {inserted} rows into applicants.")


if __name__ == "__main__":
    main()
