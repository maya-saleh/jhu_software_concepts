Maya Saleh (msaleh18)
Module 2 - Assignment: Web Scraping 
Due: 2/1/2026

Approach:
- Verified robots.txt permissions for thegradcafe.com and documented compliance
- Implemented a web scraper using urllib and BeautifulSoup
- Used pagination to collect over 30,000 applicant records
- Implemented polite scraping with delays, checkpointing, and resume support
- Parsed structured HTML table rows into applicant records
- Extracted applicant status, dates, start term, citizenship, GPA, GRE (when available),
  comments, and entry URLs
- Stored raw scraped data in applicant_data_full.json
- Cleaned and structured the dataset in clean.py
- Split program and university fields using heuristics
- Further standardized program and university names using a locally hosted LLM
- Preserved original raw fields for traceability and reproducibility

Notes:
- When running the LLM standardizer, output must be redirected to a new file to avoid
truncating the input JSON