import io
from fastapi import (
    APIRouter,
    HTTPException,
)
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.routers.controller.res_ctl import ResController
from app.routers.controller.llm_ctl import LLM_Controller

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


@router.get("/show-agent-graph")
async def get_agent_graph():
    # @TODO: 그래프 FastAPI로 보여줄 수 있는지 확인
    buf = io.BytesIO()
    graph_image = await LLM_Controller.show_graph()
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
