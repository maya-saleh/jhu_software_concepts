from flask import Flask, render_template, redirect, url_for
import psycopg
from datetime import datetime
from . import scrape
import os

DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "..."
DB_HOST = "localhost"
DB_PORT = 5432


def create_app(test_config=None):
    app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)


    if test_config:
        app.config.update(test_config)
    global pull_data_running, pull_data_status_msg
    if app.config.get("TESTING"):
        pull_data_running = False
        pull_data_status_msg = ""


    
    @app.route("/analysis")
    def analysis():
        results = get_analysis_results()
        return render_template(
            "analysis.html",
            results=results,
            pull_data_running=pull_data_running,
            pull_data_status_msg=pull_data_status_msg
    )
    @app.route("/pull-data", methods=["POST"])
    def pull_data():
        """Triggered by the Pull Data button: scrape recent pages and upsert into DB."""
        global pull_data_running, pull_data_status_msg
        if pull_data_running:
            pull_data_status_msg = "Pull Data is already running. Please wait."
            return {"busy": True}, 409

        pull_data_running = True

        try:
            pull_data_status_msg = "Pulling new data from Grad Café... Please wait."
            new_entries = scrape.scrape_recent_pages(pages=10, sleep_s=0.75)

            pull_data_status_msg = f"Scraped {len(new_entries)} records. Upserting into database..."

            conn = get_db_conn()

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

            upserted = 0
            with conn.cursor() as cur:
                for e in new_entries:
                    url = e.get("entry_url")
                    if not url:
                        continue

                    try:
                        p_id = int(url.rstrip("/").split("/")[-1])
                    except ValueError:
                        continue

                    row = {
                        "p_id": p_id,
                        "program": clean_text(e.get("program_university_raw")),
                        "comments": clean_text(e.get("comments")),
                        "date_added": parse_date(e.get("date_added")),
                        "url": clean_text(url),
                        "status": clean_text(e.get("status")),
                        "term": clean_text(e.get("start_term")),
                        "us_or_international": clean_text(e.get("citizenship")),
                        "gpa": e.get("gpa"),
                        "gre": e.get("gre_total"),
                        "gre_v": e.get("gre_v"),
                        "gre_aw": e.get("gre_aw"),                    
                        "degree": None,
                        "llm_generated_program": None,
                        "llm_generated_university": None,
                    }

                    cur.execute(insert_sql, row)
                    upserted += 1

            conn.close()

            pull_data_status_msg = (
                f"Done. Scraped {len(new_entries)} records and upserted {upserted} rows. "
                f"Click 'Update Analysis' to refresh."
            )

        except Exception as e:
            pull_data_status_msg = f"Error while pulling data: {e}"

        finally:
            pull_data_running = False

        return {"ok": True}, 200




    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        """Triggered by Update Analysis button: just reloads the page with latest DB results."""
        global pull_data_status_msg

        if pull_data_running:
            pull_data_status_msg = "Pull Data is currently running, so analysis will not update yet."
            return {"busy": True}, 409


        pull_data_status_msg = "Analysis updated with the latest available data."
        return {"ok": True}, 200



    # IMPORTANT: move/register your existing routes here
    # e.g. @app.get("/analysis") ...

    return app

def get_db_conn():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return psycopg.connect(db_url)
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )



