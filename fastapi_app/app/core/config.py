import os

from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Chat API"

    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React 프론트엔드
        "http://localhost:8000",  # FastAPI 서버
        "http://localhost",  # 기본 로컬호스트
    ]

    # OpenAI 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "Plz Check .env file")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gpt-4")

    # JWT 토큰 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Kafka 설정
    KAFKA_HOST: str = os.getenv("KAFKA_HOST", "localhost")
    KAFKA_PORT: str = os.getenv("KAFKA_PORT", "9092")
    KAFKA_URL: str = f"{KAFKA_HOST}:{KAFKA_PORT}"

    # Database 설정
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "flutter_server_db")
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    class Config:
        case_sensitive = True


settings = Settings()
