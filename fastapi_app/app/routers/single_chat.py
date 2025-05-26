from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.chat_base import ChatRequest, ChatResponse, DB_ChatLog
from langchain_openai import ChatOpenAI

router = APIRouter()


@router.post("/chat")
async def send_single_chat(message: ChatRequest, db: Session = Depends(get_db)):
    """
    단일 채팅 메시지를 전송하고 AI의 응답을 받은 후 데이터베이스에 저장합니다.
    """
    try:
        # OpenAI - ChatGPT 연결
        _llm = ChatOpenAI(
            model=settings.AI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
        )

        # 채팅 메시지 전송
        _llm_response = _llm.invoke(message.message)
        response = ChatResponse(
            status="success",
            user_id=message.user_id,
            message=_llm_response.content,
            room_id=message.room_id,
        )

        # 데이터베이스에 저장
        db_contents = DB_ChatLog(
            user_idx=int(message.user_id),
            room_id=int(message.room_id),
            message=message.message,
            response_chat=_llm_response.content,
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
        db.rollback()  # 오류 발생 시 트랜잭션 롤백
        raise HTTPException(status_code=500, detail=str(e))
