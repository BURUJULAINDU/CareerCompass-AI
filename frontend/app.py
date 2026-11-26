
import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import sqlite3
import hashlib
import hmac
import secrets
import re
from pathlib import Path

from io import BytesIO
from html import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)


# ==================================================
# CONFIGURATION
# ==================================================

API_URL = "http://127.0.0.1:8000/analyze-resume"

AI_API_URL = "http://127.0.0.1:8000/ai-analyze-upload"

# Local SQLite database for user accounts. Add this file to .gitignore.
AUTH_DB_PATH = Path(__file__).resolve().parent / "careercompass_users.db"  # Keep this database out of GitHub
PASSWORD_ITERATIONS = 310_000
st.set_page_config(
    page_title="CareerCompass AI",
    page_icon="🎯",
    layout="wide",
)


# ==================================================
# USER AUTHENTICATION
# ==================================================

def init_auth_db():
    """Create the local user table if it does not already exist."""
    with sqlite3.connect(AUTH_DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def hash_password(password):
    """Hash passwords with PBKDF2-HMAC-SHA256 and a unique random salt."""
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password, stored_hash):
    try:
        salt_hex, expected_hash = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
        ).hex()
        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, TypeError):
        return False


def create_user(email, password):
    email = email.strip().lower()
    password_hash = hash_password(password)
    try:
        with sqlite3.connect(AUTH_DB_PATH) as connection:
            connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def authenticate_user(email, password):
    with sqlite3.connect(AUTH_DB_PATH) as connection:
        row = connection.execute(
            "SELECT password_hash FROM users WHERE email = ? COLLATE NOCASE",
            (email.strip(),),
        ).fetchone()
    return bool(row and verify_password(password, row[0]))


init_auth_db()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""


# ==================================================
# SESSION STATE
# ==================================================

if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

if "ai_analysis" not in st.session_state:
    st.session_state["ai_analysis"] = None


# ==================================================
# PDF REPORT GENERATOR
# ==================================================

def _report_items(value):
    """Convert AI output values into a predictable list for PDF rendering."""
    if value is None:
        return []
    if isinstance(value, dict):
        # Some model responses return a single named item as a dictionary.
        return list(value.items())
    if isinstance(value, (str, int, float)):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def _report_text(value):
    """Render model dictionaries as readable text instead of Python reprs."""
    if isinstance(value, tuple) and len(value) == 2:
        key, item_value = value
        # For {"Week 1": "Learn SQL"}, show the objective only.
        return escape(str(item_value))
    if isinstance(value, dict):
        preferred = ("learning_objective", "objective", "topic", "description", "suggestion", "recommendation", "action")
        for key in preferred:
            if value.get(key):
                return escape(str(value[key]))
        # If the model used a custom key, show its value, not the raw dict.
        readable = [str(v) for v in value.values() if v not in (None, "")]
        return escape(" — ".join(readable)) if readable else ""
    return escape(str(value))


def _clean_resume_item(value):
    """Improve common missing separators in extracted resume lines."""
    text = str(value).replace("|", " — ")
    # Separate university/company names from a location accidentally joined to them.
    text = re.sub(r"(University|College|Institute)([A-Z][a-z]+,\s*[A-Z]{2})", r"\1 — \2", text)
    # Add a space between a project title and its technology list.
    text = re.sub(r"([A-Za-z0-9)])( — )(Power BI|Python|SQL|Machine Learning|Flask)", r"\1\2\3", text)
    return escape(text)


