# backend/app/config.py
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# ---- load .env once, at import time ----
BASE_DIR = Path(__file__).resolve().parent          # backend/app
ENV_PATH = BASE_DIR.parent / ".env"                 # backend/.env
load_dotenv(ENV_PATH)


class Settings(BaseSettings):
    # General
    PROJECT_NAME: str = "PharmaDocAI"
    API_V1_PREFIX: str = "/api/v1"

    # Database (needed by database.py -> fixes AttributeError)
    DATABASE_URL: str = "sqlite:///./pharmadocai.db"

    # LLM
    LLM_PROVIDER: str = "groq"                      # default, can override in .env
    GROQ_API_KEY: str = ""                          # must be set in .env
    EMBEDDING_MODEL: str = "groq-embedding-3-small"

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
