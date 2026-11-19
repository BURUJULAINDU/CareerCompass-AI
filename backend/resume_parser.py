"""Resume upload validation, text extraction and structure parsing.

Privacy: uploaded files are processed in memory only and never written to disk.
Contact details (email, phone numbers) are masked in any text returned to the UI.
"""
from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Dict, List

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB
from skill_extractor import extract_skills


class ResumeError(ValueError):
    """Raised for any problem with an uploaded resume (shown to the user)."""


def validate_upload(filename: str, data: bytes) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ResumeError(
            f"Unsupported file type '{ext or 'none'}'. Please upload a PDF, DOCX or TXT file."
        )
    if not data:
        raise ResumeError("The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ResumeError(f"The file is larger than the {MAX_UPLOAD_MB} MB limit.")
    return ext


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ResumeError("The PDF is password protected and cannot be read.")
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except ResumeError:
        raise
    except Exception as exc:
        raise ResumeError(f"The PDF could not be read ({type(exc).__name__}). It may be corrupted.") from exc


def _extract_docx(data: bytes) -> str:
    from docx import Document

    try:
        doc = Document(io.BytesIO(data))
    except Exception as exc:
        raise ResumeError(f"The DOCX file could not be read ({type(exc).__name__}). It may be corrupted.") from exc
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def extract_text(filename: str, data: bytes) -> str:
    ext = validate_upload(filename, data)
    if ext == ".pdf":
        text = _extract_pdf(data)
    elif ext == ".docx":
        text = _extract_docx(data)
    else:
        text = data.decode("utf-8", errors="ignore")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 30:
        raise ResumeError(
            "No readable text was found. Scanned/image-only resumes are not supported; "
            "please upload a text-based PDF or DOCX."
        )
    return text


# ------------------------------------------------------------------ privacy
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")


def mask_pii(text: str) -> str:
    text = _EMAIL.sub("[email hidden]", text)
    return _PHONE.sub("[phone hidden]", text)


# ------------------------------------------------------------------ sections
SECTION_HEADINGS = {
    "summary": ["summary", "profile", "objective", "career objective", "professional summary", "about me"],
    "education": ["education", "academic qualifications", "academics", "educational qualification"],
    "experience": ["experience", "work experience", "internship", "internships", "professional experience", "employment"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "courses", "licenses", "training"],
    "skills": ["skills", "technical skills", "key skills", "core competencies"],
    "achievements": ["achievements", "awards", "honors"],
}
_HEADING_LOOKUP = {h: sec for sec, hs in SECTION_HEADINGS.items() for h in hs}


def split_sections(text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {k: [] for k in SECTION_HEADINGS}
    sections["header"] = []
    current = "header"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = re.sub(r"[:\-_=*#]+$", "", line.lower()).strip()
        if key in _HEADING_LOOKUP and len(line) < 40:
            current = _HEADING_LOOKUP[key]
            continue
        sections[current].append(re.sub(r"^[\u2022\-*\u25cf]\s*", "", line))
    return sections


def parse_resume(text: str) -> Dict:
    sections = split_sections(text)
    skills = extract_skills(text)
    return {
        "technical_skills": skills["technical"],
        "soft_skills": skills["soft"],
        "education": sections["education"],
        "experience": sections["experience"],
        "projects": sections["projects"],
        "certifications": sections["certifications"],
        "summary_text": " ".join(sections["summary"]),
        "word_count": len(text.split()),
        "sections_found": [k for k, v in sections.items() if v and k != "header"],
    }


def suggest_improvements(parsed: Dict) -> List[str]:
    """Rule-based suggestions (deterministic, no LLM)."""
    tips = []
    if not parsed["summary_text"]:
        tips.append("Add a 2-3 line professional summary stating your target role and strongest skills.")
    if not parsed["projects"]:
        tips.append("Add a Projects section: describe what you built, the tools used and the result.")
    if not parsed["certifications"]:
        tips.append("List relevant certifications or online courses you have completed.")
    if len(parsed["technical_skills"]) < 6:
        tips.append("Only a few technical skills were detected. List the tools you actually use (languages, libraries, databases).")
    if not parsed["soft_skills"]:
        tips.append("Show soft skills through examples (teamwork in a group project, presenting results).")
    body = " ".join(parsed["experience"] + parsed["projects"])
    if body and not re.search(r"\d", body):
        tips.append("Add measurable results (numbers, percentages, dataset sizes) to project and experience bullets.")
    if parsed["word_count"] < 150:
        tips.append("The resume looks short. Add more detail about projects and coursework.")
    elif parsed["word_count"] > 900:
        tips.append("The resume is long. Aim for one page for a fresher and keep only relevant content.")
    if not tips:
        tips.append("The structure looks complete. Tailor the skills and project descriptions to each job description.")
    return tips
