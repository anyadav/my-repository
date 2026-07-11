"""
scrape_jobs.py (v4-debug2) -- LinkedIn-only job scraper for Amar's Job Hunt Dashboard.

TEMPORARY: deeper diagnostics for Easy Apply detection (v1 markers didn't
match any of the 10 sampled job pages). date_posted is confirmed None from
jobspy itself for every LinkedIn result -- separate fix needed for that.
"""

import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone

import requests
from jobspy import scrape_jobs

# ---- Config ----
SITES = ["linkedin"]  # LinkedIn only -- Naukri dropped per requirements
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
HOURS_OLD = 24
DATE_TOLERANCE_DAYS = 1
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

def within_date_tolerance(date_posted_str: str) -> bool:
    if not date_posted_str or date_posted_str in ("NaT", "nan", "None"):
        return True
    try:
        posted = datetime.strptime(date_posted_str[:10], "%Y-%m-%d").date()
    except ValueError:
        return True
    today_ist = datetime.now(IST).date()
    return abs((today_ist - posted).days) <= DATE_TOLERANCE_DAYS

LINKEDIN_ID_RE = re.compile(r"(?:jobs/view/|currentJobId=|jobPosting:|li-)(\d{6,})")
ANY_LONG_NUM_RE = re.compile(r"(\d{9,})")

def canonical_job_url(job_url: str, job_id: str) -> str | None:
    for source in (job_url or "", job_id or ""):
        m = LINKEDIN_ID_RE.search(source)
        if m:
            return f"https://www.linkedin.com/jobs/view/{m.group(1)}/"
    m = ANY_LONG_NUM_RE.search(job_url or "")
    if m:
        return f"https://www.linkedin.com/jobs/view/{m.group(1)}/"
    if job_url and "/jobs/view/" in job_url:
        return job_url.split("?")[0]
    return None

DATEPOSTED_RE = re.compile(r'"datePosted"\s*:\s*"([^"]+)"')

def fetch_job_page_signals(url: str):
    """
    DEBUG helper: fetch a job page once and report every signal we can find
    for Easy Apply + posted date, so we can pick reliable real markers
    instead of guessing.
    """
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; JobDashboardBot/1.0)"},
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"DEBUG fetch error: {e} url={url}")
        return False, None

    if resp.status_code != 200:
        print(f"DEBUG fetch: status={resp.status_code} url={url}")
        return False, None

    text = resp.text
    lower = text.lower()
    ci_easy_apply = "easy apply" in lower
    has_dateposted_key = "dateposted" in lower
    m = DATEPOSTED_RE.search(text)
    date_posted_jsonld = m.group(1) if m else None

    print(
        f"DEBUG signals url={url} len={len(text)} "
        f"ci_easy_apply={ci_easy_apply} has_dateposted_key={has_dateposted_key} "
        f"jsonld_date_posted={date_posted_jsonld}"
    )
    if ci_easy_apply:
        idx = lower.find("easy apply")
        print(f"DEBUG easy_apply context: ...{text[max(0,idx-60):idx+60]}...")
    if has_dateposted_key and not date_posted_jsonld:
        idx = lower.find("dateposted")
        print(f"DEBUG dateposted context: ...{text[max(0,idx-30):idx+150]}...")

    return ci_easy_apply, date_posted_jsonld

def delete_all_records():
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
            print(f"Batch failed ({resp.status_code}) -- retrying individually")
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
    # delete_all_records()

    all_new_records = []
    seen_ids = set()
    skipped_no_url = 0
    skipped_stale = 0

    for term in SEARCH_TERMS[:1]:
        if len(all_new_records) >= 3:
            break
        print(f"Scraping {'+'.join(SITES)} for: {term}")
        try:
            jobs = scrape_jobs(
                site_name=SITES,
                search_term=term,
                location=LOCATION,
                results_wanted=3,
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

        for _, row in jobs.iterrows():
            raw_id = str(row.get("id") or row.get("job_url"))
            if raw_id in seen_ids:
                continue
            seen_ids.add(raw_id)
            clean_url = canonical_job_url(str(row.get("job_url") or ""), raw_id)
            if not clean_url:
                skipped_no_url += 1
                continue
            fetch_job_page_signals(clean_url)

    print("DEBUG-ONLY RUN COMPLETE -- no records pushed to Airtable this run.")

if __name__ == "__main__":
    main()
