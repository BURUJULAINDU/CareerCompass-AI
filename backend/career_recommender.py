"""Deterministic career recommendation engine.

Score for each role (0-100):

    base  = (matched_required + 0.5*partial_required) / total_required
    bonus = 0.5 * (matched_preferred / total_preferred)  [preferred skills count half]
    score = (base*0.8 + bonus*0.2) x 100  (+ up to 10 points for stated interests)

The score ranks roles by skill coverage only. It is not a hiring probability.
Explanations here are rule-based; the LLM can rephrase them later but never
changes the ranking.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from config import DISCLAIMER
from skill_extractor import get_roles
from skill_gap_analyzer import analyze_for_role, canonicalize

INTEREST_BONUS_MAX = 10.0


def _interest_bonus(interests: Iterable[str], keywords: List[str]) -> float:
    words = {i.strip().lower() for i in interests if i and i.strip()}
    if not words:
        return 0.0
    hits = sum(1 for k in keywords if any(w in k or k in w for w in words))
    return round(min(INTEREST_BONUS_MAX, hits * 5.0), 1)


def recommend_careers(
    student_skills: Iterable[str],
    interests: Optional[Iterable[str]] = None,
    top_n: int = 5,
) -> List[Dict]:
    roles = get_roles()
    skills = canonicalize(student_skills)
    results = []
    for name, role in roles.items():
        gap = analyze_for_role(skills, name, roles)
        total_req = gap["total_required"] or 1
        base = (len(gap["matched"]) + 0.5 * len(gap["partial"])) / total_req
        pref_total = len(role["preferred_technical"]) or 1
        bonus = len(gap["preferred_matched"]) / pref_total
        bonus_interest = _interest_bonus(interests or [], role["interest_keywords"])
        score = round(min(100.0, (base * 0.8 + bonus * 0.2) * 100 + bonus_interest), 1)

        if gap["matched"]:
            why = (
                f"Your resume already shows {len(gap['matched'])} of {gap['total_required']} "
                f"required skills for this role ({', '.join(gap['matched'][:4])}"
                f"{'...' if len(gap['matched']) > 4 else ''})."
            )
        elif gap["partial"]:
            why = "Your resume shows related skills, but none of the core required skills directly."
        else:
            why = "Few of this role's core skills appear in your resume yet."
        if bonus_interest:
            why += " Your stated interests also align with this role."

        results.append({
            "role": name,
            "description": role["description"],
            "fit_score": score,
            "why_it_matches": why,
            "required_technical": role["required_technical"],
            "required_soft": role["soft_skills"],
            "matching_skills": gap["matched"],
            "partial_skills": [p["skill"] for p in gap["partial"]],
            "missing_skills": gap["missing"],
            "next_steps": role["beginner_learning"][:3],
            "disclaimer": DISCLAIMER + " Recommendations do not guarantee employment.",
        })
    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results[:top_n]
