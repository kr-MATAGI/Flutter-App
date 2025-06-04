import json
import asyncio
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    Query,
    Body,
)
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.kafka_config import KafkaConfig, ChatMessage, send_message
from app.routers.controller.agent_ctl import AgentController

router = APIRouter()


# 응답 모델 정의
class ChatResponse(BaseModel):
    message_id: str
    user_id: str
    message: str
    room_id: str
    timestamp: str
    status: str

    class Config:
        schema_extra = {
            "example": {
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user123",
                "message": "안녕하세요!",
                "room_id": "room456",
                "timestamp": "2024-03-20T12:00:00",
                "status": "delivered",
            }
        }


# 요청 모델 정의
class ChatMessageRequest(BaseModel):
    message: str
    room_id: str

    class Config:
        schema_extra = {"example": {"message": "안녕하세요!", "room_id": "room456"}}


# 활성 연결을 관리하는 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)


manager = ConnectionManager()


# WebSocket 엔드포인트
@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """
    WebSocket 연결을 통한 실시간 채팅

    Parameters:
    - room_id: 채팅방 ID
    - user_id: 사용자 ID
    """
    producer = await KafkaConfig.get_producer()
    try:
        await manager.connect(websocket, room_id)
        while True:
            data = await websocket.receive_text()
            message = ChatMessage(
                user_id=user_id,
                message=data,
                room_id=room_id,
                timestamp=datetime.now().isoformat(),
            )
            await send_message(producer, message)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await producer.stop()
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
        manager.disconnect(websocket, room_id)
        await producer.stop()


@router.post("/send", response_model=ChatResponse, status_code=201)
async def send_message_rest(
    message: ChatMessageRequest = Body(..., description="전송할 메시지 내용"),
    user_id: str = Query(..., description="사용자 ID"),
) -> ChatResponse:
    """
    채팅 메시지를 전송합니다.

    Parameters:
    - message: 전송할 메시지 내용과 채팅방 ID
    - user_id: 메시지를 보내는 사용자의 ID

    Returns:
    - ChatResponse: 전송된 메시지의 상세 정보

    Raises:
    - HTTPException(500): 메시지 전송 중 오류 발생
    """
    try:
        producer = await KafkaConfig.get_producer()
        chat_message = ChatMessage(
            user_id=user_id,
            message=message.message,
            room_id=message.room_id,
            timestamp=datetime.now().isoformat(),
        )
        await send_message(producer, chat_message)

        return ChatResponse(
            message_id=f"msg_{datetime.now().timestamp()}",
            user_id=user_id,
            message=message.message,
            room_id=message.room_id,
            timestamp=chat_message.timestamp,
            status="delivered",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{room_id}", response_model=List[ChatResponse])
async def get_chat_history(
    room_id: str = Query(..., description="채팅방 ID"),
    limit: Optional[int] = Query(50, description="조회할 메시지 수", ge=1, le=100),
) -> List[ChatResponse]:
    """
    특정 채팅방의 메시지 기록을 조회합니다.

    Parameters:
    - room_id: 채팅방 ID
    - limit: 조회할 최대 메시지 수 (기본값: 50, 최대: 100)

    Returns:
    - List[ChatResponse]: 채팅 메시지 목록

    Raises:
    - HTTPException(404): 채팅방을 찾을 수 없음
    """
    try:
        # TODO: 데이터베이스에서 채팅 기록 조회 구현
        return []
    except Exception as e:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
