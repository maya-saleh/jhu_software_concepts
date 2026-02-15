Architecture
============

Web layer (Flask)
-----------------
- Routes live in ``src/app.py``.
- ``GET /analysis`` renders analysis results.
- ``POST /pull-data`` scrapes + upserts rows.
- ``POST /update-analysis`` refreshes results (with busy gating).

ETL layer
---------
- Scraping happens in ``src/scrape.py``.
- Loading/upserting happens in ``src/load_data.py`` (uses psycopg and UPSERT).
- Cleaning helpers are used to safely convert/normalize values.

DB layer
--------
- PostgreSQL stores all records in a single table ``applicants``.
- ``p_id`` is treated as the unique key for idempotency.
- Query logic (analysis results dictionary) lives in ``src/app.py`` (and/or ``src/query_data.py`` if present).