def parse_date(value):
    """Parse dates like 'January 31, 2026' into a Python date object, or return None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def clean_text(value):
    """Remove NUL bytes (Postgres doesn't allow them), trim whitespace, and convert empty strings to None."""
    if value is None:
        return None
    s = str(value).replace("\x00", "").strip()
    return s if s else None


def get_analysis_results():
    """Runs all SQL queries and returns a results dictionary for the webpage."""
    conn = get_db_conn()


    results = {}

    with conn.cursor() as cur:
        #Q1: Fall 2026 applicant count
        cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        results["q1"] = cur.fetchone()[0]

        #Q2: Percent international
        cur.execute("""
            SELECT ROUND(
                100.0 * SUM(CASE WHEN us_or_international = 'International' THEN 1 ELSE 0 END)
                / COUNT(*), 2)
            FROM applicants;
        """)
        results["q2"] = float(cur.fetchone()[0])

        #Q3
        cur.execute("""
            SELECT
                COUNT(gpa), COUNT(gre), COUNT(gre_v), COUNT(gre_aw),
                ROUND(AVG(gpa)::numeric, 2),
                ROUND(AVG(gre)::numeric, 2),
                ROUND(AVG(gre_v)::numeric, 2),
                ROUND(AVG(gre_aw)::numeric, 2)
            FROM applicants;
        """)
        gpa_ct, gre_ct, grev_ct, greaw_ct, avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()

        results["q3_counts"] = {"gpa": gpa_ct, "gre": gre_ct, "gre_v": grev_ct, "gre_aw": greaw_ct}
        results["q3_avgs"] = {
            "gpa": float(avg_gpa) if avg_gpa is not None else None,
            "gre": float(avg_gre) if avg_gre is not None else None,
            "gre_v": float(avg_gre_v) if avg_gre_v is not None else None,
            "gre_aw": float(avg_gre_aw) if avg_gre_aw is not None else None,
        }
        #Q4
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term='Fall 2026' AND us_or_international='American' AND gpa IS NOT NULL;
        """)
        q4 = cur.fetchone()[0]
        results["q4"] = float(q4) if q4 is not None else None

        #Q5
        cur.execute("""
            SELECT ROUND(
                100.0 * SUM(CASE WHEN status ILIKE 'accept%' THEN 1 ELSE 0 END)
                / COUNT(*), 2)
            FROM applicants
            WHERE term='Fall 2026';
        """)
        results["q5"] = float(cur.fetchone()[0])

        #Q6
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term='Fall 2026' AND status ILIKE 'accept%' AND gpa IS NOT NULL;
        """)
        q6 = cur.fetchone()[0]
        results["q6"] = float(q6) if q6 is not None else None

        #Q7
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE degree ILIKE 'master%'
              AND (program ILIKE '%johns hopkins%' OR program ILIKE '%jhu%' OR program ILIKE '%john hopkins%')
              AND (program ILIKE '%computer science%' OR program ILIKE '%comp sci%' OR program ILIKE '%cs%');
        """)
        results["q7"] = cur.fetchone()[0]

        #Q8
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE date_added >= DATE '2026-01-01'
              AND date_added <  DATE '2027-01-01'
              AND status ILIKE 'accept%'
              AND degree ILIKE 'phd%'
              AND (program ILIKE '%computer science%' OR program ILIKE '%comp sci%' OR program ILIKE '%cs%')
              AND (
                    program ILIKE '%georgetown%'
                 OR program ILIKE '%massachusetts institute of technology%'
                 OR program ILIKE '%mit%'
                 OR program ILIKE '%stanford%'
                 OR program ILIKE '%carnegie mellon%'
                 OR program ILIKE '%cmu%'
              );
        """)
        results["q8"] = cur.fetchone()[0]

        #Q9
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE date_added >= DATE '2026-01-01'
              AND date_added <  DATE '2027-01-01'
              AND status ILIKE 'accept%'
              AND degree ILIKE 'phd%'
              AND llm_generated_program ILIKE '%computer science%'
              AND llm_generated_university IN (
                    'Georgetown University',
                    'Massachusetts Institute of Technology',
                    'Stanford University',
                    'Carnegie Mellon University'
              );
        """)
        results["q9"] = cur.fetchone()[0]

        #Q10
        cur.execute("""
            SELECT
                us_or_international,
                ROUND(100.0 * SUM(CASE WHEN status ILIKE 'accept%' THEN 1 ELSE 0 END) / COUNT(*), 2)
            FROM applicants
            WHERE term='Fall 2026'
            GROUP BY us_or_international
            ORDER BY us_or_international;
        """)
        results["q10a"] = [(row[0], float(row[1])) for row in cur.fetchall()]

        #Q11
        cur.execute("""
            SELECT
                CASE WHEN status ILIKE 'accept%' THEN 'Accepted' ELSE 'Not Accepted' END,
                ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term='Fall 2026' AND gpa IS NOT NULL
            GROUP BY 1
            ORDER BY 1;
        """)
        results["q10b"] = [(row[0], float(row[1])) for row in cur.fetchall()]

    conn.close()
    return results



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

