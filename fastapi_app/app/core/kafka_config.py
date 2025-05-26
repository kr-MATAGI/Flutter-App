from typing import List
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
import asyncio
from app.core.config import settings


class KafkaConfig:
    KAFKA_BOOTSTRAP_SERVERS = settings.KAFKA_BOOTSTRAP_SERVERS
    CHAT_TOPIC = "chat_messages"
    GROUP_ID = "chat_consumer_group"

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        producer = AIOKafkaProducer(
            bootstrap_servers=cls.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()
        return producer

    @classmethod
    async def get_consumer(cls, topics: List[str] = None) -> AIOKafkaConsumer:
        if topics is None:
            topics = [cls.CHAT_TOPIC]

        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=cls.KAFKA_BOOTSTRAP_SERVERS,
            group_id=cls.GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await consumer.start()
        return consumer


class ChatMessage(BaseModel):
    user_id: str
    message: str
    room_id: str
    timestamp: str


async def send_message(producer: AIOKafkaProducer, message: ChatMessage):
    try:
        await producer.send_and_wait(KafkaConfig.CHAT_TOPIC, message.dict())
    except Exception as e:
        print(f"Error sending message to Kafka: {e}")
        raise
