from kafka_service.base_consumer import BaseConsumer
from kafka_service.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("[Start] Consumer")
    consumer = BaseConsumer(
        topic="test_chat",
        group_id="test_group",
        logger_name="test_consumer",
    )
    consumer.create_consumer(
        bootstrap_servers=["localhost:9092"],
        offset="earliest",
        auto_commit=True,
    )
    consumer.subscribe(["ai_chat"])

    for message in consumer.get_messages():
        logger.info(f"Message: {message}")


if __name__ == "__main__":
    main()
