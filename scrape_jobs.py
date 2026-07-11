"""
scrape_jobs.py (v6-debug) -- DIAGNOSTIC ONLY. Does not delete or push
records. Prints jobspy's raw dataframe columns and per-row values for
job_url_direct / date_posted so we can test whether job_url_direct can be
used as an Easy Apply signal (external application link present => NOT
Easy Apply) and re-check whether date_posted is populated right now.
"""

import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone

import requests
from jobspy import scrape_jobs

# ---- Config ----
SITES = ["linkedin"]
SEARCH_TERMS = [
    "Delivery Manager",
    "Program Manager",
]
LOCATION = "Bengaluru, Karnataka, India"
RESULTS_PER_TERM = 5
HOURS_OLD = 24
MAX_NEW_PER_RUN = 10

IST = timezone(timedelta(hours=5, minutes=30))

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}


def main():
    for term in SEARCH_TERMS:
        print(f"Scraping {'+'.join(SITES)} for: {term}")
        try:
            jobs = scrape_jobs(
                site_name=SITES,
                search_term=term,
                location=LOCATION,
                results_wanted=RESULTS_PER_TERM,
                hours_old=HOURS_OLD,
                country_indeed="india",
                linkedin_fetch_description=True,
            )
        except Exception as e:
            print(f"Error scraping '{term}': {e}", file=sys.stderr)
            continue

        if jobs is None or jobs.empty:
            print(f"No results for: {term}")
            continue

        print(f"DEBUG columns: {jobs.columns.tolist()}")
        for _, row in jobs.iterrows():
            desc = str(row.get("description") or "")
            print(
                "DEBUG row |",
                "title=", row.get("title"),
                "| company=", row.get("company"),
                "| job_url=", row.get("job_url"),
                "| job_url_direct=", (row.get("job_url_direct") if "job_url_direct" in row else "<no col>"),
                "| date_posted=", row.get("date_posted"),
                "| desc_len=", len(desc),
                "| desc_has_easy_apply_text=", ("easy apply" in desc.lower()),
            )

    print("DEBUG DONE -- no delete, no push in this diagnostic run.")


if __name__ == "__main__":
    main()
