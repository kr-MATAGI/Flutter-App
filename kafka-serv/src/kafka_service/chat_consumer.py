import os
import asyncio
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer
from kafka_service.utils.logger import get_logger

from kafka_service.base_consumer import BaseConsumer

##
load_dotenv()

logger = get_logger(__name__)


class ChatConsumer:
    def __init__(self, bootstrap_servers=["localhost:9092"], topic="test_chat"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.consumer = None

    async def start(self):
        """Consumer를 시작하고 초기화합니다."""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="chat_group",
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        logger.info(f"Consumer started. Listening to topic: {self.topic}")

    async def consume(self):
        """메시지를 비동기적으로 소비합니다."""
        try:
            async for msg in self.consumer:
                logger.info(
                    f"Received message: {msg.value.decode('utf-8')} "
                    f"from partition {msg.partition} at offset {msg.offset}"
                )
                # 메시지 처리 시뮬레이션을 위한 지연
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error consuming message: {str(e)}")

    async def stop(self):
        """Consumer를 정상적으로 종료합니다."""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Consumer stopped")


## MAIN
async def main():
    BROKER_HOST = os.getenv("KAFKA_BROKER_HOST")
    BROKER_PORT = os.getenv("KAFKA_BROKER_PORT")
    logger.info(f"BROKER_HOST: {BROKER_HOST}, BROKER_PORT: {BROKER_PORT}")

    # Create Consumer
    consumer = ChatConsumer(
        bootstrap_servers=[f"{BROKER_HOST}:{BROKER_PORT}"],
        topic="ai_chat",
    )

    try:
        await consumer.start()
        await consumer.consume()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
