from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.config import settings

router = APIRouter()


@router.post("/send")
async def send_message(message: str):
    """
    채팅 메시지를 전송하고 AI의 응답을 받습니다.
    """
    try:
        # TODO: OpenAI API 연동 구현
        return {"response": f"메시지 '{message}'에 대한 AI 응답입니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history():
    """
    채팅 기록을 조회합니다.
    """
    # TODO: 데이터베이스 연동 구현
    return {"history": []}
