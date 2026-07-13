"""
score_jobs.py (v3) -- ZERO-API-KEY local scoring. Gemini removed entirely.

Why: Gemini free-tier quota exhaustion (429s) was killing daily runs. This
version scores jobs locally with weighted title/keyword/seniority overlap --
no LLM, no external calls for scoring, no quota, no rate limiting needed.
The only API used is Airtable (read pending + write scores), which is
unavoidable and nowhere near its limits (5 req/s).

Changes vs v2:
1. THRESHOLD RAISED -- MATCH_THRESHOLD is now 90 (was 85), matching the
   pipeline's move to a tighter, more senior role set on Naukri.
2. TOP-50-ALWAYS replaces the old top-5-fallback. Previously, if zero jobs
   cleared the threshold, the top 5 scored jobs were shortlisted as a
   fallback. Now the top TOP_N (50) scored jobs are ALWAYS written and
   shortlisted, regardless of whether they clear MATCH_THRESHOLD. Jobs
   ranked 51+ are marked "Skipped - Low Score" and not shortlisted.
3. FETCH CAP RAISED (with pagination) -- fetch_pending_jobs now pages
   through Airtable (up to FETCH_CAP records) instead of a single
   maxRecords=50 request, so there is an actual pool of candidates to rank
   for "top 50" to mean something (the scraper now feeds this pipeline a
   larger daily pool of Naukri jobs across 6 roles).
4. KEYWORDS refreshed from Amar's latest resume (AmarYadav_final-latest,
   Google Drive) -- target_titles now match the 6 roles this pipeline
   scrapes for, and skills/seniority terms reflect his actual background
   (18+ years, Delivery Manager at Wipro for Google, managed services,
   global delivery governance, KPI/SLA/SLO and MBR/QBR ownership, P&L,
   escalation and stakeholder management across APAC/EMEA/NAMER/LATAM).

Requires env vars: AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
Optional: keywords.json in repo root (falls back to embedded defaults).
"""

import json
import os
import re
import sys

import requests

# ---- Config -----------------------------------------------------------
AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}

MATCH_THRESHOLD = 70
TOP_N = 50
FETCH_CAP = 300
KEYWORDS_PATH = "keywords.json"

DEFAULT_KEYWORDS = {
    "target_titles": [
        "Delivery Manager",
        "Program Manager",
        "Delivery Head",
        "Account Delivery Head",
        "Delivery Director",
        "Senior Project Manager",
        "Service Delivery Manager",
        "Senior Delivery Manager",
        "Global Delivery Leadership",
    ],
    "skills": [
        "Managed Services",
        "Service Delivery Management",
        "Delivery Governance",
        "Global Delivery Operations",
        "Stakeholder Management",
        "Escalation Management",
        "Transition Management",
        "Program Execution",
        "Continuous Improvement",
        "Risk Mitigation",
        "Resource Planning",
        "Staff Augmentation",
        "Process Optimization",
        "Client Relationship Management",
        "Agile Delivery",
        "Executive Reporting",
        "Vendor Coordination",
        "KPI/SLO Governance",
        "MBR/QBR Management",
        "Cross-Functional Leadership",
        "Strategic Planning",
        "P&L Management",
        "Budgeting and Forecasting",
    ],
    "seniority": "leadership",
}

TITLE_WEIGHT, KEYWORD_WEIGHT, SENIORITY_WEIGHT = 0.45, 0.45, 0.10

SENIORITY_TERMS = {
    "leadership": ["leadership", "head", "director", "vp", "vice president", "senior manager"],
    "senior": ["senior", "sr.", "sr ", "lead"],
    "mid": ["mid", "manager", "specialist"],
    "junior": ["junior", "associate", "coordinator"],
}


