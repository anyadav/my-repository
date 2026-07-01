"""
Scores Pending Review jobs in Airtable against Amar's resume using Google Gemini (free tier).
Caps scoring at MAX_SCORE_PER_RUN per run to stay within Gemini free tier limits.
Adds exponential backoff on 429 rate limit errors.

Requires env vars: AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID, GEMINI_API_KEY
"""

import os
import sys
import json
import time
import requests

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
AT_HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}
GEMINI_API = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)
MATCH_THRESHOLD = 90
MAX_SCORE_PER_RUN = 10   # hard cap — stays within Gemini free tier per run

RESUME_TEXT = """
AMAR NATH YADAV
Delivery Manager | Program Manager | Global Delivery | Account Growth | Agile Program Execution
Bangalore, India | +91 9739295982 | amaryadav.9s@gmail.com | linkedin.com/in/amar-nath-yadav-1481021a

EXECUTIVE SUMMARY
Senior Delivery Management professional with 18+ years IT industry experience, including significant
years in Delivery Management, Program Governance, Managed Services, and Global Operations Leadership
across APAC, EMEA, NAMER and LATEM regions. Proven expertise leading large-scale delivery programs,
managed services operations, staff augmentation engagements, transition management, and cross-functional
delivery execution for enterprise customers including Google and Oracle. Currently leading global delivery
operations from customer (Google) location in Taiwan with strong expertise in stakeholder management,
operational governance, delivery transformation, escalation management, KPI/SLA/SLO governance, and
customer engagement.

CORE COMPETENCIES
Delivery Management, Program Management, Account Delivery Management, Cross-Functional Leadership,
Global Delivery Operations, Managed Services, Service Delivery Management, Staff Augmentation, Transition
Management, Delivery Governance, Program Execution, Escalation Management, Risk Mitigation, Resource
Planning, KPI/SLA/SLO Governance, MBR/QBR Management, Executive Reporting, Vendor Coordination,
Stakeholder Management, Client Relationship Management, Global Team Management, Agile Delivery, QA
Program Management, Revenue & Contract Management, SOW Management.

PROFESSIONAL EXPERIENCE
Wipro Limited — Delivery Manager | Dec 2012 - Present | Taiwan / India
Progressed through Technical Lead, Technical Manager, Project Manager, Program Manager, and Delivery
Manager roles managing enterprise delivery programs for global customers including Google and Oracle.
Key programs: ChromeOS Global Operations, Google Pixel Hardware Testing Programs, Google Home & Nest,
Oracle Product Porting on IBM Platforms.

Sasken Technologies — Senior Engineer, System Software | Feb 2010 - Dec 2012 | India
Mahathi Software — Software Engineer | Oct 2007 - Feb 2010 | India

EDUCATION
B.Tech - Computer Science & Engineering
Post Graduate Diploma in Embedded Systems - CDAC Pune
"""

SCORING_PROMPT = """You are scoring how well a job posting matches a candidate's resume for a job search shortlist.

CANDIDATE RESUME:
{resume}

JOB POSTING:
Title: {title}
Company: {company}
Location: {location}
Description:
{description}

Score the match from 0-100 based on:
- Role title alignment (Delivery Manager / Program Manager / Delivery Head / Account Delivery Head / Engineering Manager)
- Seniority fit (18+ years experience)
- Domain overlap (enterprise IT services, managed services, global delivery, stakeholder/SLA governance)
- Location fit (Bangalore, India)

Also extract ONLY if explicitly present in the job description text (do not guess or invent):
- hiring_manager_name
- hiring_manager_email
- hiring_manager_linkedin

Respond with STRICT JSON only — no markdown fences, no preamble, no explanation:
{{"match_score": <int 0-100>, "reasoning": "<2-3 sentence justification>", "hiring_manager_name": null, "hiring_manager_email": null, "hiring_manager_linkedin": null}}"""


