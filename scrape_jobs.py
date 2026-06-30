"""
LinkedIn job scraper for Amar's Job Hunt Dashboard.
Uses JobSpy (free, open-source) to pull LinkedIn postings with Easy Apply,
then pushes new (non-duplicate) listings into Airtable.

Run via GitHub Actions on a schedule. Requires env vars:
  AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
"""

import os
import sys
import time
import requests
from jobspy import scrape_jobs

# ---- Config ----
SEARCH_TERMS = [
    "Delivery Manager",
    "Program Manager",
    "Delivery Head",
    "Account Delivery Head",
    "Project Manager",
    "Engineering Manager",
]
LOCATION = "Bengaluru, Karnataka, India"
RESULTS_PER_TERM = 40
HOURS_OLD = 168  # 7 days

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}


def get_existing_job_ids():
    """Fetch all Source Job ID values already in Airtable to avoid duplicates."""
    existing = set()
    offset = None
    while True:
        params = {"fields[]": "Source Job ID"}
        if offset:
            params["offset"] = offset
        resp = requests.get(AIRTABLE_API, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for rec in data.get("records", []):
            sid = rec.get("fields", {}).get("Source Job ID")
            if sid:
                existing.add(sid)
        offset = data.get("offset")
        if not offset:
            break
    return existing


def push_records(records):
    """Create records in Airtable in batches of 10. If a batch fails, retry one-by-one
    so a single bad record doesn't block the rest of the batch."""
    for i in range(0, len(records), 10):
        batch = records[i : i + 10]
        resp = requests.post(
            AIRTABLE_API,
            headers=HEADERS,
            json={"records": batch, "typecast": True},
            timeout=30,
        )
        if resp.status_code >= 300:
            print(f"Batch failed ({resp.status_code}): {resp.text[:300]} — retrying individually")
            for rec in batch:
                r = requests.post(
                    AIRTABLE_API,
                    headers=HEADERS,
                    json={"records": [rec], "typecast": True},
                    timeout=30,
                )
                if r.status_code >= 300:
                    print(f"Skipped 1 record: {r.status_code} {r.text[:200]}", file=sys.stderr)
                time.sleep(0.25)
        else:
            print(f"Pushed {len(batch)} records")
        time.sleep(0.3)


def main():
    existing_ids = get_existing_job_ids()
    print(f"Existing job IDs in Airtable: {len(existing_ids)}")

    all_new_records = []

    for term in SEARCH_TERMS:
        print(f"Scraping LinkedIn for: {term}")
        try:
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=term,
                location=LOCATION,
                results_wanted=RESULTS_PER_TERM,
                hours_old=HOURS_OLD,
                linkedin_fetch_description=True,
                easy_apply=True,
                country_indeed="india",
            )
        except Exception as e:
            print(f"Error scraping '{term}': {e}", file=sys.stderr)
            continue

        if jobs is None or jobs.empty:
            print(f"No results for: {term}")
            continue

        for _, row in jobs.iterrows():
            job_id = str(row.get("id") or row.get("job_url"))
            if job_id in existing_ids:
                continue
            existing_ids.add(job_id)  # avoid dupes within this same run too

            fields = {
                "Job Title": str(row.get("title") or ""),
                "Company": str(row.get("company") or ""),
                "Job URL": str(row.get("job_url") or ""),
                "Location": str(row.get("location") or ""),
                "Easy Apply": bool(row.get("easy_apply")) if "easy_apply" in row else True,
                "Job Description Raw": str(row.get("description") or "")[:90000],
                "Status": "Pending Review",
                "Source Job ID": job_id,
            }
            # Posted Date as ISO string if available (pandas may represent missing as NaN or NaT)
            date_posted = row.get("date_posted")
            if date_posted is not None:
                date_str = str(date_posted)
                if date_str not in ("NaT", "nan", "None", ""):
                    fields["Posted Date"] = date_str[:10]

            all_new_records.append({"fields": fields})

    print(f"Total new jobs to push: {len(all_new_records)}")
    if all_new_records:
        push_records(all_new_records)
    else:
        print("No new jobs found this run.")


if __name__ == "__main__":
    main()
