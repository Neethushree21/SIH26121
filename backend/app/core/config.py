from pydantic_settings import BaseSettings
from typing import List, Union
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_DB_PATH = os.path.join(ROOT_DIR, "nwis_wells.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "NWIS - Nearby Wells Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", os.path.join(ROOT_DIR, "chroma_data"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(ROOT_DIR, "uploads"))
    
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Normalize SQLite path so it always resolves to the root workspace directory
if settings.DATABASE_URL.startswith("sqlite:///."):
    clean_rel = settings.DATABASE_URL.replace("sqlite:///./", "").replace("sqlite:///.", "")
    abs_db = os.path.abspath(os.path.join(ROOT_DIR, clean_rel)).replace("\\", "/")
    settings.DATABASE_URL = f"sqlite:///{abs_db}"

# Ensure directories exist
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
