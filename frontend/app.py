
import streamlit as st
import requests
import plotly.express as px
import pandas as pd

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

st.set_page_config(
    page_title="CareerCompass AI",
    page_icon="🎯",
    layout="wide",
)


# ==================================================
# SESSION STATE
# ==================================================

if "analysis" not in st.session_state:
    st.session_state["analysis"] = None


# ==================================================
# PDF REPORT GENERATOR
# ==================================================

def generate_career_report(result):

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
        Paragraph(soft_text, body_style)
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
                "• " + escape(str(item)),
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
                "• " + escape(str(item)),
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
                "• " + escape(str(item)),
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
                "• " + escape(str(item)),
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

    if st.button(
        "🚀 Analyze My Career",
        use_container_width=True,
    ):

        with st.spinner("Analyzing your resume... Please wait."):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }

                params = [
                    ("interests", interest)
                    for interest in interests
                ]

                response = requests.post(
                    API_URL,
                    files=files,
                    params=params,
                    timeout=120,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state["analysis"] = result

                    st.success(
                        "Resume analysis completed successfully!"
                    )

                else:

                    st.error(
                        f"API Error: {response.status_code}"
                    )

                    st.code(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to backend. "
                    "Please start FastAPI on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. Please try again."
                )

            except Exception as e:

                st.error(f"Unexpected error: {e}")


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

    pdf_data = generate_career_report(result)

    st.download_button(
        label="📄 Download Career Report (PDF)",
        data=pdf_data,
        file_name="CareerCompass_Career_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    