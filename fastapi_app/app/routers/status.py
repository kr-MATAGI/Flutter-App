import io
from fastapi import (
    APIRouter,
    HTTPException,
)
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.routers.controller.res_ctl import ResController
from app.routers.controller.agent_ctl import AgentController

router = APIRouter()
res_controller = ResController()


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


@router.get("/res-mem")
async def get_res_monitor():
    return await res_controller.get_memory_usage()


@router.get("/res-threshold")
async def get_res_threshold():
    return await res_controller.get_memory_alert()


@router.get("/graph")
async def get_agent_graph():
    """
    에이전트 그래프의 이미지를 반환합니다.
    """
    try:
        agent_controller = AgentController()
        image_bytes = await agent_controller.show_graph()
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
