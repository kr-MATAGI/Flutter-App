import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os

from app.core.config import settings
from app.routers import (
    auth,
    single_chat,
    status,
    ws_chat,
    user_info,
    image_scan,
    menu_info,
    sample_router
)

from app.routers.controller.agent_ctl import AgentController
from app.routers.controller.db_ctl import DBController
from app.routers.controller.res_ctl import ResController
from app.routers.controller.ocr_ctl import OCR_Controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    ### Controller 초기화
    # AI Model
    agent_controller = AgentController(
        base_model_name=settings.FREE_AI_MODEL, paid_model_name=settings.AI_MODEL
    )
    ocr_controller = OCR_Controller(model_name=settings.OCR_AI_MODEL)

    # DB
    db_controller = DBController()

    # Resource
    res_controller = ResController()

    # Startup
    await agent_controller.build_graph()
    yield # 이전의 코드는 app startup 시 실행되는 코드, 이후 코드는 종료시 실행
    # Shutdown
    pass


app = FastAPI(
    title=os.getenv("PROJECT_NAME", "AI Chat API"),
    version="1.0.0",
    description="AI 채팅을 위한 FastAPI 기반 백엔드 API",
    docs_url=None,  # 기본 /docs 비활성화
    redoc_url=None,  # 기본 /redoc 비활성화
    lifespan=lifespan,
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
app.include_router(user_info.router, prefix="/api/v1/user-info", tags=["user-info"])
app.include_router(image_scan.router, prefix="/api/v1/image-scan", tags=["image-scan"])
app.include_router(menu_info.router, prefix="/api/v1/menu-info", tags=["menu-info"])
app.include_router(sample_router.router, prefix="/api/v1/sample", tags=["sample"])


# 커스텀 OpenAPI 스키마
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
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

def start():
    uvicorn.run(app, host="0.0.0.0", port=8000)