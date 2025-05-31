import json
import asyncio

from typing import List
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from app.core.config import settings
from app.models import KafkaMessage
from app.utils.logger import setup_logger


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
