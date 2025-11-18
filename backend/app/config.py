from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "PharmaDocAI"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = (
        "sqlite+aiosqlite:///./pharmadocai.db"
    )  # local dev database

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
