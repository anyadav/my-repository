"""
scrape_jobs.py (v2) — LinkedIn job scraper for Amar's Job Hunt Dashboard.

Changes vs v1:
1. CANONICAL JOB URLS — every job URL is normalized to
   https://www.linkedin.com/jobs/view/<numeric_id>/ so clicking a job in the
   dashboard ALWAYS lands on the actual posting (fixes tracking/redirect URLs
   that previously dumped users on a search page).
2. Sets "Date Scraped" on every record.
3. Skips records where no usable URL can be derived (no point storing a job
   you can't open).

Pipeline: (this) scrape -> Airtable "Pending Review" -> score_jobs.py (local, no LLM)
Requires env vars: AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
"""

import os
import re
import sys
import time
from datetime import date

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
RESULTS_PER_TERM = 5
HOURS_OLD = 48
MAX_NEW_PER_RUN = 10

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}

LINKEDIN_ID_RE = re.compile(r"(?:jobs/view/|currentJobId=|jobPosting:|li-)(\d{6,})")
ANY_LONG_NUM_RE = re.compile(r"(\d{9,})")


def canonical_linkedin_url(job_url: str, job_id: str) -> str | None:
    """
    Return a direct, canonical LinkedIn posting URL, or None if impossible.
    Handles: tracking params, search-page URLs with currentJobId, jobspy ids
    like 'li-4123456789'.
    """
    for source in (job_url or "", job_id or ""):
        m = LINKEDIN_ID_RE.search(source)
        if m:
            return f"https://www.linkedin.com/jobs/view/{m.group(1)}/"
    # last resort: any 9+ digit number in the URL is almost certainly the posting id
    m = ANY_LONG_NUM_RE.search(job_url or "")
    if m:
        return f"https://www.linkedin.com/jobs/view/{m.group(1)}/"
    # if the url already looks like a clean /jobs/view/ link, keep it
    if job_url and "/jobs/view/" in job_url:
        return job_url.split("?")[0]
    return None


def delete_all_records():
    """Delete every existing record — fresh slate each run."""
    print("Clearing previous listings from Airtable ...")
    deleted_total = 0
    while True:
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
        ids = [r["id"] for r in records]
        for i in range(0, len(ids), 10):
            batch = ids[i:i + 10]
            params = "&".join(f"records[]={rid}" for rid in batch)
            del_resp = requests.delete(f"{AIRTABLE_API}?{params}", headers=HEADERS, timeout=30)
            if del_resp.status_code >= 300:
                print(f"Delete error: {del_resp.status_code} {del_resp.text[:200]}", file=sys.stderr)
            else:
                deleted_total += len(batch)
            time.sleep(0.25)
        if not data.get("offset"):
            break
    print(f"Deleted {deleted_total} previous records.")


def push_records(records):
    for i in range(0, len(records), 10):
        batch = records[i:i + 10]
        resp = requests.post(
            AIRTABLE_API, headers=HEADERS,
            json={"records": batch, "typecast": True}, timeout=30,
        )
        if resp.status_code >= 300:
            print(f"Batch failed ({resp.status_code}) — retrying individually")
            for rec in batch:
                r = requests.post(
                    AIRTABLE_API, headers=HEADERS,
                    json={"records": [rec], "typecast": True}, timeout=30,
                )
                if r.status_code >= 300:
                    print(f"Skipped 1 record: {r.status_code} {r.text[:150]}", file=sys.stderr)
                time.sleep(0.25)
        else:
            print(f"Pushed {len(batch)} records")
        time.sleep(0.3)


def main():
    delete_all_records()

    all_new_records = []
    seen_ids = set()
    skipped_no_url = 0

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
            raw_id = str(row.get("id") or row.get("job_url"))
            if raw_id in seen_ids:
                continue
            seen_ids.add(raw_id)

            # --- URL FIX: only store jobs with a verified direct posting link ---
            clean_url = canonical_linkedin_url(str(row.get("job_url") or ""), raw_id)
            if not clean_url:
                skipped_no_url += 1
                continue

            fields = {
                "Job Title": str(row.get("title") or ""),
                "Company": str(row.get("company") or ""),
                "Job URL": clean_url,
                "Location": str(row.get("location") or ""),
                "Easy Apply": bool(row.get("easy_apply")) if "easy_apply" in row else True,
                "Job Description Raw": str(row.get("description") or "")[:90000],
                "Status": "Pending Review",
                "Source Job ID": raw_id,
                "Date Scraped": date.today().isoformat(),
            }
            date_posted = row.get("date_posted")
            if date_posted is not None:
                date_str = str(date_posted)
                if date_str not in ("NaT", "nan", "None", ""):
                    fields["Posted Date"] = date_str[:10]

            all_new_records.append({"fields": fields})

    print(f"Pushing {len(all_new_records)} new jobs to Airtable "
          f"({skipped_no_url} skipped: no direct URL derivable) ...")
    if all_new_records:
        push_records(all_new_records)
    else:
        print("No new jobs found this run.")


if __name__ == "__main__":
    main()
