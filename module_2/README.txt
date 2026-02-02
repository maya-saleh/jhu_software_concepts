Maya Saleh (msaleh18)
Module 2 - Assignment: Web Scraping 
Due: 2/1/2026

Approach:
- Verified robots.txt permissions for thegradcafe.com and documented compliance
- Implemented a web scraper using urllib and BeautifulSoup
- Used pagination to collect 30,000 applicant records
- Implemented polite scraping with delays, checkpointing, and resume support
- Parsed structured HTML table rows into applicant records
- Extracted applicant status, dates, start term, citizenship, GPA, GRE (when available),
  comments, and entry URLs
- Stored raw scraped data in applicant_data_full.json
- Cleaned and structured the dataset in clean.py
- Split program and university fields using heuristics
- Further standardized program and university names using a locally hosted LLM
- Preserved original raw fields for traceability and reproducibility

Known Bugs/Notes:
- When running the LLM standardizer, it was successfully set up and executed, however it did not complete in a reasonable time. It ran for several hours and due to hardware limitations and since it is now past the due date, it was terminated. The commands are correct and it should complete on a machine with sufficient CPU/RAM requirements