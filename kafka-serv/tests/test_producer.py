import time
from kafka import KafkaProducer
from kafka_service.utils.logger import get_logger

# Logger
logger = get_logger(__name__)


def create_producer():
    # Producer 설정
    return KafkaProducer(
        acks=1,  # 메시지 전송 완료 확인
        compression_type="gzip",
        bootstrap_servers=["localhost:9092"],
        value_serializer=lambda x: x.encode("utf-8"),
    )


def main():
    logger.info("[Start] Producer")
    producer = create_producer()
    start_time = time.time()

    try:
        # Send Messages
        for i in range(5):  # 테스트를 위해 메시지 수를 줄임
            message = f"Hello, Kafka! Message {i}"
            future = producer.send("ai_chat", value=message)
            # 메시지 전송 완료 대기
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent successfully: {message}")
            logger.info(f"Topic: {record_metadata.topic}")
            logger.info(f"Partition: {record_metadata.partition}")
            logger.info(f"Offset: {record_metadata.offset}")
            logger.info("-" * 50)
            time.sleep(1)  # 메시지 간 간격 추가

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        try:
            producer.flush()  # 남은 메시지 모두 전송
            producer.close()  # 프로듀서 종료
            logger.info(f"[End] Producer : {time.time() - start_time}")
        except Exception as e:
            logger.error(f"Error while closing producer: {str(e)}")


if __name__ == "__main__":
    main()
