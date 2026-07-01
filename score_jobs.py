"""
Scores Pending Review jobs in Airtable against Amar's resume using the Claude API.
Writes back: Match Score, AI Reasoning, Status, Hiring Manager Name/Email/LinkedIn (if present in posting).
If zero jobs score >=90, falls back to marking the top 5 as Shortlisted regardless of score.

Requires env vars: AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID, ANTHROPIC_API_KEY
"""

import os
import sys
import json
import time
import requests

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

AIRTABLE_API = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
AT_HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}
ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
ANTHROPIC_HEADERS = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}
MATCH_THRESHOLD = 90

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

SCORING_PROMPT = """You are scoring how well a job posting matches a candidate's resume for the purpose of a job search shortlist.

CANDIDATE RESUME:
{resume}

JOB POSTING:
Title: {title}
Company: {company}
Location: {location}
Description:
{description}

Score the match from 0-100 based on: role title alignment (Delivery Manager / Program Manager / Delivery Head /
Account Delivery Head / Engineering Manager), seniority fit (18+ years experience), domain overlap (enterprise
IT services, managed services, global delivery, stakeholder/SLA governance), and location fit (Bangalore, India).

Also extract, ONLY if explicitly present in the job description text (do not guess or invent):
- hiring_manager_name
- hiring_manager_email
- hiring_manager_linkedin

Respond with STRICT JSON only, no markdown fences, no preamble:
{{"match_score": <int 0-100>, "reasoning": "<2-3 sentence justification>", "hiring_manager_name": "<string or null>", "hiring_manager_email": "<string or null>", "hiring_manager_linkedin": "<string or null>"}}
"""


def get_pending_jobs():
    records = []
    offset = None
    while True:
        params = {"filterByFormula": "{Status} = 'Pending Review'"}
        if offset:
            params["offset"] = offset
        resp = requests.get(AIRTABLE_API, headers=AT_HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records


def score_job(title, company, location, description):
    prompt = SCORING_PROMPT.format(
        resume=RESUME_TEXT,
        title=title,
        company=company,
        location=location,
        description=(description or "")[:8000],
    )
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(ANTHROPIC_API, headers=ANTHROPIC_HEADERS, json=body, timeout=60)
    if resp.status_code >= 300:
        print(f"Anthropic API error: {resp.status_code} {resp.text[:500]}", file=sys.stderr)
        return None
    data = resp.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"Failed to parse model output: {text[:300]}", file=sys.stderr)
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
    jobs = get_pending_jobs()
    print(f"Found {len(jobs)} jobs pending scoring")

    scored = []  # (record_id, score, fields_dict)

    for rec in jobs:
        f = rec["fields"]
        title = f.get("Job Title", "")
        company = f.get("Company", "")
        location = f.get("Location", "")
        description = f.get("Job Description Raw", "")

        result = score_job(title, company, location, description)
        time.sleep(0.5)  # gentle on rate limits

        if not result:
            continue

        score = int(result.get("match_score", 0))
        update_fields = {
            "Match Score": score,
            "AI Reasoning": result.get("reasoning", ""),
        }
        if result.get("hiring_manager_name"):
            update_fields["Hiring Manager Name"] = result["hiring_manager_name"]
        if result.get("hiring_manager_email"):
            update_fields["Hiring Manager Email"] = result["hiring_manager_email"]
        if result.get("hiring_manager_linkedin"):
            update_fields["Hiring Manager LinkedIn"] = result["hiring_manager_linkedin"]

        update_fields["Status"] = "Shortlisted" if score >= MATCH_THRESHOLD else "Reviewed - Below Threshold"

        update_record(rec["id"], update_fields)
        scored.append((rec["id"], score))
        print(f"Scored: {title} @ {company} -> {score}")

    # Fallback: if nobody crossed the threshold, shortlist the top 5 anyway
    shortlisted_count = sum(1 for _, s in scored if s >= MATCH_THRESHOLD)
    if shortlisted_count == 0 and scored:
        print("No jobs met 90% threshold — applying top-5 fallback")
        top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]
        for record_id, score in top5:
            update_record(record_id, {"Status": "Shortlisted (Top 5 Fallback)"})

    print("Scoring complete.")


if __name__ == "__main__":
    main()
