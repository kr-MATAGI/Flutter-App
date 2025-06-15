from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.models.chat_base import ChatRequest, ChatResponse, DB_ChatLog
from app.models.graph_state import GraphBaseState
from app.routers.controller.agent_ctl import AgentController
from app.utils.logger import setup_logger

router = APIRouter()

logger = setup_logger("[Router] Single Chat")

class AgentChatRequest(BaseModel):
    message: str

    class Config:
        json_schema_extra = {"example": {"message": "안녕하세요!"}}


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


@router.post("/agent")
async def get_agent_response(
    request: AgentChatRequest,
):
    agent_controller = AgentController()

    try:
        agent_resp: GraphBaseState = await agent_controller.call_agent(
            message=request.message
        )

        return {
            "status": status.HTTP_200_OK,
            "data": {
                "answer": agent_resp["answer"],
                "next_node": agent_resp["next_node"],
                "confidence_score": agent_resp["confidence_score"],
                "reasoning": agent_resp["reasoning"]
            },
        }

    except Exception as e:
        logger.error(f"Error in agent response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
