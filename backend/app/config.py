import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
DB_PATH = BASE_DIR / "screening_system.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "PG-AGI AI-Powered Candidate Screening System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    KNOWLEDGE_BASE_DIR: Path = KNOWLEDGE_BASE_DIR
    DB_PATH: Path = DB_PATH
    UPLOAD_DIR: Path = UPLOAD_DIR
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOTAL_INTERVIEW_QUESTIONS: int = 5

settings = Settings()
