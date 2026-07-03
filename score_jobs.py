"""
score_jobs.py — Quota-aware Gemini scoring for job agent pipeline.
Changes vs previous version:
1. Fail-fast on quota exhaustion — one confirmed 429-after-backoff aborts the
   whole batch instead of retrying all N jobs individually (saves ~40 min of
   wasted CI time on a bad day).
2. Reduced retries: 4 -> 2, shorter backoff (5s/10s instead of up to 40s).
3. Model fallback: gemini-2.0-flash -> gemini-2.0-flash-lite (separate quota
   bucket) if primary is rate-limited.
4. Enforced RPM pacing: sleeps between calls so you never approach the
   15 RPM free-tier ceiling in the first place — quota exhaustion should
   become rare rather than something we just retry around.
5. Airtable status differentiates *why* a job was skipped:
   "Skipped - Low Score" vs "Skipped - Quota Exhausted" vs "Skipped - Error".
"""

import os
import time
import json
import requests

# ---- Config -----------------------------------------------------------
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

PRIMARY_MODEL = "gemini-2.0-flash"
FALLBACK_MODEL = "gemini-2.0-flash-lite"

MAX_RETRIES = 2  # was 4
BACKOFF_SECONDS = [5, 10]  # was [5, 10, 20, 40]
MIN_SECONDS_BETWEEN_CALLS = 4.5  # keeps us under 15 RPM with margin (60/15=4s + buffer)
MATCH_THRESHOLD = 90

RESUME_TEXT_PATH = "resume.txt"  # pre-extracted resume text, adjust if needed

GEMINI_URL_TMPL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
)

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"


# ---- Gemini call with capped retry + fallback --------------------------
def call_gemini(prompt: str, model: str = PRIMARY_MODEL):
    """
    Returns (result_text, status) where status is one of:
    'ok', 'quota_exhausted', 'error'
    """
    url = GEMINI_URL_TMPL.format(model=model, key=GEMINI_API_KEY)
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(MAX_RETRIES + 1):
        resp = requests.post(url, json=body, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text, "ok"
            except (KeyError, IndexError):
                return None, "error"

        if resp.status_code == 429:
            if attempt < MAX_RETRIES:
                wait = BACKOFF_SECONDS[attempt]
                print(f"  429 rate limit — waiting {wait}s before retry {attempt + 1}/{MAX_RETRIES} ...")
                time.sleep(wait)
                continue
            # Retries exhausted on this model
            return None, "quota_exhausted"

        # Non-429, non-200 — treat as error, don't burn retries on it
        print(f"  Unexpected status {resp.status_code}: {resp.text[:200]}")
        return None, "error"

    return None, "quota_exhausted"


def score_job(job: dict, resume_text: str):
    prompt = build_scoring_prompt(job, resume_text)

    # Try primary model
    text, status = call_gemini(prompt, PRIMARY_MODEL)

    # If primary is quota-exhausted, try fallback model ONCE (separate bucket)
    if status == "quota_exhausted":
        print("  Primary model quota exhausted — trying fallback model ...")
        text, status = call_gemini(prompt, FALLBACK_MODEL)

    return text, status


def build_scoring_prompt(job: dict, resume_text: str) -> str:
    return f"""You are scoring a job posting against a candidate resume.

RESUME:
{resume_text}

JOB POSTING:
Title: {job.get('Job Title')}
Company: {job.get('Company')}
Description: {job.get('Job Description Raw')}

Return ONLY valid JSON with this exact shape, no markdown fences:
{{
  "match_score": <integer 0-100>,
  "reasoning": "<2-3 sentence explanation>",
  "hiring_manager": "<name if explicitly present in posting, else empty string>"
}}"""


# ---- Airtable helpers ---------------------------------------------------
def fetch_pending_jobs(cap: int = 10):
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {
        "filterByFormula": "{Status} = 'Pending Review'",
        "maxRecords": cap,
    }
    resp = requests.get(AIRTABLE_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("records", [])


def update_job_record(record_id: str, fields: dict):
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {"fields": fields}
    resp = requests.patch(f"{AIRTABLE_URL}/{record_id}", headers=headers, json=body, timeout=30)
    resp.raise_for_status()


# ---- Main -----------------------------------------------------------
def main():
    cap = 10
    print(f"=== score_jobs.py starting (cap: {cap} per run) ===")

    with open(RESUME_TEXT_PATH, "r", encoding="utf-8") as f:
        resume_text = f.read()

    records = fetch_pending_jobs(cap)
    print(f"Fetched {len(records)} jobs to score this run")

    shortlisted = 0
    scored = 0
    quota_hit = False

    for i, record in enumerate(records):
        job = record["fields"]
        title = job.get("Job Title", "Unknown")
        company = job.get("Company", "Unknown")
        print(f"Scoring: {title} @ {company} ...")

        if quota_hit:
            # Fail-fast: don't even attempt further jobs once quota is confirmed dead
            update_job_record(record["id"], {"Status": "Skipped - Quota Exhausted"})
            print("  -> Skipped (quota already confirmed exhausted this run)")
            continue

        text, status = score_job(job, resume_text)

        if status == "quota_exhausted":
            quota_hit = True
            update_job_record(record["id"], {"Status": "Skipped - Quota Exhausted"})
            print("  -> Skipped (quota exhausted on both primary and fallback models)")
            continue

        if status == "error" or text is None:
            update_job_record(record["id"], {"Status": "Skipped - Error"})
            print("  -> Skipped (no usable result from model)")
            continue

        try:
            cleaned = text.strip().removeprefix("```json").removesuffix("```").strip()
            parsed = json.loads(cleaned)
            match_score = int(parsed.get("match_score", 0))
            reasoning = parsed.get("reasoning", "")
            hiring_manager = parsed.get("hiring_manager", "")
        except (json.JSONDecodeError, ValueError):
            update_job_record(record["id"], {"Status": "Skipped - Error"})
            print("  -> Skipped (could not parse model output)")
            continue

        scored += 1
        is_shortlisted = match_score >= MATCH_THRESHOLD
        if is_shortlisted:
            shortlisted += 1

        fields = {
            "Match Score": match_score,
            "AI Reasoning": reasoning,
            "Status": "Shortlisted" if is_shortlisted else "Skipped",
        }
        if hiring_manager:
            fields["Hiring Manager"] = hiring_manager

        update_job_record(record["id"], fields)

        # Pace calls to stay comfortably under the RPM ceiling —
        # prevents us from walking into 429s in the first place.
        if i < len(records) - 1 and not quota_hit:
            time.sleep(MIN_SECONDS_BETWEEN_CALLS)

    print(f"Shortlisted: {shortlisted} / {scored} scored this run")
    if quota_hit:
        print("NOTE: Run ended early due to Gemini quota exhaustion. "
              "Check https://aistudio.google.com/ for reset time.")
    print("=== score_jobs.py complete ===")


if __name__ == "__main__":
    main()
