from fastapi import APIRouter, status, HTTPException

from app.core.config import settings
from app.models.chat_base import ChatMessage, ChatResponse

from langchain_openai import ChatOpenAI

router = APIRouter()


@router.post("/single/chat")
async def send_single_chat(message: ChatMessage):
    """
    단일 채팅 메시지를 전송하고 AI의 응답을 받습니다.
    """
    try:
        # OpenAI - ChatGPT 연결
        _llm = ChatOpenAI(
            model=settings.AI_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
        )

        # 채팅 메시지 전송
        _response = _llm.invoke(message.message)

        # 채팅 메시지 응답
        _chat_response = ChatResponse(
            status="success",
            message_id="test",
            user_id=message.user_id,
            message=_response.content,
            room_id=message.room_id,
            timestamp=message.timestamp,
        )
        # 채팅 메시지 전송
        return {"status": status.HTTP_200_OK, "response": _chat_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
