Name: Maya Saleh
Module: Module 4 - Testing and Documentation Assignment
Due: 2/15/2026

Approach:

1. Data Collection:
    - Graduate admissions data is scraped from Grad Café using the web scraper developed in Module 2.
    - Only recent pages are scraped when the Pull Data button is used, preventing unnecessary re-downloading of historical entries.

2. Data Storage:
    - Cleaned applicant data is stored in a PostgreSQL database using psycopg. 
    - A single table, applicants, is used to store all records, with p_id serving as the primary key.
    - Data is inserted using UPSERT logic (ON CONFLICT) to avoid duplicate entries while allowing updates to existing records.

3. Data Analysis:
    - SQL queries are written to answer the required analytic questions for this module. 
    - Queries compute applicant counts, acceptance rates, GPA statistics, and demographic breakdowns directly within PostgreSQL.

4. Web Application:
    - A Flask web application displays analysis results on an /analysis webpage. 
    - A Pull Data button scrapes new Grad Café data and inserts it into the database. 
    - An Update Analysis button refreshes the displayed results using the latest database contents.

5. Testing & CI:
    - The test suite is organized with pytest markers (web, buttons, analysis, db, integration) so the full suite runs with: pytest -m "web or buttons or analysis or db or integration". 
    - Tests verify the /analysis page renders required components (title text, buttons, “Answer:” labels) and ensure percentage formatting is always two decimals. 
    - Database tests confirm inserts/upserts work correctly, duplicate pulls do not duplicate rows, and required fields are written.
    - An end-to-end integration test validates the flow: pull → update → render.
    - GitHub Actions runs the same marked suite against a Postgres service container to ensure consistent CI results.

6. Limitations Analysis:
    - The analysis relies on anonymously self-submitted Grad Café data, which may be incomplete, inaccurate, or biased.
    - Applicants may selectively report results, and not all programs or outcomes are equally represented.

How to Run

1. Install dependencies  
   pip install -r module_4/requirements.txt
2. Set up PostgreSQL
3. Load initial data
    cd module_4
    python -m src.load_data
4. Run analysis logic
    python -m src.query_data
5. Start Flask Application
    python -m src.app
6. Visit Webpage
    http://127.0.0.1:5000/analysis
    
7. Documentation

Sphinx documentation for this project is published on Read the Docs:

https://jhu.readthedocs.io/en/latest/