def generate_career_report(result, ai=None):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#4338CA"),
        alignment=TA_CENTER,
        spaceAfter=15,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#4338CA"),
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = styles["BodyText"]

    story = []

    resume = result.get("resume_analysis", {}) or {}
    skills = result.get("skills", {}) or {}
    careers = result.get("career_recommendations", []) or []
    improvements = result.get("resume_improvements", []) or []

    # Title
    story.append(
        Paragraph("CareerCompass AI", title_style)
    )

    story.append(
        Paragraph(
            "Personal Career Analysis Report",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 12))


    # Generative AI analysis (included when AI analysis is available)
    ai = ai if isinstance(ai, dict) else {}
    if ai:
        story.append(Paragraph("Generative AI Resume Analysis", heading_style))

        summary = ai.get("professional_summary", "")
        story.append(Paragraph("<b>AI Professional Summary</b>", body_style))
        story.append(
            Paragraph(
                escape(str(summary)) if summary else "No AI professional summary available.",
                body_style,
            )
        )

        technical_values = _report_items(ai.get("technical_skills"))
        technical_names = {str(item).strip().casefold() for item in technical_values}
        story.append(Paragraph("AI-Identified Technical Skills", heading_style))
        story.append(Paragraph(", ".join(escape(str(item)) for item in technical_values) if technical_values else "No skills identified.", body_style))

        # Remove technical skills accidentally repeated by the model in its soft-skills field.
        soft_values = _report_items(ai.get("soft_skills"))
        technical_terms = ("python", "sql", "power bi", "machine learning", "data visualization", "data cleaning", "web scraping", "etl", "git", "jupyter", "google sheets", "numpy", "pandas", "matplotlib", "seaborn", "scikit-learn", "excel", "dashboard development", "dax")
        clean_soft = []
        for item in soft_values:
            name = str(item).strip()
            lowered = name.casefold()
            if lowered in technical_names or any(term in lowered for term in technical_terms):
                continue
            if name and name not in clean_soft:
                clean_soft.append(name)
        story.append(Paragraph("AI-Identified Soft Skills", heading_style))
        story.append(Paragraph(", ".join(escape(item) for item in clean_soft) if clean_soft else "No reliable soft skills identified by the AI.", body_style))

        story.append(Paragraph("AI Career Recommendations", heading_style))
        for item in _report_items(ai.get("career_recommendations")):
            if isinstance(item, dict):
                role = escape(str(item.get("role", "Career option")))
                score = escape(str(item.get("match_score", "N/A")))
                reason = item.get("reason", "")
                story.append(Paragraph(f"<b>{role} — {score}% AI match</b>", body_style))
                if reason:
                    story.append(Paragraph(escape(str(reason)), body_style))
            else:
                story.append(Paragraph(escape(str(item)), body_style))

        missing = _report_items(ai.get("missing_skills"))
        story.append(Paragraph("AI Skills to Develop", heading_style))
        story.append(
            Paragraph(
                escape(", ".join(str(item) for item in missing))
                if missing else "No missing skills identified by the AI.",
                body_style,
            )
        )

        story.append(Paragraph("Personalized Learning Roadmap", heading_style))
        roadmap = _report_items(ai.get("learning_roadmap"))
        if roadmap:
            for index, item in enumerate(roadmap, start=1):
                if isinstance(item, tuple) and len(item) == 2:
                    week_label, objective_value = item
                    week_match = re.search(r"(\d+)", str(week_label))
                    week = week_match.group(1) if week_match else str(index)
                    story.append(Paragraph(f"<b>Week {escape(week)}</b>: {_report_text(item)}", body_style))
                elif isinstance(item, dict):
                    week = escape(str(item.get("week", index)))
                    objective = _report_text(item)
                    story.append(Paragraph(f"<b>Week {week}</b>: {objective}", body_style))
                else:
                    story.append(Paragraph(f"• {_report_text(item)}", body_style))
        else:
            story.append(Paragraph("No learning roadmap available.", body_style))

        suggestions = _report_items(ai.get("resume_suggestions"))
        story.append(Paragraph("AI Resume Improvement Suggestions", heading_style))
        if suggestions:
            for suggestion in suggestions:
                story.append(Paragraph(f"• {_report_text(suggestion)}", body_style))
        else:
            story.append(Paragraph("No AI resume suggestions available.", body_style))

        story.append(Spacer(1, 10))

    # Resume Overview
    story.append(
        Paragraph("Resume Overview", heading_style)
    )

    story.append(
        Paragraph(
            f"Resume Word Count: {resume.get('word_count', 0)}",
            body_style,
        )
    )

    story.append(Spacer(1, 8))

    # Technical Skills
    story.append(
        Paragraph("Technical Skills", heading_style)
    )

    technical = skills.get("technical", []) or []

    story.append(
        Paragraph(
            escape(", ".join(map(str, technical)))
            if technical
            else "No technical skills detected.",
            body_style,
        )
    )

       # Soft Skills
    story.append(
        Paragraph("Soft Skills", heading_style)
    )

    soft = skills.get("soft", [])

    soft_text = ", ".join(map(str, soft)) if soft else "No soft skills detected."

    story.append(
        Paragraph(escape(soft_text), body_style)
    )

    # Career Recommendations
    story.append(
        Paragraph("Career Recommendations", heading_style)
    )

    if careers:

        for career in careers:

            role = escape(str(career.get("role", "Unknown Role")))
            score = career.get("fit_score", 0)

            story.append(
                Paragraph(
                    f"<b>{role} — {score}% Match</b>",
                    body_style,
                )
            )

            explanation = career.get("why_it_matches", "")

            if explanation:
                story.append(
                    Paragraph(
                        escape(str(explanation)),
                        body_style,
                    )
                )

            matching = career.get("matching_skills", []) or []
            missing = career.get("missing_skills", []) or []
            next_steps = career.get("next_steps", []) or []

            story.append(
                Paragraph(
                    "<b>Matching Skills:</b> "
                    + (
                        escape(", ".join(map(str, matching)))
                        if matching
                        else "None identified"
                    ),
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    "<b>Missing Skills:</b> "
                    + (
                        escape(", ".join(map(str, missing)))
                        if missing
                        else "None identified"
                    ),
                    body_style,
                )
            )

            if next_steps:

                story.append(
                    Paragraph(
                        "<b>Recommended Next Steps:</b>",
                        body_style,
                    )
                )

                for step in next_steps:
                    story.append(
                        Paragraph(
                            "• " + escape(str(step)),
                            body_style,
                        )
                    )

            story.append(Spacer(1, 10))

    else:

        story.append(
            Paragraph(
                "No career recommendations available.",
                body_style,
            )
        )

    # Resume Improvements
    story.append(
        Paragraph(
            "Resume Improvement Suggestions",
            heading_style,
        )
    )

    if improvements:

        for suggestion in improvements:
            story.append(
                Paragraph(
                    "• " + escape(str(suggestion)),
                    body_style,
                )
            )

    else:

        story.append(
            Paragraph(
                "No additional suggestions available.",
                body_style,
            )
        )

    # Education
    story.append(
        Paragraph("Education", heading_style)
    )

    education = resume.get("education", []) or []

    for item in education:
        story.append(
            Paragraph(
                "• " + _clean_resume_item(item),
                body_style,
            )
        )

    if not education:
        story.append(
            Paragraph(
                "No education information detected.",
                body_style,
            )
        )

    # Experience
    story.append(
        Paragraph("Experience", heading_style)
    )

    experience = resume.get("experience", []) or []

    for item in experience:
        story.append(
            Paragraph(
                "• " + _clean_resume_item(item),
                body_style,
            )
        )

    if not experience:
        story.append(
            Paragraph(
                "No experience information detected.",
                body_style,
            )
        )

    # Projects
    story.append(
        Paragraph("Projects", heading_style)
    )

    projects = resume.get("projects", []) or []

    for item in projects:
        story.append(
            Paragraph(
                "• " + _clean_resume_item(item),
                body_style,
            )
        )

    if not projects:
        story.append(
            Paragraph(
                "No projects detected.",
                body_style,
            )
        )

    # Certifications
    story.append(
        Paragraph("Certifications", heading_style)
    )

    certifications = resume.get("certifications", []) or []

    for item in certifications:
        story.append(
            Paragraph(
                "• " + _clean_resume_item(item),
                body_style,
            )
        )

    if not certifications:
        story.append(
            Paragraph(
                "No certifications detected.",
                body_style,
            )
        )

    # Footer note
    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "CareerCompass AI provides skill-based career guidance. "
            "Recommendations are informational and do not guarantee employment.",
            styles["Italic"],
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ==================================================
# STYLING
# ==================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0f172a;
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #e2e8f0 !important;
    }

    div[data-testid="stMetric"] {
        background: #1e293b;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    div.stButton > button {
        background: #6366f1;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.2rem;
    }

    div.stButton > button:hover {
        background: #4f46e5;
        color: white;
    }

    div[data-testid="stExpander"] {
        background-color: #162033;
        border-radius: 10px;
        border: 1px solid #334155;
    }

    </style>
    """,
    unsafe_allow_html=True,
)



# ==================================================
# LOGIN / SIGN UP SCREEN
# ==================================================

if not st.session_state["authenticated"]:
    st.markdown(
        """
        <style>
        .auth-hero {
            background: linear-gradient(120deg, #172554, #4338CA, #7C3AED);
            padding: 42px 28px;
            border-radius: 18px;
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        .auth-hero h1 { color: white !important; }
        .auth-hero p { color: #E0E7FF; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="auth-hero">
            <h1>🎯 CareerCompass AI</h1>
            <p><b>Welcome! Sign in or create an account to continue.</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

    with login_tab:
        with st.form("careercompass_login_form"):
            login_email = st.text_input("Email address", key="login_email")
            login_password = st.text_input(
                "Password", type="password", key="login_password"
            )
            login_submitted = st.form_submit_button(
                "Login", use_container_width=True
            )

        if login_submitted:
            if not login_email.strip() or not login_password:
                st.error("Enter both your email address and password.")
            elif authenticate_user(login_email, login_password):
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = login_email.strip().lower()
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email address or password.")

    with signup_tab:
        with st.form("careercompass_signup_form"):
            signup_email = st.text_input("Email address", key="signup_email")
            signup_password = st.text_input(
                "Create password", type="password", key="signup_password"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password", key="confirm_password"
            )
            signup_submitted = st.form_submit_button(
                "Create Account", use_container_width=True
            )

        if signup_submitted:
            clean_email = signup_email.strip()
            if not clean_email or "@" not in clean_email or "." not in clean_email.split("@")[-1]:
                st.error("Enter a valid email address.")
            elif len(signup_password) < 8:
                st.error("Use a password with at least 8 characters.")
            elif signup_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                created, message = create_user(clean_email, signup_password)
                if created:
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = clean_email.lower()
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.caption(
        "Passwords are stored as salted hashes in a local SQLite database. "
        "This local project version does not include email verification or password reset."
    )
    st.stop()


# ==================================================
# PROFESSIONAL LANDING PAGE
# ==================================================

st.markdown("""
<style>
.hero-section {
    background: linear-gradient(120deg, #172554, #4338CA, #7C3AED);
    padding: 55px 35px;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 25px;
}

.hero-section h1 {
    color: white;
    font-size: 44px;
    font-weight: 800;
    margin-bottom: 12px;
}

.hero-section p {
    color: #E0E7FF;
    font-size: 18px;
    line-height: 1.6;
}

.hero-button {
    display: inline-block;
    background: white;
    color: #4338CA !important;
    padding: 13px 25px;
    border-radius: 10px;
    text-decoration: none !important;
    font-weight: 700;
    margin-top: 15px;
}

.feature-card {
    background: #172033;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 22px;
    min-height: 165px;
    margin-bottom: 12px;
}

.feature-card h3 {
    color: #A5B4FC;
    font-size: 19px;
}

.feature-card p {
    color: #CBD5E1;
    font-size: 14px;
}
</style>

<div class="hero-section">
    <h1>🎯 CareerCompass AI</h1>
    <p><b>Discover Your Skills. Explore Your Future.</b></p>
    <p>
        Transform your resume into a personalized career roadmap.
        Discover your strengths, explore suitable careers,
        and identify the skills you need to grow.
    </p>
    <a href="#resume-analyzer" class="hero-button">
        Explore Resume Analyzer ↓
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🚀 What CareerCompass AI Offers")

st.write(
    "Your intelligent career companion helps you understand "
    "your professional potential and plan your next move."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📄 Resume Analysis</h3>
        <p>Upload your resume and discover your technical
        and soft skills automatically.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Career Matching</h3>
        <p>Explore career recommendations based on
        your existing skills and interests.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Skill Gap Analysis</h3>
        <p>Identify missing skills and receive
        suggestions for your career growth.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown(
    '<div id="resume-analyzer"></div>',
    unsafe_allow_html=True
)

st.markdown("## 📂 Start Your Career Analysis")

st.write(
    "Upload your PDF or DOCX resume below to get started."
)

st.divider()



# ==================================================
# SIDEBAR – CAREER PREFERENCES
# ==================================================

with st.sidebar:

    st.caption(f"Signed in as: {st.session_state.get('user_email', '')}")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_email"] = ""
        st.session_state["analysis"] = None
        st.session_state["ai_analysis"] = None
        st.rerun()

    st.markdown("---")
    st.header("👤 Career Preferences")

    interests_input = st.text_input(
        "Career interests",
        placeholder="Data Science, AI, Analytics",
    )

    interests = [
        item.strip()
        for item in interests_input.split(",")
        if item.strip()
    ]

    st.info(
        "Your interests help personalize career recommendations."
    )

    st.markdown("---")

    st.caption("CareerCompass AI | Resume Intelligence")


# ==================================================
# RESUME UPLOAD
# ==================================================

st.header("📄 Upload your resume")

uploaded_file = st.file_uploader(
    "Choose a resume file",
    type=["pdf", "docx"],
    help="Upload a text-based PDF or DOCX resume.",
)

if uploaded_file:
    st.success(f"File selected: {uploaded_file.name}")

    if st.button("🚀 Analyze My Career", use_container_width=True):
        # Clear previous results before analyzing a new file
        st.session_state["analysis"] = None
        st.session_state["ai_analysis"] = None

        file_bytes = uploaded_file.getvalue()
        content_type = uploaded_file.type or "application/octet-stream"

        traditional_files = {
            "file": (
                uploaded_file.name,
                file_bytes,
                content_type,
            )
        }

        params = [("interests", interest) for interest in interests]

        with st.spinner("Running traditional resume analysis..."):
            try:
                response = requests.post(
                    API_URL,
                    files=traditional_files,
                    params=params,
                    timeout=120,
                )

                if response.status_code != 200:
                    st.error(
                        f"Resume analysis failed ({response.status_code})."
                    )
                    st.code(response.text)
                else:
                    st.session_state["analysis"] = response.json()
                    st.success("Traditional resume analysis completed!")

                    # Run the Ollama analysis on the same uploaded file
                    ai_files = {
                        "file": (
                            uploaded_file.name,
                            file_bytes,
                            content_type,
                        )
                    }

                    with st.spinner(
                        "Generating AI insights with Ollama. This may take a few minutes..."
                    ):
                        try:
                            ai_response = requests.post(
                                AI_API_URL,
                                files=ai_files,
                                timeout=300,
                            )

                            if ai_response.status_code == 200:
                                ai_payload = ai_response.json()
                                st.session_state["ai_analysis"] = (
                                    ai_payload.get("ai_analysis") or {}
                                )
                                st.success(
                                    "Traditional and AI analysis completed!"
                                )
                            else:
                                st.warning(
                                    "Traditional analysis succeeded, but AI "
                                    f"analysis returned {ai_response.status_code}."
                                )
                                st.code(ai_response.text)

                        except requests.exceptions.Timeout:
                            st.warning(
                                "AI analysis timed out. Traditional results "
                                "are still available."
                            )
                        except requests.exceptions.RequestException as e:
                            st.warning(
                                f"Could not connect to the AI endpoint: {e}"
                            )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI. Start the backend on "
                    "http://127.0.0.1:8000 and try again."
                )
            except requests.exceptions.Timeout:
                st.error(
                    "Traditional resume analysis timed out. Please try again."
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
            except ValueError:
                st.error("The backend returned an invalid JSON response.")


# ==================================================
# RESULTS DASHBOARD
# ==================================================

result = st.session_state.get("analysis")

if result:

    st.divider()

    st.header("📊 Resume Analysis Results")

    resume = result.get("resume_analysis", {}) or {}
    skills = result.get("skills", {}) or {}
    careers = result.get("career_recommendations", []) or []
    improvements = result.get("resume_improvements", []) or []
    ai = st.session_state.get("ai_analysis") or {}

    # ==================================================
    # GENERATIVE AI RESUME ANALYSIS
    # ==================================================

    if ai:
        st.divider()
        st.header("🤖 Generative AI Resume Analysis")
        st.caption("Powered by Ollama – Llama 3.2")

        # 1. Professional Summary
        st.subheader("📝 AI Professional Summary")
        st.info(
            ai.get(
                "professional_summary",
                "No professional summary available.",
            )
        )

        # 2. AI-identified skills
        ai_col1, ai_col2 = st.columns(2)

        with ai_col1:
            st.markdown("**💻 Technical Skills**")
            technical_ai = ai.get("technical_skills", []) or []
            if technical_ai:
                st.write(" · ".join(map(str, technical_ai)))
            else:
                st.info("No technical skills identified.")

        with ai_col2:
            st.markdown("**🤝 Soft Skills**")
            soft_ai = ai.get("soft_skills", []) or []
            if soft_ai:
                st.write(" · ".join(map(str, soft_ai)))
            else:
                st.info("No soft skills identified.")

        # 3. AI career recommendations
        st.subheader("🎯 AI Career Recommendations")
        ai_careers = ai.get("career_recommendations", []) or []

        if ai_careers:
            for career in ai_careers:
                role = career.get("role", "Unknown Role")
                score = career.get("match_score", 0)
                reason = career.get("reason", "")

                try:
                    score_value = max(0, min(int(float(score)), 100))
                except (TypeError, ValueError):
                    score_value = 0

                with st.expander(f"{role} — {score_value}% AI match"):
                    st.progress(score_value)
                    if reason:
                        st.write(reason)
        else:
            st.info("No AI career recommendations available.")

        # 4. Skills to develop
        st.subheader("📚 Skills to Develop")
        missing_ai = ai.get("missing_skills", []) or []

        if missing_ai:
            st.write(" · ".join(map(str, missing_ai)))
        else:
            st.success("No missing skills identified by the AI.")

        # 5. Learning roadmap
        st.subheader("🗓️ Personalized Learning Roadmap")
        roadmap = ai.get("learning_roadmap", []) or []

        # The AI may return roadmap entries as dictionaries or plain strings.
        # Normalize a single string/object into a list before displaying it.
        if isinstance(roadmap, (str, dict)):
            roadmap = [roadmap]

        if roadmap:
            for index, item in enumerate(roadmap, start=1):
                if isinstance(item, dict):
                    week = item.get("week", index)
                    objective = (
                        item.get("learning_objective")
                        or item.get("objective")
                        or item.get("topic")
                        or item.get("description")
                        or ""
                    )
                    st.markdown(f"**Week {week}**")
                    if objective:
                        st.write(objective)
                    else:
                        st.write(item)
                else:
                    st.write(f"**{index}.** {item}")
        else:
            st.info("No learning roadmap available.")

        # 6. AI resume suggestions
        st.subheader("💡 AI Resume Improvement Suggestions")
        ai_suggestions = ai.get("resume_suggestions", []) or []

        if ai_suggestions:
            for suggestion in ai_suggestions:
                st.write(f"✅ {suggestion}")
        else:
            st.info("No AI resume suggestions available.")

    else:
        st.info(
            "AI analysis is not available for this upload. "
            "Traditional resume results are shown below."
        )


    # ==================================================
    # RESUME SUMMARY
    # ==================================================

    st.subheader("📝 Resume Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Resume Word Count",
            resume.get("word_count", 0),
        )

    with col2:
        st.metric(
            "Technical Skills",
            len(skills.get("technical", [])),
        )

    with col3:
        st.metric(
            "Soft Skills",
            len(skills.get("soft", [])),
        )


    # ==================================================
    # SKILLS
    # ==================================================

    st.subheader("🧠 Extracted Skills")

    tab1, tab2 = st.tabs(
        ["💻 Technical Skills", "🤝 Soft Skills"]
    )

    with tab1:

        technical = skills.get("technical", [])

        if technical:
            st.write(" · ".join(technical))
        else:
            st.info("No technical skills detected.")

    with tab2:

        soft = skills.get("soft", [])

        if soft:
            st.write(" · ".join(soft))
        else:
            st.info("No soft skills detected.")


    # ==================================================
    # CAREER RECOMMENDATIONS
    # ==================================================

    st.subheader("🎯 Career Recommendations")

    if careers:

        for career in careers:

            role = career.get("role", "Unknown Role")
            score = career.get("fit_score", 0)

            with st.expander(
                f"{role} — {score}% match",
                expanded=True,
            ):

                st.progress(
                    max(0, min(int(score), 100))
                )

                st.write(
                    career.get("why_it_matches", "")
                )

                # Matching Skills
                st.markdown("**Matching Skills**")

                matching = career.get("matching_skills", [])

                if matching:
                    st.success(", ".join(matching))
                else:
                    st.write("No direct skill matches found.")

                # Missing Skills
                st.markdown("**Missing Skills**")

                missing = career.get("missing_skills", [])

                if missing:
                    st.warning(", ".join(missing))
                else:
                    st.success("No missing skills identified!")

                # Next Steps
                st.markdown("**Recommended Next Steps**")

                next_steps = career.get("next_steps", [])

                if next_steps:

                    for step in next_steps:
                        st.write(f"• {step}")

                # Disclaimer
                st.caption(
                    career.get("disclaimer", "")
                )

    else:

        st.info("No career recommendations available.")


    # ==================================================
    # CAREER MATCH CHART
    # ==================================================

    if careers:

        st.subheader("📊 Career Match Overview")

        chart_data = [
            {
                "Career": career.get("role", "Unknown Role"),
                "Match Score": float(
                    career.get("fit_score", 0)
                ),
            }
            for career in careers
        ]

        chart_df = pd.DataFrame(chart_data)

        chart_df = chart_df.sort_values(
            by="Match Score",
            ascending=True,
        )

        fig = px.bar(
            chart_df,
            x="Match Score",
            y="Career",
            orientation="h",
            color="Match Score",
            text="Match Score",
            color_continuous_scale="Viridis",
            range_x=[0, 100],
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
        )

        fig.update_layout(
            height=400,
            template="plotly_dark",
            xaxis_title="Career Match (%)",
            yaxis_title="",
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    # ==================================================
    # RESUME IMPROVEMENTS
    # ==================================================

    st.subheader("💡 Resume Improvement Suggestions")

    if improvements:

        for suggestion in improvements:
            st.write(f"• {suggestion}")

    else:

        st.info(
            "No additional improvement suggestions returned."
        )


    # ==================================================
    # EDUCATION
    # ==================================================

    st.subheader("🎓 Education")

    education = resume.get("education", [])

    if education:

        for item in education:
            st.write(f"• {item}")

    else:

        st.write("No education information detected.")


    # ==================================================
    # EXPERIENCE
    # ==================================================

    st.subheader("💼 Experience")

    experience = resume.get("experience", [])

    if experience:

        for item in experience:
            st.write(f"• {item}")

    else:

        st.write("No experience information detected.")


    # ==================================================
    # PROJECTS
    # ==================================================

    st.subheader("🛠️ Projects")

    projects = resume.get("projects", [])

    if projects:

        for item in projects:
            st.write(f"• {item}")

    else:

        st.write("No projects detected.")


    # ==================================================
    # CERTIFICATIONS
    # ==================================================

    st.subheader("📜 Certifications")

    certifications = resume.get("certifications", [])

    if certifications:

        for item in certifications:
            st.write(f"• {item}")

    else:

        st.write("No certifications detected.")


    # ==================================================
    # FOOTER
    # ==================================================

    st.divider()

    st.caption(
        "CareerCompass AI provides skill-based career guidance. "
        "Recommendations are informational and do not guarantee employment."
    )


    # ==================================================
    # DOWNLOAD CAREER REPORT
    # ==================================================

    st.subheader("📥 Download Your Career Report")

    pdf_data = generate_career_report(result, ai)

    st.download_button(
        label="📄 Download Career Report (PDF)",
        data=pdf_data,
        file_name="CareerCompass_Career_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    