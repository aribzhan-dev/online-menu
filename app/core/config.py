from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALEMBIC_DATABASE_URL: str = os.getenv("ALEMBIC_DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")

    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_LOGIN: str = os.getenv("ADMIN_LOGIN")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD")

    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()