from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.chat_base import ChatRequest, ChatResponse, DB_ChatLog
from app.routers.controller.agent_ctl import AgentController

router = APIRouter()


@router.post("/chat")
async def send_single_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    단일 채팅 메시지를 전송하고 AI의 응답을 받은 후 데이터베이스에 저장합니다.
    """
    try:
        # OpenAI - ChatGPT 연결
        llm = AgentController()

        # 채팅 메시지 전송
        llm_response = await llm.ainvoke(request.message)
        response = ChatResponse(
            status="success",
            user_id=request.user_id,
            message=llm_response,
            room_id=request.room_id,
        )

        # 데이터베이스에 저장
        db_contents = DB_ChatLog(
            user_id=request.user_id,
            room_id=request.room_id,
            message=request.message,
            response_chat=llm_response,
        )
        db.add(db_contents)
        db.commit()
        db.refresh(db_contents)

        # 채팅 메시지 응답
        return {
            "status": status.HTTP_200_OK,
            "data": response,
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        await db.rollback()  # 오류 발생 시 트랜잭션 롤백
        raise HTTPException(status_code=500, detail=str(e))
