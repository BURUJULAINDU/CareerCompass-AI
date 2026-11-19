"""Deterministic skill-gap analysis.

Formula (documented, reproducible - the LLM never calculates it):

    Skill Match Percentage = (matched required skills / total required skills) x 100

A secondary figure, Weighted Coverage, gives each partially matched skill
PARTIAL_CREDIT (0.5) of a point:

    Weighted Coverage = (matched + 0.5 x partial) / total required x 100

Categories
----------
Matched    : the required skill appears in the resume.
Partial    : not present, but a related skill is (catalogue 'related' links) or a
             semantically similar skill is above SEMANTIC_THRESHOLD.
Missing    : neither matched nor partial.
Additional : resume skills that are not required by the target role.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from config import DISCLAIMER, PARTIAL_CREDIT
from skill_extractor import get_catalog, semantic_candidate

FORMULA = (
    "Skill Match % = (matched required skills / total required skills) x 100. "
    f"Weighted Coverage % = (matched + {PARTIAL_CREDIT} x partial) / total x 100."
)


def _dedupe(items: Iterable[str]) -> List[str]:
    seen, out = set(), []
    for item in items:
        if item and item.lower() not in seen:
            seen.add(item.lower())
            out.append(item)
    return out


def canonicalize(skills: Iterable[str]) -> List[str]:
    """Map skill names (any case) to catalogue names; unknown names are kept."""
    lookup = {k.lower(): k for k in get_catalog()}
    return _dedupe(lookup.get(s.strip().lower(), s.strip()) for s in skills if s and s.strip())


def analyze_gap(
    student_skills: Iterable[str],
    required_skills: Iterable[str],
    preferred_skills: Optional[Iterable[str]] = None,
    use_semantic: bool = True,
) -> Dict:
    student = canonicalize(student_skills)
    required = canonicalize(required_skills)
    preferred = [s for s in canonicalize(preferred_skills or []) if s not in required]
    catalog = get_catalog()
    student_set = {s.lower() for s in student}

    matched, partial, missing = [], [], []
    for skill in required:
        if skill.lower() in student_set:
            matched.append(skill)
            continue
        related = [r for r in catalog.get(skill, {}).get("related", []) if r.lower() in student_set]
        if related:
            partial.append({"skill": skill, "evidence": related[0], "method": "related skill"})
            continue
        if use_semantic:
            cand, score = semantic_candidate(skill, student)
            if cand:
                partial.append({"skill": skill, "evidence": cand, "method": f"semantic similarity {score}"})
                continue
        missing.append(skill)

    required_lower = {s.lower() for s in required}
    additional = [s for s in student if s.lower() not in required_lower]
    pref_matched = [s for s in preferred if s.lower() in student_set]
    pref_missing = [s for s in preferred if s.lower() not in student_set]

    total = len(required)
    match_pct = round(len(matched) / total * 100, 1) if total else 0.0
    weighted = round((len(matched) + PARTIAL_CREDIT * len(partial)) / total * 100, 1) if total else 0.0

    return {
        "total_required": total,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "additional": additional,
        "preferred_matched": pref_matched,
        "preferred_missing": pref_missing,
        "match_percentage": match_pct,
        "weighted_coverage": weighted,
        "formula": FORMULA,
        "disclaimer": DISCLAIMER,
    }


def analyze_for_role(student_skills: Iterable[str], role_name: str, roles: Dict[str, dict]) -> Dict:
    if role_name not in roles:
        raise KeyError(f"Unknown role: {role_name}")
    role = roles[role_name]
    result = analyze_gap(student_skills, role["required_technical"], role["preferred_technical"])
    soft = analyze_gap(student_skills, role["soft_skills"], use_semantic=False)
    result["role"] = role_name
    result["soft_skill_gap"] = {"matched": soft["matched"], "missing": soft["missing"]}
    return result
