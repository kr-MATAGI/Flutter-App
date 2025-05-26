from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict
from datetime import datetime
import json
import asyncio
from app.core.config import settings
from app.core.kafka_config import KafkaConfig, ChatMessage, send_message

router = APIRouter()


# 활성 연결을 관리하는 클래스
class ConnectionManager:
    def __init__(self):
        # room_id -> List[WebSocket]
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


# Kafka 메시지 소비자 태스크
async def kafka_message_consumer():
    consumer = await KafkaConfig.get_consumer()
    try:
        async for msg in consumer:
            message_data = msg.value
            room_id = message_data.get("room_id")
            if room_id:
                await manager.broadcast_to_room(json.dumps(message_data), room_id)
    finally:
        await consumer.stop()


# WebSocket 엔드포인트
@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    producer = await KafkaConfig.get_producer()
    try:
        await manager.connect(websocket, room_id)

        # Kafka 소비자 태스크 시작
        consumer_task = asyncio.create_task(kafka_message_consumer())

        while True:
            data = await websocket.receive_text()
            message = ChatMessage(
                user_id=user_id,
                message=data,
                room_id=room_id,
                timestamp=datetime.now().isoformat(),
            )

            # Kafka로 메시지 전송
            await send_message(producer, message)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await producer.stop()
    except Exception as e:
        print(f"Error in websocket endpoint: {e}")
        manager.disconnect(websocket, room_id)
        await producer.stop()
    finally:
        if "consumer_task" in locals():
            consumer_task.cancel()


# REST API 엔드포인트 (기존 코드는 유지)
@router.post("/send")
async def send_message_rest(message: str):
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
