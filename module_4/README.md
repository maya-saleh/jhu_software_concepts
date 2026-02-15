Name: Maya Saleh  
Module: Module 4 - Testing and Documentation Assignment 
Due: 2/15/2026

Approach

1. Data Collection  
   - Graduate admissions data is scraped from Grad Café using the web scraper developed in Module 2.  
   - Only recent pages are scraped when the Pull Data button is used, preventing unnecessary re-downloading of historical entries.

2. Data Storage  
   - Cleaned applicant data is stored in a PostgreSQL database using `psycopg`.  
   - A single table, `applicants`, is used to store all records, with `p_id` serving as the primary key.  
   - Data is inserted using UPSERT logic (`ON CONFLICT`) to avoid duplicate entries while allowing updates to existing records.

3. Data Analysis  
   - SQL queries are written to answer the required analytic questions for this module.  
   - Queries compute applicant counts, acceptance rates, GPA statistics, and demographic breakdowns directly within PostgreSQL.

4. Web Application  
   - A Flask web application displays analysis results on an `/analysis` webpage.  
   - A Pull Data button allows users to scrape new Grad Café data and insert it into the database.  
   - An Update Analysis button refreshes the displayed results without reloading data.

5. Limitations Analysis  
   - The analysis relies on anonymously self-submitted Grad Café data, which may be incomplete, inaccurate, or biased.  
   - Applicants may selectively report results, and not all programs or outcomes are equally represented.

How to Run

1. Install dependencies  
   ```bash
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
    