def get_pending_jobs(limit):
    """Fetch up to `limit` Pending Review records from Airtable."""
    records = []
    offset = None
    while len(records) < limit:
        params = {
            "filterByFormula": "{Status} = 'Pending Review'",
            "pageSize": min(100, limit - len(records)),
        }
        if offset:
            params["offset"] = offset
        resp = requests.get(AIRTABLE_API, headers=AT_HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records[:limit]


def score_job(title, company, location, description):
    """Call Gemini with exponential backoff on 429 rate limit errors."""
    prompt = SCORING_PROMPT.format(
        resume=RESUME_TEXT,
        title=title,
        company=company,
        location=location,
        description=(description or "")[:8000],
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512},
    }

    wait = 5  # initial backoff seconds
    for attempt in range(4):  # max 4 attempts per job
        resp = requests.post(GEMINI_API, json=body, timeout=60)
        if resp.status_code == 429:
            print(f"  429 rate limit — waiting {wait}s before retry {attempt + 1}/3 ...")
            time.sleep(wait)
            wait *= 2  # exponential: 5 → 10 → 20 → 40
            continue
        if resp.status_code >= 300:
            print(f"Gemini API error: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
            return None
        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            print(f"Unexpected Gemini response: {str(data)[:200]}", file=sys.stderr)
            return None
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"Failed to parse Gemini output: {text[:200]}", file=sys.stderr)
            return None

    print("  Max retries reached — skipping this job", file=sys.stderr)
    return None


def update_record(record_id, fields):
    resp = requests.patch(
        f"{AIRTABLE_API}/{record_id}",
        headers=AT_HEADERS,
        json={"fields": fields, "typecast": True},
        timeout=30,
    )
    if resp.status_code >= 300:
        print(f"Airtable update error: {resp.status_code} {resp.text}", file=sys.stderr)


def main():
    print(f"=== score_jobs.py starting (cap: {MAX_SCORE_PER_RUN} per run) ===")
    jobs = get_pending_jobs(MAX_SCORE_PER_RUN)
    print(f"Fetched {len(jobs)} jobs to score this run")

    if not jobs:
        print("Nothing to score — exiting.")
        return

    scored = []

    for rec in jobs:
        f = rec["fields"]
        title = f.get("Job Title", "(no title)")
        company = f.get("Company", "(no company)")
        location = f.get("Location", "")
        description = f.get("Job Description Raw", "")

        print(f"Scoring: {title} @ {company} ...")
        result = score_job(title, company, location, description)
        time.sleep(5)  # 5s gap = max 12 RPM, safely under Gemini free tier 15 RPM limit

        if not result:
            print("  -> Skipped (no result from model)")
            continue

        score = int(result.get("match_score", 0))
        print(f"  -> Score: {score}")

        update_fields = {
            "Match Score": score,
            "AI Reasoning": result.get("reasoning", ""),
            "Status": "Shortlisted" if score >= MATCH_THRESHOLD else "Skipped",
        }
        if result.get("hiring_manager_name"):
            update_fields["Hiring Manager Name"] = result["hiring_manager_name"]
        if result.get("hiring_manager_email"):
            update_fields["Hiring Manager Email"] = result["hiring_manager_email"]
        if result.get("hiring_manager_linkedin"):
            update_fields["Hiring Manager LinkedIn"] = result["hiring_manager_linkedin"]

        update_record(rec["id"], update_fields)
        scored.append((rec["id"], score))

    shortlisted_count = sum(1 for _, s in scored if s >= MATCH_THRESHOLD)
    print(f"Shortlisted: {shortlisted_count} / {len(scored)} scored this run")

    if shortlisted_count == 0 and scored:
        print("No jobs met 90% threshold — applying top-5 fallback")
        top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]
        for record_id, _ in top5:
            update_record(record_id, {"Status": "Shortlisted"})

    print("=== score_jobs.py complete ===")


if __name__ == "__main__":
    main()