# ---- Local scoring (no API) --------------------------------------------
def norm(text):
    text = re.sub(r"[^a-zA-Z0-9\s\+\.#/]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def title_score(job_title, target_titles):
    job_title = norm(job_title)
    best = 0.0
    for t in target_titles:
        t_norm = norm(t)
        t_words, j_words = set(t_norm.split()), set(job_title.split())
        if not t_words:
            continue
        overlap = len(t_words & j_words) / len(t_words)
        if t_norm and t_norm in job_title:
            overlap = max(overlap, 0.95)
        best = max(best, overlap)
    return best


KEYWORD_TARGET_HITS = 8


def keyword_score(job_text, skills):
    job_text = norm(job_text)
    if not skills:
        return 0.0, []
    hits = [s for s in skills if norm(s) in job_text]
    return min(1.0, len(hits) / KEYWORD_TARGET_HITS), hits


def seniority_score(job_text, target_level):
    job_text = norm(job_text)
    order = ["junior", "mid", "senior", "leadership"]
    if target_level not in order:
        return 0.5
    target_idx = order.index(target_level)
    for level in order[target_idx:]:
        for term in SENIORITY_TERMS.get(level, []):
            if term in job_text:
                return max(0.0, 1.0 - 0.3 * abs(order.index(level) - target_idx))
    return 0.5


def score_job(fields, kw):
    title = fields.get("Job Title", "")
    desc = fields.get("Job Description Raw", "")
    full_text = f"{title} {desc}"

    t = title_score(title, kw.get("target_titles", []))
    k, hits = keyword_score(full_text, kw.get("skills", []))
    s = seniority_score(full_text, kw.get("seniority", "senior"))

    pct = round((t * TITLE_WEIGHT + k * KEYWORD_WEIGHT + s * SENIORITY_WEIGHT) * 100, 1)
    reasoning = (
        f"Local match (no LLM): title {round(t*100)}%, "
        f"skills {round(k*100)}% ({len(hits)} hits: {', '.join(hits[:8])}), "
        f"seniority fit {round(s*100)}%."
    )
    return pct, reasoning


# ---- Airtable ------------------------------------------------------------
def fetch_pending_jobs(cap=FETCH_CAP):
    """Page through Airtable's Pending Review records up to cap, so there is
    a real pool for the top-TOP_N ranking to choose from."""
    all_records = []
    offset = None
    while len(all_records) < cap:
        params = {"filterByFormula": "{Status} = 'Pending Review'", "pageSize": 100}
        if offset:
            params["offset"] = offset
        resp = requests.get(AIRTABLE_URL, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("records", [])
        all_records.extend(batch)
        offset = data.get("offset")
        if not offset or not batch:
            break
    return all_records[:cap]


def batch_update(updates):
    """updates: list of {'id':..., 'fields':{...}} -- PATCH 10 at a time."""
    for i in range(0, len(updates), 10):
        batch = updates[i:i + 10]
        resp = requests.patch(
            AIRTABLE_URL, headers=HEADERS,
            json={"records": batch, "typecast": True}, timeout=30,
        )
        if resp.status_code >= 300:
            print(f"Batch update failed ({resp.status_code}): {resp.text[:200]}", file=sys.stderr)


# ---- Main ------------------------------------------------------------
def main():
    print("=== score_jobs.py v3 (local scoring, zero API key, >=70% shortlist) ===")    kw = DEFAULT_KEYWORDS
    if os.path.exists(KEYWORDS_PATH):
        with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
            kw = {**DEFAULT_KEYWORDS, **json.load(f)}
        print(f"Loaded keywords from {KEYWORDS_PATH}")

    records = fetch_pending_jobs()
    print(f"Fetched {len(records)} pending jobs")
    if not records:
        print("Nothing to score.")
        return

    scored = []
    for record in records:
        pct, reasoning = score_job(record["fields"], kw)
        scored.append({
            "id": record["id"],
            "pct": pct,
            "reasoning": reasoning,
            "title": record["fields"].get("Job Title", "?"),
        })

    scored.sort(key=lambda r: r["pct"], reverse=True)

   # Shortlist only jobs scoring >= MATCH_THRESHOLD, capped at TOP_N.
   qualifying = [r for r in scored if r["pct"] >= MATCH_THRESHOLD]
   top_ids = {r["id"] for r in qualifying[:TOP_N]}

    updates = []
    for r in scored:
        is_short = r["id"] in top_ids
        updates.append({
            "id": r["id"],
            "fields": {
                "Match Score": r["pct"],
                "AI Reasoning": r["reasoning"],
                "Status": "Shortlisted" if is_short else "Skipped - Low Score",
            },
        })
        print(f"{r['pct']:5.1f}% {'SHORTLIST' if is_short else 'skip '} {r['title']}")

    batch_update(updates)
    print(f"Shortlisted {len(top_ids)}/{len(scored)} jobs scoring >= "
                    f"{MATCH_THRESHOLD}% (capped at top {TOP_N})")
    print("=== complete -- zero LLM calls made ===")


if __name__ == "__main__":
    main()
