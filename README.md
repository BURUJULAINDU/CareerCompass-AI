\# 🎯 CareerCompass AI

\### AI-Powered Resume Analyzer \& Career Recommendation System



CareerCompass AI is an intelligent resume analysis and career guidance application that helps users understand their skills, explore suitable career opportunities, identify skill gaps, and receive personalized career improvement suggestions.



The application combines Python-based resume processing, career recommendation logic, a FastAPI backend, and an interactive Streamlit dashboard.



\## ✨ Features



\- \*\*Resume Upload:\*\* Upload PDF and DOCX resumes.

\- \*\*Resume Parsing:\*\* Extract education, experience, projects, certifications, and other resume information.

\- \*\*Skill Extraction:\*\* Identify technical and soft skills.

\- \*\*Career Recommendations:\*\* Recommend suitable career paths based on extracted skills.

\- \*\*Career Match Scores:\*\* Display skill-based career fit percentages.

\- \*\*Skill Gap Analysis:\*\* Identify skills required for recommended career roles.

\- \*\*Personalized Learning Suggestions:\*\* Provide next steps to improve career readiness.

\- \*\*Interactive Dashboard:\*\* Explore resume analysis and career recommendations.

\- \*\*Data Visualization:\*\* Compare career match scores through interactive charts.

\- \*\*PDF Report Generation:\*\* Download a career analysis report.



\## 🛠️ Technologies Used



| Technology | Purpose |

|---|---|

| Python | Core programming |

| FastAPI | Backend API |

| Streamlit | Interactive frontend |

| Pandas | Data processing |

| Plotly | Data visualization |

| ReportLab | PDF report generation |

| NLP / Text Processing | Resume analysis and skill extraction |



\## 📁 Project Structure



```text

CareerCompass\_AI/

│

├── backend/

│   ├── career\_recommender.py

│   ├── config.py

│   ├── demo.py

│   ├── job\_description.py

│   ├── main.py

│   ├── resume\_parser.py

│   ├── skill\_extractor.py

│   ├── skill\_gap\_analyzer.py

│   ├── requirements.txt

│   └── .env.example

│

├── data/

│

├── docs/

│   ├── diagrams/

│   ├── sample\_outputs/

│   └── test\_results.md

│

├── frontend/

│   ├── app.py

│   └── src/

│

├── tests/

│

└── .gitignore

```



\## ⚙️ Installation and Setup



\### 1. Clone the repository



```bash

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd CareerCompass\_AI

```



\### 2. Create a virtual environment



\*\*Windows:\*\*



```powershell

python -m venv venv

```



Activate it:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

pip install -r backend/requirements.txt

pip install streamlit plotly pandas reportlab

```



\### 4. Start the FastAPI backend



Open a terminal in the main project folder:



```powershell

python -m uvicorn backend.main:app --reload

```



Backend API:



```text

http://127.0.0.1:8000

```



API documentation:



```text

http://127.0.0.1:8000/docs

```



\### 5. Start the Streamlit frontend



Open another terminal in the main project folder:



```powershell

python -m streamlit run frontend/app.py

```



The application will open in your browser.



\## 🔄 Application Workflow



1\. User uploads a resume.

2\. FastAPI receives the uploaded document.

3\. Resume parser extracts relevant information.

4\. Skill extractor identifies technical and soft skills.

5\. Career recommendation module evaluates suitable roles.

6\. Skill gap analyzer identifies missing skills.

7\. Streamlit displays career recommendations and visualizations.

8\. User downloads a personalized PDF career report.



\## 📊 Career Recommendation Disclaimer



Career match percentages represent skill-based alignment with predefined career requirements. They are indicative scores and do not represent guaranteed employment probability.



\## 🚀 Future Enhancements



\- Integration with real-time job listings.

\- Job description matching.

\- Improved NLP-based skill extraction.

\- Personalized learning roadmaps.

\- Cloud deployment.

\- Enhanced recommendation algorithms.



\## 👩‍💻 Project



\*\*CareerCompass AI\*\*  

AI-powered resume analysis and career guidance.



Developed as a portfolio project using Python, FastAPI, and Streamlit.



