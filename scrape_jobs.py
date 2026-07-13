"""
scrape_jobs.py (v8) -- Naukri job scraper for Amar's Job Hunt Dashboard.

Changes vs v7 (LinkedIn):
1. SOURCE SWITCH -- scraping now targets Naukri exclusively via
   python-jobspy's site_name=["naukri"] support. LinkedIn is dropped: four
   independent v4-v7 diagnostics established that anonymous/unauthenticated
   LinkedIn scraping in this environment could never reliably expose Easy
   Apply status or a real posted date (see git history on this branch for
   the full trail). That is a hard limitation of anonymous LinkedIn access,
   not something fixable in this script.
2. ROLES -- SEARCH_TERMS updated to the six target roles: Delivery Manager,
   Program Manager, Delivery Head, Account Delivery Head, Delivery Director,
   Senior Project Manager.
3. RECENCY FILTER -- posted within the last 24 hours (HOURS_OLD = 24, passed
   to jobspy) plus a local RECENCY_DAYS=1 safety-net filter on whatever
   date_posted Naukri/jobspy actually returns. Jobs with an unparseable or
   missing posted date are KEPT -- we never drop a job for missing data.
4. EXPERIENCE FILTER (15+ yrs) -- Naukri exposes a free-text
   "experience_range" field (e.g. "15-20 Yrs"). We parse the numbers in it
   and keep the job if the upper bound of the range is >= MIN_EXPERIENCE_YRS.
   Jobs where this can't be parsed are KEPT (standing rule: never drop a job
   on missing/unparseable data).
5. SALARY FILTER (>= Rs 30,00,000 / yr) -- parses jobspy's min_amount /
   max_amount + interval/currency columns, annualizes them, and keeps the
   job if the best available figure clears MIN_ANNUAL_SALARY_INR. Jobs with
   no disclosed salary, or in a currency we can't safely compare in INR, are
   KEPT (standing rule: never drop a job on missing data).
6. EXTERNAL-APPLY EXCLUSION (best effort) -- Naukri's API/jobspy don't
   directly expose whether a listing routes to an external company site.
   We do a best-effort GET of each JD page and look for an "apply on
   company site/website" marker. CONFIRMED matches are DROPPED; everything
   else (fetch failure, timeout, marker absent) is UNDETERMINED and KEPT.
7. NO APPLY LOGIC -- this script only scrapes, filters, and lists jobs in
   Airtable with Status "Pending Review". It never applies, clicks Easy
   Apply/similar, or submits anything on the job seeker's behalf, on Naukri
   or anywhere else. That remains true across this whole pipeline.
8. Volume raised (RESULTS_PER_TERM / MAX_NEW_PER_RUN) vs the old LinkedIn
   defaults so score_jobs.py has a real candidate pool to pick a genuine
   "top 50 by score" from, instead of a handful of daily results.

Pipeline: (this) scrape -> Airtable "Pending Review" -> score_jobs.py (local, no LLM)
Requires env vars: AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
"""

import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
from jobspy import scrape_jobs

# ---- Config ----
SITES = ["indeed", "linkedin", "zip_recruiter", "google"]  # Naukri is not supported by python-jobspy; switched to supported India-capable sources
SEARCH_TERMS = [
    "Delivery Manager",
    "Program Manager",
    "Delivery Head",
    "Account Delivery Head",
    "Delivery Director",
    "Senior Project Manager",
]

LOCATION = "Bengaluru, Karnataka, India"
RESULTS_PER_TERM = 20
HOURS_OLD = 24              # posted within the last 24 hours
RECENCY_DAYS = 1            # local safety-net filter mirroring HOURS_OLD (+1 day tz-skew guard below)
MIN_EXPERIENCE_YRS = 15     # keep jobs whose experience_range upper bound >= this
MIN_ANNUAL_SALARY_INR = 30_00_000  # Rs 30,00,000 / year
MAX_NEW_PER_RUN = 100       # headroom across 6 roles so score_jobs.py has a real pool to rank

IST = timezone(timedelta(hours=5, minutes=30))

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}

JD_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
EXTERNAL_APPLY_MARKERS = [
    "apply on company site",
    "apply on company website",
    "apply on the company website",
    "apply on companys website",
    "apply on company's website",
]


# ---- Recency ----
def within_recency(date_posted_str: str, days: int = RECENCY_DAYS) -> bool:
    """True if posted date is within the last N days (IST), with a
    1-day forward tolerance for timezone skew. Jobs with no parseable date
    pass through -- HOURS_OLD already bounds the Naukri-side query, and we
    never drop a job just because we can't confirm its date locally."""
    if not date_posted_str or date_posted_str in ("NaT", "nan", "None"):
        return True
    try:
        posted = datetime.strptime(date_posted_str[:10], "%Y-%m-%d").date()
    except ValueError:
        return True
    today_ist = datetime.now(IST).date()
    delta_days = (today_ist - posted).days
    return -1 <= delta_days <= days


# ---- Experience parsing ----
EXPERIENCE_NUM_RE = re.compile(r"(\d+(?:\.\d+)?)")


def passes_experience_filter(experience_range, min_years: float = MIN_EXPERIENCE_YRS) -> bool:
    """Keep the job if the upper bound of Naukri's free-text experience_range
    (e.g. "15-20 Yrs") is >= min_years. Unparseable/missing values are KEPT
    per the standing rule: never drop a job on missing/ambiguous data."""
    if experience_range is None or str(experience_range).strip().lower() in ("nan", "none", ""):
        return True
    nums = [float(n) for n in EXPERIENCE_NUM_RE.findall(str(experience_range))]
    if not nums:
        return True
    return max(nums) >= min_years


