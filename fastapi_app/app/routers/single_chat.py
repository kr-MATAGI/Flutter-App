from fastapi import (
    APIRouter,
)

from app.core.config import settings

router = APIRouter()


@router.post("/single/chat")
async def send_single_chat(message: str):
    """
    단일 채팅 메시지를 전송하고 AI의 응답을 받습니다.
    """
    try:
        # TODO: OpenAI API 연동 구현
        return {"response": f"메시지 '{message}'에 대한 AI 응답입니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
