Maya Saleh
Module 3 - Database Queries Assignment Experiment
Due: 2/8/2026

Approach
1. Data Collection
   - Graduate admissions data was scraped from Grad Café using scraper developed in Module 2.
   - Only recent pages are scraped when requested to avoid re-downloading all past entries.

2. Data Storage
   - Cleaned data is loaded into a PostgreSQL database using `psycopg`.
   - A single table `applicants` is used, with `p_id` as the key.
   - New data is inserted using UPSERT logic to prevent duplicate entries.

3. Data Analysis
   - SQL queries are written to answer required analytic questions.
   - Queries compute the answer to the Query Questions.

4. Web Application
   - A Flask web application displays the analysis results on a page.
   - A Pull Data button allows users to scrape new Grad Café data and add it to the database.
   - An Update Analysis button refreshes the results.

5. Limitations Analysis
   - A written discussion evaluates the limitations of analyzing anonymously self-submitted data.
   
How to Run:
1. Install: pip install -r requirements.txt
2. Set up PostGreSQL
3. Load initial data: python load_data.py
4. Run code Analysis: python query_data.py
5. Start Flask: python app.py
6. Vist webpage: http://127.0.0.1:5000