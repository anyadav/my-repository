"""
score_jobs.py (v2) — ZERO-API-KEY local scoring. Gemini removed entirely.

Why: Gemini free-tier quota exhaustion (429s) was killing daily runs. This
version scores jobs locally with weighted title/keyword/seniority overlap —
no LLM, no external calls for scoring, no quota, no rate limiting needed.
The only API used is Airtable (read pending + write scores), which is
unavoidable and nowhere near its limits (5 req/s).

Fixes vs v1:
1. FIELD NAME BUG: v1 read job.get("title") / job.get("description") but the
   Airtable fields are "Job Title" / "Job Description Raw" — Gemini was
   scoring empty text. Fixed.
2. "Hiring Manager" field didn't exist (actual: "Hiring Manager Name") —
   removed; local scoring doesn't extract names anyway.
3. Status PATCH now uses typecast:true so new singleSelect options
   ("Skipped - Low Score") are auto-created instead of silently failing.
4. Top-5 fallback (was a TODO comment in v1) is implemented.
5. Batch PATCH (10 records/request) instead of one PATCH per record.

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

MATCH_THRESHOLD = 85
FALLBACK_TOP = 5
KEYWORDS_PATH = "keywords.json"

DEFAULT_KEYWORDS = {
    "target_titles": [
        "Delivery Manager", "Program Manager", "Delivery Head",
        "Account Delivery Head", "Project Manager", "Engineering Manager",
        "Service Delivery Manager", "Senior Delivery Manager",
    ],
    "skills": [
        "delivery", "program management", "SLA", "KPI", "SLO", "governance",
        "managed services", "stakeholder", "MBR", "QBR", "cross-functional",
        "staff augmentation", "global delivery", "client", "operations",
        "agile", "escalation", "transition",
    ],
    "seniority": "leadership",
}

TITLE_WEIGHT, KEYWORD_WEIGHT, SENIORITY_WEIGHT = 0.45, 0.45, 0.10
SENIORITY_TERMS = {
    "leadership": ["head", "director", "vp", "vice president", "senior manager"],
    "senior": ["senior", "sr.", "sr ", "lead"],
    "mid": ["manager", "specialist"],
    "junior": ["associate", "junior", "coordinator"],
}


# ---- Local scoring (no API) --------------------------------------------
def norm(text):
    text = re.sub(r"[^a-zA-Z0-9\s\+\.#/]", " ", text or "").lower()
    return re.sub(r"\s+", " ", text).strip()


def title_score(job_title, target_titles):
    jt = norm(job_title)
    best = 0.0
    for t in target_titles:
        t_norm = norm(t)
        t_words, j_words = set(t_norm.split()), set(jt.split())
        if not t_words:
            continue
        overlap = len(t_words & j_words) / len(t_words)
        if t_norm in jt or jt in t_norm:
            overlap = max(overlap, 0.95)
        best = max(best, overlap)
    return best


def keyword_score(job_text, skills):
    jt = norm(job_text)
    if not skills:
        return 0.0
    hits = [s for s in skills if norm(s) in jt]
    return len(hits) / len(skills), hits


def seniority_score(job_text, target_level):
    jt = norm(job_text)
    order = ["junior", "mid", "senior", "leadership"]
    if target_level not in order:
        return 0.5
    target_idx = order.index(target_level)
    for level in [order[target_idx]] + order:
        for term in SENIORITY_TERMS.get(level, []):
            if term in jt:
                return max(0.0, 1.0 - 0.3 * abs(order.index(level) - target_idx))
    return 0.5


def score_job(fields, kw):
    title = fields.get("Job Title", "")
    desc = fields.get("Job Description Raw", "")
    full_text = f"{title} {desc}"

    t = title_score(title, kw["target_titles"])
    k, hits = keyword_score(full_text, kw["skills"])
    s = seniority_score(full_text, kw.get("seniority", "senior"))

    pct = round((t * TITLE_WEIGHT + k * KEYWORD_WEIGHT + s * SENIORITY_WEIGHT) * 100, 1)
    reasoning = (
        f"Local match (no LLM): title {round(t*100)}%, "
        f"skills {round(k*100)}% ({len(hits)}/{len(kw['skills'])}: {', '.join(hits[:8])}), "
        f"seniority fit {round(s*100)}%."
    )
    return pct, reasoning


# ---- Airtable ------------------------------------------------------------
def fetch_pending_jobs(cap=50):
    params = {"filterByFormula": "{Status} = 'Pending Review'", "maxRecords": cap}
    resp = requests.get(AIRTABLE_URL, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("records", [])


def batch_update(updates):
    """updates: list of {'id':..., 'fields':{...}} — PATCH 10 at a time."""
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
    print("=== score_jobs.py v2 (local scoring, zero API key) ===")

    kw = DEFAULT_KEYWORDS
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
        scored.append({"id": record["id"], "pct": pct, "reasoning": reasoning,
                       "title": record["fields"].get("Job Title", "?")})

    scored.sort(key=lambda x: x["pct"], reverse=True)
    shortlisted_ids = {s["id"] for s in scored if s["pct"] >= MATCH_THRESHOLD}

    fallback_used = False
    if not shortlisted_ids:
        shortlisted_ids = {s["id"] for s in scored[:FALLBACK_TOP]}
        fallback_used = True

    updates = []
    for s in scored:
        is_short = s["id"] in shortlisted_ids
        note = " [top-5 fallback: below threshold]" if (is_short and fallback_used) else ""
        updates.append({
            "id": s["id"],
            "fields": {
                "Match Score": s["pct"],
                "AI Reasoning": s["reasoning"] + note,
                "Status": "Shortlisted" if is_short else "Skipped - Low Score",
            },
        })
        print(f"  {s['pct']:5.1f}%  {'SHORTLIST' if is_short else 'skip     '}  {s['title']}")

    batch_update(updates)
    print(f"Shortlisted {len(shortlisted_ids)}/{len(scored)}"
          + (" (top-5 fallback)" if fallback_used else ""))
    print("=== complete — zero LLM calls made ===")


if __name__ == "__main__":
    main()
