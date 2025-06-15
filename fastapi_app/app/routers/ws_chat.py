import os
import json
import asyncio
from typing import List, Dict
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException

from app.core.kafka_config import KafkaConfig, ChatMessage, send_message
from app.utils.logger import setup_logger
from app.routers.controller.agent_ctl import AgentController

router = APIRouter()
logger = setup_logger("ws_chat")

# Kafka 설정
CHAT_TOPIC = "chat_messages"
KAFKA_GROUP_ID = "chat_group"


# 활성 연결을 관리하는 클래스
class ConnectionManager:
    def __init__(self):
        # room_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.logger = logger

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        self.logger.info(f"New connection in room {room_id}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
            self.logger.info(f"Connection closed in room {room_id}")

    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    self.logger.error(f"Error broadcasting message: {e}")


manager = ConnectionManager()


# WebSocket 엔드포인트
@router.websocket("/ws/chat/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    kafka_config = KafkaConfig(
        chat_topic=CHAT_TOPIC,
        group_id=KAFKA_GROUP_ID,
        logger_name=f"kafka_chat_{room_id}_{user_id}",
    )

    try:
        # Kafka 초기화
        await kafka_config.init_producer()
        await kafka_config.init_consumer([CHAT_TOPIC])

        # WebSocket 연결
        await manager.connect(websocket, room_id)
        logger.info(f"User {user_id} connected to room {room_id}")

        # Kafka 메시지 수신 태스크
        async def consume_messages():
            try:
                async for msg in kafka_config.consumer:
                    message_data = json.loads(msg.value.decode("utf-8"))
                    if message_data.get("chat_room_id") == room_id:
                        await websocket.send_text(json.dumps(message_data))
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")

        consumer_task = asyncio.create_task(consume_messages())

        # 클라이언트로부터 메시지 수신
        while True:
            data = await websocket.receive_text()
            message = ChatMessage(
                content=data,
                sender_id=user_id,
                receiver_id="all",  # 그룹 채팅의 경우
                chat_room_id=room_id,
                message_type="text",
            )

            # Kafka로 메시지 전송
            await kafka_config.send_message(message.dict())
            logger.info(f"Message sent to Kafka: {message.dict()}")

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from room {room_id}")
        manager.disconnect(websocket, room_id)
    except Exception as e:
        logger.error(f"Error in websocket endpoint: {e}")
        manager.disconnect(websocket, room_id)
    finally:
        if "consumer_task" in locals():
            consumer_task.cancel()
        await kafka_config.consumer.stop()
        await kafka_config._producer.stop()


# 테스트용 WebSocket 엔드포인트
@router.websocket("/ws/chat-test")
async def websocket_test_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Test WebSocket connected")
    try:
        while True:
            try:
                # 메시지 수신
                data = await websocket.receive()
                logger.info(f"Received data: {data}")

                # 메시지 타입에 따른 처리
                if data["type"] == "websocket.receive":
                    message = data.get("text") or data.get("bytes")
                    if not message:
                        continue

                    # bytes인 경우 디코딩
                    if isinstance(message, bytes):
                        message = message.decode("utf-8")

                    # JSON 형식인지 확인
                    try:
                        json_data = json.loads(message)
                        content = json_data.get("message", message)
                    except json.JSONDecodeError:
                        content = message

                    # LLM Response 생성
                    llm_resp = await free_ai_model.ainvoke(content)

                    # 응답 생성
                    response = {
                        "role": "assistant",
                        "content": {
                            "message": llm_resp,
                        },
                        "timestamp": datetime.now().isoformat(),
                        "type": "echo",
                    }

                    await websocket.send_text(json.dumps(response))
                    logger.info(f"Echo message sent: {content}")

            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {str(je)}")
                error_response = {
                    "content": "JSON 형식이 올바르지 않습니다.",
                    "error": str(je),
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                }
                await websocket.send_text(json.dumps(error_response))
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                error_response = {
                    "content": "메시지 처리 중 오류가 발생했습니다.",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                }
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        logger.info("Test WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        try:
            await websocket.close()
        except:
            pass
