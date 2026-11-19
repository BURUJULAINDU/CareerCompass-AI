"""Job description analyzer: title, required/preferred skills, education and experience."""
from __future__ import annotations

import re
from typing import Dict, Iterable, List

from skill_extractor import extract_skills, get_roles
from skill_gap_analyzer import analyze_gap

_PREFERRED_MARK = re.compile(
    r"\b(preferred|nice to have|good to have|bonus|desirable|an advantage|a plus|plus point)\b", re.I
)
_REQUIRED_MARK = re.compile(
    r"\b(required|requirements|must have|must-have|qualifications|responsibilities|what you.?ll need|skills)\b", re.I
)
_EDU = re.compile(
    r"(bachelor|master|b\.?\s?tech|b\.?\s?e\b|m\.?\s?tech|m\.?\s?sc|b\.?\s?sc|bca|mca|mba|phd|degree|graduate)", re.I
)
_EXP = re.compile(r"(\d+\s*\+?\s*(?:-|to)?\s*\d*\s*\+?\s*years?)", re.I)


def extract_title(jd: str) -> str:
    m = re.search(r"(?im)^\s*(?:job\s*title|position|role)\s*[:\-]\s*(.+)$", jd)
    if m:
        return m.group(1).strip()
    for line in jd.splitlines():
        line = line.strip()
        if line:
            if len(line) <= 80 and not line.endswith("."):
                return line
            break
    lowered = jd.lower()
    for role in get_roles():
        if role.lower() in lowered:
            return role
    return "Not specified"


def _split_required_preferred(jd: str) -> tuple[str, str]:
    required, preferred, mode = [], [], "required"
    for line in jd.splitlines():
        stripped = line.strip()
        is_heading = bool(stripped) and len(stripped) < 60 and (stripped.endswith(":") or stripped.isupper())
        if is_heading and _PREFERRED_MARK.search(stripped):
            mode = "preferred"
            continue
        if is_heading and _REQUIRED_MARK.search(stripped):
            mode = "required"
            continue
        line_mode = "preferred" if _PREFERRED_MARK.search(stripped) else mode
        (preferred if line_mode == "preferred" else required).append(stripped)
    return "\n".join(required), "\n".join(preferred)


def _lines_matching(jd: str, pattern: re.Pattern, limit: int = 4) -> List[str]:
    found = []
    for line in re.split(r"[\n.]", jd):
        line = line.strip(" -\u2022*\t")
        if line and pattern.search(line) and line not in found:
            found.append(line[:200])
    return found[:limit]


def analyze_job_description(jd_text: str, student_skills: Iterable[str]) -> Dict:
    if not jd_text or len(jd_text.strip()) < 40:
        raise ValueError("Please paste a longer job description (at least a few sentences).")
    req_text, pref_text = _split_required_preferred(jd_text)
    required = extract_skills(req_text)["technical"]
    preferred = [s for s in extract_skills(pref_text)["technical"] if s not in required]
    jd_soft = extract_skills(jd_text)["soft"]
    if not required and not preferred:
        raise ValueError("No recognisable technical skills were found in this job description.")
    if not required:  # everything was marked preferred: treat as required for the comparison
        required, preferred = preferred, []

    gap = analyze_gap(student_skills, required, preferred)
    suggestions = []
    for skill in gap["missing"]:
        suggestions.append(
            f"If you have genuinely used {skill}, add it with a project or course as evidence. "
            "If not, add it to your learning plan rather than listing it."
        )
    for p in gap["partial"]:
        suggestions.append(
            f"You show {p['evidence']}, which is related to {p['skill']}. Mention {p['skill']} explicitly if you have used it."
        )
    if gap["matched"]:
        suggestions.append("Move your matched skills (" + ", ".join(gap["matched"][:5]) + ") higher in the resume and back them with project results.")

    return {
        "job_title": extract_title(jd_text),
        "required_skills": required,
        "preferred_skills": preferred,
        "soft_skills_mentioned": jd_soft,
        "education_requirements": _lines_matching(jd_text, _EDU),
        "experience_requirements": _lines_matching(jd_text, _EXP),
        "gap": gap,
        "resume_suggestions": suggestions,
    }
