Testing Guide
=============

Markers
-------
All tests are marked with one or more of:
- web
- buttons
- analysis
- db
- integration

Run the entire suite using::

  pytest -m "web or buttons or analysis or db or integration"

UI selectors used in tests
--------------------------
The HTML includes stable selectors:
- ``data-testid="pull-data-btn"``
- ``data-testid="update-analysis-btn"``

UI Selectors
------------

The Flask analysis page exposes stable selectors for UI testing:

- ``data-testid="pull-data-btn"`` for the Pull Data button
- ``data-testid="update-analysis-btn"`` for the Update Analysis button

These selectors are used in web and integration tests to verify page behavior
without relying on fragile HTML structure.


Expected formatting
-------------------
- Analysis items include an ``Answer:`` label.
- Percentages render with two decimal places (e.g., ``39.28%``).

Fixtures / doubles
------------------
Network calls are not used in tests.
Scraping is mocked so tests are fast and deterministic.
