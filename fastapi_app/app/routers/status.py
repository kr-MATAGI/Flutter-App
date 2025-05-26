from fastapi import (
    APIRouter,
    HTTPException,
)

from app.core.config import settings

router = APIRouter()


@router.get("/ping")
async def ping_pong():
    return {"status": "ok"}


@router.get("/api-info")
async def get_status():
    return {
        "status": "ok",
        "api_key": settings.OPENAI_API_KEY,
        "model_name": settings.AI_MODEL_NAME,
    }
