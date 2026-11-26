
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from resume_parser import extract_text, parse_resume, suggest_improvements, ResumeError
from career_recommender import recommend_careers
from llm_service import analyze_resume_with_llm


app = FastAPI(
    title="CareerCompass AI",
    description="AI-powered career guidance and resume analysis system",
    version="1.0.0"
)


# Request model for AI analysis
class AIResumeRequest(BaseModel):
    resume_text: str


@app.get("/")
def home():
    return {
        "message": "Welcome to CareerCompass AI",
        "status": "Backend running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# NEW: Ollama-powered AI resume analysis
@app.post("/ai-analyze")
def ai_analyze_resume(request: AIResumeRequest):
    try:
        if not request.resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Resume text cannot be empty."
            )

        result = analyze_resume_with_llm(request.resume_text)

        return {
            "status": "success",
            "message": "AI resume analysis completed successfully",
            "ai_analysis": result
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI analysis failed. Check that Ollama is running and the configured model is available."
        )


@app.post("/ai-analyze-upload")
async def ai_analyze_uploaded_resume(file: UploadFile = File(...)):
    try:
        file_data = await file.read()

        if not file_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        resume_text = extract_text(file.filename or "", file_data)

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the resume."
            )

        result = analyze_resume_with_llm(resume_text)

        return {
            "status": "success",
            "message": "AI resume analysis completed successfully",
            "ai_analysis": result
        }

    except ResumeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI analysis failed. Check Ollama and the configured model."
        )

# EXISTING: Traditional resume analysis
@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    interests: list[str] = Query(default=[]),
):
    try:
        # Read uploaded resume
        file_data = await file.read()

        if not file_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # Extract text from PDF, DOCX or supported file
        resume_text = extract_text(file.filename or "", file_data)

        # Parse resume into structured information
        parsed_resume = parse_resume(resume_text)

        # Collect skills for career recommendation
        student_skills = (
            parsed_resume["technical_skills"]
            + parsed_resume["soft_skills"]
        )

        # Generate career recommendations
        career_recommendations = recommend_careers(
            student_skills=student_skills,
            interests=interests,
            top_n=5
        )

        # Generate resume improvement suggestions
        improvements = suggest_improvements(parsed_resume)

        return {
            "status": "success",
            "message": "Resume analyzed successfully",
            "resume_analysis": parsed_resume,
            "skills": {
                "technical": parsed_resume["technical_skills"],
                "soft": parsed_resume["soft_skills"]
            },
            "career_recommendations": career_recommendations,
            "resume_improvements": improvements
        }

    except ResumeError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {str(e)}"
        )
