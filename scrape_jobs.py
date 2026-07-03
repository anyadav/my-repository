"""
LinkedIn job scraper for Amar's Job Hunt Dashboard.
On each run:
  1. Deletes ALL existing Airtable records (fresh slate)
  2. Scrapes LinkedIn via JobSpy (Easy Apply, last 48hrs, Bangalore)
  3. Pushes up to MAX_NEW_PER_RUN new jobs as Pending Review

Run via GitHub Actions at 23:00 UTC = 07:00 TPE daily, or manually.
Requires env vars: AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
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
RESULTS_PER_TERM = 5      # 6 terms x 5 = 30 raw max before dedup
HOURS_OLD = 48            # today + yesterday only
MAX_NEW_PER_RUN = 10      # hard cap on jobs pushed to Airtable per run

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}


def delete_all_records():
    """Delete every existing record in the Airtable table — fresh slate each run."""
    print("Clearing previous listings from Airtable ...")
    deleted_total = 0
    while True:
        # Fetch a page of record IDs
        resp = requests.get(
            AIRTABLE_API,
            headers=HEADERS,
            params={"fields[]": "Job Title", "pageSize": 100},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", [])
        if not records:
            break

        # Delete in batches of 10 (Airtable API limit)
        ids = [r["id"] for r in records]
        for i in range(0, len(ids), 10):
            batch = ids[i:i + 10]
            params = "&".join(f"records[]={rid}" for rid in batch)
            del_resp = requests.delete(
                f"{AIRTABLE_API}?{params}",
                headers=HEADERS,
                timeout=30,
            )
            if del_resp.status_code >= 300:
                print(f"Delete error: {del_resp.status_code} {del_resp.text[:200]}", file=sys.stderr)
            else:
                deleted_total += len(batch)
            time.sleep(0.25)

        # If no offset, we've fetched all records
        if not data.get("offset"):
            break

    print(f"Deleted {deleted_total} previous records.")


def push_records(records):
    """Push new records in batches of 10. Falls back to one-by-one on batch failure."""
    for i in range(0, len(records), 10):
        batch = records[i:i + 10]
        resp = requests.post(
            AIRTABLE_API,
            headers=HEADERS,
            json={"records": batch, "typecast": True},
            timeout=30,
        )
        if resp.status_code >= 300:
            print(f"Batch failed ({resp.status_code}) — retrying individually")
            for rec in batch:
                r = requests.post(
                    AIRTABLE_API,
                    headers=HEADERS,
                    json={"records": [rec], "typecast": True},
                    timeout=30,
                )
                if r.status_code >= 300:
                    print(f"Skipped 1 record: {r.status_code} {r.text[:150]}", file=sys.stderr)
                time.sleep(0.25)
        else:
            print(f"Pushed {len(batch)} records")
        time.sleep(0.3)


def main():
    # Step 1: clear everything
    delete_all_records()

    # Step 2: scrape LinkedIn
    all_new_records = []
    seen_ids = set()

    for term in SEARCH_TERMS:
        if len(all_new_records) >= MAX_NEW_PER_RUN:
            break
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
            if len(all_new_records) >= MAX_NEW_PER_RUN:
                break
            job_id = str(row.get("id") or row.get("job_url"))
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

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
            date_posted = row.get("date_posted")
            if date_posted is not None:
                date_str = str(date_posted)
                if date_str not in ("NaT", "nan", "None", ""):
                    fields["Posted Date"] = date_str[:10]

            all_new_records.append({"fields": fields})

    # Step 3: push
    print(f"Pushing {len(all_new_records)} new jobs to Airtable ...")
    if all_new_records:
        push_records(all_new_records)
    else:
        print("No new jobs found this run.")


if __name__ == "__main__":
    main()
