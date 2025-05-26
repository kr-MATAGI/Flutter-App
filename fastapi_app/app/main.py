from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.routers import auth
from fastapi_app.app.routers import kafka_chat

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title=os.getenv("PROJECT_NAME", "AI Chat API"),
    version="1.0.0",
    description="AI 채팅을 위한 FastAPI 기반 백엔드 API",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("BACKEND_CORS_ORIGINS", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(kafka_chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "AI Chat API에 오신 것을 환영합니다!"}
