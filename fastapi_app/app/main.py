from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.routers import auth, single_chat, status, ws_chat

from app.routers.controller.ai_resp_ctl import AiRespController
from app.routers.controller.db_ctl import DBController
from app.routers.controller.res_ctl import ResController

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title=os.getenv("PROJECT_NAME", "AI Chat API"),
    version="1.0.0",
    description="AI 채팅을 위한 FastAPI 기반 백엔드 API",
    docs_url=None,  # 기본 /docs 비활성화
    redoc_url=None,  # 기본 /redoc 비활성화
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서만 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ws_chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    single_chat.router, prefix="/api/v1/single-chat", tags=["single-chat"]
)
app.include_router(status.router, prefix="/api/v1/status", tags=["status"])


### Controller 초기화
# AI Model
AiRespController(model_name=os.getenv("FREE_AI_MODEL", "llama"))
AiRespController(model_name=os.getenv("AI_MODEL", "chatgpt"))

# DB
DBController()

# Resource
ResController()


# 커스텀 OpenAPI 스키마
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=os.getenv("PROJECT_NAME", "AI Chat API"),
        version=os.getenv("VERSION", "1.0.0"),
        description=os.getenv("DESCRIPTION", "AI 채팅을 위한 FastAPI 기반 백엔드 API"),
        routes=app.routes,
    )

    # 서버 정보 추가
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# 커스텀 swagger UI 엔드포인트
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{os.getenv('PROJECT_NAME', 'AI Chat API')} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )


@app.get("/")
async def root():
    return {"message": "AI Chat API에 오신 것을 환영합니다!"}
