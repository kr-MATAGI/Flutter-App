import json
import asyncio
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from app.core.config import settings
from app.models import KafkaMessage
from app.utils.logger import setup_logger


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""

    content: str = Field(..., description="메시지 내용")
    sender_id: str = Field(..., description="발신자 ID")
    receiver_id: str = Field(..., description="수신자 ID")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="메시지 전송 시간"
    )
    message_type: str = Field(
        default="text", description="메시지 타입 (text, ai, human 등)"
    )
    chat_room_id: Optional[str] = Field(None, description="채팅방 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "안녕하세요!",
                "sender_id": "user_123",
                "receiver_id": "user_456",
                "timestamp": "2024-02-28T12:00:00Z",
                "message_type": "text",
                "chat_room_id": "room_789",
            }
        }


class KafkaConfig:
    KAFKA_HOST = settings.KAFKA_HOST
    KAFKA_PORT = settings.KAFKA_PORT
    KAFKA_URL = settings.KAFKA_URL

    def __init__(self, chat_topic: str, group_id: str, logger_name: str):
        self.chat_topic = chat_topic
        self.group_id = group_id

        self.logger = setup_logger(logger_name)

        self._producer = None
        self._consumer = None

        self.logger.info(
            f"KafkaConfig initialized with chat_topic: {chat_topic}, group_id: {group_id}"
        )

    async def init_producer(self) -> AIOKafkaProducer:
        self.logger.info("[START] Initializing Kafka producer")

        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.KAFKA_URL,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._producer.start()

        self.logger.info("[END] Kafka producer initialized")

    async def init_consumer(self, topics: List[str] = None) -> AIOKafkaConsumer:
        if topics is None:
            self.logger.error("No topics provided")
            return

        self.logger.info("[START] Initializing Kafka consumer")

        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.KAFKA_URL,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await self.consumer.start()

        self.logger.info("[END] Kafka consumer initialized")

    async def send_message(self, message: KafkaMessage):
        try:
            await self._producer.send_and_wait(self.chat_topic, message.dict())
        except Exception as e:
            self.logger.error(f"Error sending message to Kafka: {e}")


async def send_message(kafka_config: KafkaConfig, message: KafkaMessage):
    """메시지를 Kafka로 전송하는 유틸리티 함수"""
    await kafka_config.send_message(message)
