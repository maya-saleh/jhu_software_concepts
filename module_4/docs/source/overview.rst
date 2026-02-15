Overview & Setup
================


Grad Café Analytics is a Flask-based web application that pulls, stores,
and analyzes graduate admissions data from Grad Café. The system provides
a simple web interface for triggering data pulls and viewing summarized
analysis results.

The project is designed to be testable, documented, and extensible.

Running the Application
-----------------------

1. Ensure Python 3.11+ is installed.
2. Create and activate a virtual environment.
3. Install dependencies:

   ::

       pip install -r requirements.txt

4. Set required environment variables:

   ::

       DATABASE_URL=postgresql://user:password@localhost:5432/grad_cafe

5. Run the Flask application:

   ::

       python -m module_4.src.flask_app

Running Tests
-------------

This project uses **pytest** with required markers and 100% coverage.

To run all tests:

::

    pytest -m "web or buttons or analysis or db or integration"

To run only web-related tests:

::

    pytest -m web

Architecture Overview
---------------------

The system is composed of three layers:

- **Web Layer (Flask)**: Serves the Analysis page and handles user actions.
- **ETL Layer**: Pulls, cleans, and loads Grad Café data.
- **Database Layer (PostgreSQL)**: Stores normalized application records and
  supports analytical queries.