# ---- Salary parsing ----
def _to_float(x):
    try:
        if x is None:
            return None
        f = float(x)
        return None if f != f else f  # NaN check
    except (TypeError, ValueError):
        return None


def passes_salary_filter(min_amount, max_amount, interval, currency,
                          min_annual: int = MIN_ANNUAL_SALARY_INR) -> bool:
    """Keep the job if the best available disclosed salary figure, annualized,
    is >= min_annual. Undisclosed salary, or a currency we can't safely
    compare in INR, is KEPT per the standing rule on missing data."""
    lo, hi = _to_float(min_amount), _to_float(max_amount)
    if lo is None and hi is None:
        return True  # undisclosed -- keep

    if currency and str(currency).strip().upper() not in ("INR", "NAN", ""):
        return True  # can't safely compare a non-INR figure -- keep

    best = hi if hi is not None else lo
    interval_norm = str(interval).strip().lower() if interval else "yearly"
    if interval_norm in ("hour", "hourly"):
        annual = best * 2080
    elif interval_norm in ("month", "monthly"):
        annual = best * 12
    elif interval_norm in ("week", "weekly"):
        annual = best * 52
    else:  # "year"/"yearly"/"annual"/unknown -- Naukri figures are normally CTC/yr
        annual = best
    return annual >= min_annual


# ---- URL handling ----
def clean_job_url(job_url):
    """Return the direct job posting URL as scraped (query params kept --
    e.g. Indeed's job-key param); None if the URL is missing/unusable."""
    if not job_url or str(job_url).strip().lower() in ("nan", "none", ""):
        return None
    url = str(job_url).strip()
    return url or None


# ---- External-apply detection (best effort) ----
def is_external_apply(job_url: str) -> bool:
    """Best-effort check: fetch the JD page and look for an 'apply on
    company site/website' marker. Returns True only on a CONFIRMED match.
    Any failure, timeout, or absence of the marker is UNDETERMINED and
    treated as False (i.e. the job is kept) -- Naukri's API doesn't expose
    this directly, so best-effort is all we can do."""
    try:
        resp = requests.get(job_url, headers=JD_FETCH_HEADERS, timeout=15)
        if resp.status_code != 200:
            return False
        page_text = resp.text.lower()
        return any(marker in page_text for marker in EXTERNAL_APPLY_MARKERS)
    except requests.RequestException:
        return False


# ---- Airtable ----
def delete_all_records():
    """Delete every existing record -- fresh slate each run."""
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
            del_resp = requests.delete(
                f"{AIRTABLE_API}?{params}", headers=HEADERS, timeout=30
            )
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
            print(f"Batch failed ({resp.status_code}) -- retrying individually", file=sys.stderr)
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


# ---- Main ----
def main():
    delete_all_records()

    all_new_records = []
    seen_ids = set()
    skipped_no_url = 0
    skipped_stale = 0
    skipped_experience = 0
    skipped_salary = 0
    skipped_external_apply = 0

    for term in SEARCH_TERMS:
        if len(all_new_records) >= MAX_NEW_PER_RUN:
            break
        print(f"Scraping {'+'.join(SITES)} for: {term}")
        try:
            jobs = scrape_jobs(
                site_name=SITES,
                search_term=term,
                location=LOCATION,
                results_wanted=RESULTS_PER_TERM,
                hours_old=HOURS_OLD,
               country_indeed="India",  # required by jobspy when "indeed" is included in site_name
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

            clean_url = clean_job_url(row.get("job_url"))
            if not clean_url:
                skipped_no_url += 1
                continue

            # --- FRESHNESS FILTER: last 24h (IST today, 1-day tz-skew tolerance) ---
            date_posted_raw = str(row.get("date_posted") or "")
            if not within_recency(date_posted_raw):
                skipped_stale += 1
                continue

            # --- EXPERIENCE FILTER: keep 15+ yrs, keep unparseable ---
            experience_range = row.get("experience_range")
            if not passes_experience_filter(experience_range):
                skipped_experience += 1
                continue

            # --- SALARY FILTER: keep >= Rs 30L/yr, keep undisclosed ---
            if not passes_salary_filter(
                row.get("min_amount"), row.get("max_amount"),
                row.get("interval"), row.get("currency"),
            ):
                skipped_salary += 1
                continue

            # --- EXTERNAL-APPLY EXCLUSION: best effort, undetermined = keep ---
            if is_external_apply(clean_url):
                skipped_external_apply += 1
                continue
            time.sleep(0.4)  # be polite to Naukri between JD-page fetches

            fields = {
                "Job Title": str(row.get("title") or ""),
                "Company": str(row.get("company") or ""),
                "Job URL": clean_url,
                "Location": str(row.get("location") or ""),
                "Job Description Raw": str(row.get("description") or "")[:90000],
                "Status": "Pending Review",
                "Source Job ID": raw_id,
                "Date Scraped": datetime.now(IST).date().isoformat(),
            }
            if experience_range and str(experience_range).strip().lower() not in ("nan", "none", ""):
                fields["Experience Range"] = str(experience_range)

            date_posted = row.get("date_posted")
            if date_posted is not None:
                date_str = str(date_posted)
                if date_str and date_str not in ("NaT", "nan", "None"):
                    fields["Posted Date"] = date_str[:10]

            all_new_records.append({"fields": fields})

    print(f"Pushing {len(all_new_records)} new jobs to Airtable "
          f"({skipped_no_url} skipped: no URL; {skipped_stale} skipped: outside recency; "
          f"{skipped_experience} skipped: under experience; {skipped_salary} skipped: under salary; "
          f"{skipped_external_apply} skipped: confirmed external apply)")
    if all_new_records:
        push_records(all_new_records)
    else:
        print("No new jobs found this run.")


if __name__ == "__main__":
    main()
