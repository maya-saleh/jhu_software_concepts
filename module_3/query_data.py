import psycopg

DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "methJHU2026"
DB_HOST = "localhost"
DB_PORT = 5432


def main():
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    with conn.cursor() as cur:

        #Q1- How many Fall 2026 applications?
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE term = 'Fall 2026';
        """)
        q1 = cur.fetchone()[0]
        print("Q1 - Number of Fall 2026 applications:", q1)

        #Q2- Percentage of international students (overall)
        cur.execute("""
            SELECT
                ROUND(
                    100.0 * SUM(CASE WHEN us_or_international = 'International' THEN 1 ELSE 0 END)
                    / COUNT(*),
                    2
                )
            FROM applicants;
        """)
        q2 = cur.fetchone()[0]
        print("Q2 - Percent International (overall):", q2, "%")

        #Q3- Average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics
        
        cur.execute("""
            SELECT
                COUNT(gpa)    AS gpa_count,
                COUNT(gre)    AS gre_count,
                COUNT(gre_v)  AS gre_v_count,
                COUNT(gre_aw) AS gre_aw_count,
                ROUND(AVG(gpa)::numeric, 2)    AS avg_gpa,
                ROUND(AVG(gre)::numeric, 2)    AS avg_gre_q,
                ROUND(AVG(gre_v)::numeric, 2)  AS avg_gre_v,
                ROUND(AVG(gre_aw)::numeric, 2) AS avg_gre_aw
            FROM applicants;
        """)
        gpa_ct, gre_ct, grev_ct, greaw_ct, avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()
        print("Q3 - Non-null counts -> GPA:", gpa_ct, "GRE:", gre_ct, "GRE_V:", grev_ct, "GRE_AW:", greaw_ct)
        print("Q3 - Avg GPA (provided):", avg_gpa)
        print("Q3 - Avg GRE Quant (provided):", avg_gre)
        print("Q3 - Avg GRE Verbal (provided):", avg_gre_v)
        print("Q3 - Avg GRE AW (provided):", avg_gre_aw)

        #Q4-Average GPA of American students in Fall 2026
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term = 'Fall 2026'
              AND us_or_international = 'American'
              AND gpa IS NOT NULL;
        """)
        q4 = cur.fetchone()[0]
        print("Q4 - Avg GPA of American students (Fall 2026):", q4)

        #Q5 - What percent of entries for Fall 2026 are Acceptances?
        cur.execute("""
            SELECT
                ROUND(
                    100.0 * SUM(CASE WHEN status ILIKE 'accept%' THEN 1 ELSE 0 END) / COUNT(*),
                    2
                )
            FROM applicants
            WHERE term = 'Fall 2026';
        """)
        q5 = cur.fetchone()[0]
        print("Q5 - Percent Acceptances (Fall 2026):", q5, "%")

        #Q6 - Average GPA of Fall 2026 applicants who are Acceptances
        cur.execute("""
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term = 'Fall 2026'
              AND status ILIKE 'accept%'
              AND gpa IS NOT NULL;
        """)
        q6 = cur.fetchone()[0]
        print("Q6 - Avg GPA of Acceptances (Fall 2026):", q6)

        #Q7 - How many entries are from applicants who applied to JHU for a masters degree in Computer Science?
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE degree ILIKE 'master%'
              AND (
                    program ILIKE '%johns hopkins%'
                 OR program ILIKE '%jhu%'
                 OR program ILIKE '%john hopkins%'
              )
              AND (
                    program ILIKE '%computer science%'
                 OR program ILIKE '%comp sci%'
                 OR program ILIKE '%cs%'
              );
        """)
        q7 = cur.fetchone()[0]
        print("Q7 - JHU Masters in Computer Science entries:", q7)

        #Q8 - How many entries from 2026 are acceptances from applicants who applied to Georgetown, MIT, Stanford, or CMU for a PhD in Computer Science? (original fields)
        cur.execute("""
            SELECT COUNT(*)
            FROM applicants
            WHERE date_added >= DATE '2026-01-01'
              AND date_added <  DATE '2027-01-01'
              AND status ILIKE 'accept%'
              AND degree ILIKE 'phd%'
              AND (
                    program ILIKE '%computer science%'
                 OR program ILIKE '%comp sci%'
                 OR program ILIKE '%cs%'
              )
              AND (
                    program ILIKE '%georgetown%'
                 OR program ILIKE '%massachusetts institute of technology%'
                 OR program ILIKE '%mit%'
                 OR program ILIKE '%stanford%'
                 OR program ILIKE '%carnegie mellon%'
                 OR program ILIKE '%cmu%'
              );
        """)
        q8 = cur.fetchone()[0]
        print("Q8 - 2026 Acceptances, PhD CS, target universities (original fields):", q8)

        #Q9 - Do the numbers for Q8 change if you use LLM Generated Fields?
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
        q9 = cur.fetchone()[0]
        print("Q9 - Same count using LLM fields:", q9)

        #Q10
        cur.execute("""
            SELECT
                us_or_international,
                ROUND(
                    100.0 * SUM(CASE WHEN status ILIKE 'accept%' THEN 1 ELSE 0 END)
                    / COUNT(*),
                    2
                ) AS acceptance_rate
            FROM applicants
            WHERE term = 'Fall 2026'
            GROUP BY us_or_international
            ORDER BY us_or_international;
        """)
        print("Q10A - Acceptance rate by citizenship (Fall 2026):")
        for row in cur.fetchall():
            print("   ", row)

        #Q11
        cur.execute("""
            SELECT
                CASE
                    WHEN status ILIKE 'accept%' THEN 'Accepted'
                    ELSE 'Not Accepted'
                END AS decision_group,
                ROUND(AVG(gpa)::numeric, 2) AS avg_gpa
            FROM applicants
            WHERE term = 'Fall 2026'
              AND gpa IS NOT NULL
            GROUP BY decision_group
            ORDER BY decision_group;
        """)
        print("Q10B - Avg GPA by decision group (Fall 2026):")
        for row in cur.fetchall():
            print("   ", row)

    conn.close()


if __name__ == "__main__":
    main()
