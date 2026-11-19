"""Central configuration for CareerCompass AI.

Student: BURUJULA INDU | USN: SCA25MSD017
Values can be overridden with environment variables or a .env file.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
SKILLS_FILE = DATA_DIR / "career_skills.json"


def _load_env_file() -> None:
    """Tiny .env reader so the project does not need python-dotenv."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "careercompass.db"))
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",")

# Partial matches count as this fraction in the secondary "weighted coverage" figure.
PARTIAL_CREDIT = 0.5
SEMANTIC_THRESHOLD = 0.80

DISCLAIMER = (
    "The skill match percentage is a skill coverage indicator based on the skills "
    "found in the resume text. It is not a probability of getting hired or a "
    "guarantee of employment."
)
