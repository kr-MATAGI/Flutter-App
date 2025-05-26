from pydantic_settings import BaseSettings
from typing import List
import os
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
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gpt-4")

    # JWT 토큰 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Kafka 설정
    KAFKA_BOOTSTRAP_SERVERS: List[str] = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    ).split(",")
    KAFKA_CONSUMER_GROUP: str = "chat_consumer_group"
    KAFKA_CHAT_TOPIC: str = "chat_messages"

    class Config:
        case_sensitive = True


settings = Settings()
