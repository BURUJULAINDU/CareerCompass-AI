# CareerCompass AI – AI-Powered Resume Analysis and Career Guidance System

## 📌 Project Overview

**CareerCompass AI** is an AI-powered career guidance system designed to help students and job seekers understand their resume, identify their skills, discover suitable career opportunities, and improve their professional profiles.

The application combines traditional resume analysis with Generative AI to provide personalized career recommendations, skill-gap analysis, learning roadmaps, and resume improvement suggestions.

Users can create an account, log in, upload their resumes, analyze their skills, and generate a downloadable PDF career analysis report.

## 🎯 Project Objectives

- Analyze uploaded resumes and extract important information.
- Identify technical and soft skills from resumes.
- Recommend suitable career paths based on skills and interests.
- Identify missing skills for selected career roles.
- Generate personalized learning roadmaps using Generative AI.
- Provide AI-based resume improvement suggestions.
- Generate downloadable career analysis reports in PDF format.
- Provide user registration and login functionality.

## ✨ Key Features

### 1. User Authentication
- User registration and login.
- Password hashing for account security.
- Logout functionality.
- Local SQLite database for user account storage.

### 2. Resume Analysis
- Upload resumes for analysis.
- Extract resume information.
- Identify technical skills.
- Detect education, experience, projects, and certifications.
- Calculate resume word count.

### 3. AI-Powered Resume Analysis
- Generate an AI professional summary.
- Identify technical and soft skills.
- Analyze career opportunities.
- Provide personalized career recommendations.

### 4. Career Recommendations
- Recommend suitable career roles.
- Calculate career match percentages.
- Display matching and missing skills.
- Provide recommended next steps.

### 5. Skill Gap Analysis
- Identify missing skills for target career roles.
- Help users understand the skills they need to develop.

### 6. Personalized Learning Roadmap
- Generate week-wise learning recommendations.
- Suggest topics and practical learning activities.
- Guide users toward their selected career goals.

### 7. AI Resume Improvement
- Provide suggestions to improve resume content.
- Recommend project achievements and professional summaries.
- Help users present their skills and experience effectively.

### 8. PDF Career Analysis Report
- Generate downloadable PDF reports.
- Include traditional resume analysis results.
- Include AI-generated professional insights.
- Present career recommendations and learning roadmaps.

## 🛠️ Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| AI Integration | Ollama |
| AI Model | Llama 3.2 |
| Database | SQLite |
| PDF Generation | ReportLab |
| API Communication | REST API |
| Version Control | Git and GitHub |

## 🏗️ System Architecture

The project follows a frontend-backend architecture.

1. **User Interface:** Streamlit provides the application interface for registration, login, resume upload, and displaying results.
2. **Backend Processing:** FastAPI handles resume analysis requests and AI analysis requests.
3. **Resume Processing:** Resume parsing and skill extraction modules identify relevant resume information.
4. **Career Recommendation:** The career recommendation and skill-gap analysis modules evaluate career suitability.
5. **Generative AI:** Ollama with the Llama 3.2 model generates personalized career insights.
6. **Database:** SQLite stores local user account information.
7. **PDF Report:** ReportLab generates downloadable career analysis reports.

## 📂 Project Structure

```text
CareerCompass_AI/
│
├── backend/
│   ├── main.py
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   ├── career_recommender.py
│   ├── skill_gap_analyzer.py
│   ├── llm_service.py
│   └── .env.example
│
├── frontend/
│   ├── app.py
│   └── careercompass_users.db  (created locally)
│
├── .env
├── .gitignore
└── README.md
```

*The database file is generated locally when the application runs. It should not be committed to GitHub.*

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.11
- Git
- Ollama
- Llama 3.2 model

### Step 1: Clone the Repository

```bash
git clone https://github.com/BURUJULAINDU/CareerCompass-AI.git
```

### Step 2: Navigate to the Project

```bash
cd CareerCompass-AI
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\activate
```

### Step 4: Install Dependencies

If the project contains a requirements.txt file, run:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies listed in the project:

```bash
pip install fastapi uvicorn streamlit requests python-dotenv reportlab
```

### Step 5: Configure Ollama

Install Ollama and download the model:

```bash
ollama pull llama3.2:3b
```

Start Ollama:

```bash
ollama serve
```

Keep Ollama running while using AI features.

### Step 6: Configure Environment Variables

Use the provided `.env.example` as a reference and configure your local `.env` file with the required settings.

Example configuration:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=180
MAX_UPLOAD_MB=5
DATABASE_PATH=careercompass.db
```

Do not upload your actual `.env` file or private credentials to GitHub.

## ▶️ Running the Application

The application requires the backend and frontend to run separately.

### Terminal 1: Start the Backend

```powershell
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2: Start the Frontend

Open another terminal:

```powershell
cd frontend
streamlit run app.py
```

The Streamlit application will open in your browser.

## 🔗 Backend API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome endpoint |
| GET | `/health` | Check backend health |
| POST | `/analyze-resume` | Traditional resume analysis |
| POST | `/ai-analyze` | AI-powered resume analysis |
| POST | `/ai-analyze-upload` | AI analysis for uploaded resumes, if enabled in the backend |

## 📊 Expected Application Results

The system provides:

- Resume overview and extracted information.
- Technical and soft skill identification.
- Career match percentages.
- Matching and missing skills.
- AI-generated professional summary.
- Personalized career recommendations.
- Week-wise learning roadmap.
- Resume improvement suggestions.
- Downloadable PDF career analysis report.

## 🔐 Security

- Passwords are stored as salted PBKDF2 hashes in the local SQLite database.
- Private environment files are excluded using `.gitignore`.
- Local user account data is not intended to be committed to the public repository.

**Note:** The current authentication implementation is intended for a local academic project demonstration, not production deployment.

## 🚀 Future Enhancements

- Email verification and password recovery.
- More advanced user authentication.
- Integration with additional AI models.
- Job portal integration.
- Real-time job recommendations.
- Resume comparison with job descriptions.
- More career paths and skill datasets.
- Enhanced analytics dashboard.
- Cloud database integration.
- Deployment to a cloud platform.

## 👩‍💻 Developed By

**Project Name:** CareerCompass AI  
**Project Type:** Academic / GenAI Project  
**Developer:** Indu  
**GitHub Repository:** https://github.com/BURUJULAINDU/CareerCompass-AI

## 📄 Disclaimer

CareerCompass AI provides skill-based career guidance and resume analysis for informational and educational purposes. Career recommendations do not guarantee employment or job placement.