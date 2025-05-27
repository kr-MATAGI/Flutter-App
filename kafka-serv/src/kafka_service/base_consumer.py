from kafka import KafkaConsumer, TopicPartition
from kafka_service.utils.logger import get_logger
import json

# Logger
logger = get_logger(__name__)


class BaseConsumer:
    def __init__(self, topic: str, group_id: str, logger_name: str):
        self.topic = topic
        self.group_id = group_id

        self.logger = get_logger(logger_name)

        self._consumer = None

        self.logger.info(
            f"Consumer initialized for topic: {self.topic}, group_id: {self.group_id}"
        )

    def create_consumer(
        self,
        bootstrap_servers: list[str],
        offset: str = "earliest",
        auto_commit: bool = True,
    ):
        self._consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset=offset,
            enable_auto_commit=auto_commit,
            group_id=self.group_id,
            value_deserializer=lambda x: x.decode("utf-8"),
        )

    def release_consumer(self):
        if self._consumer:
            try:
                self._consumer.close()
            except Exception as e:
                self.logger.error(f"Error while closing consumer: {str(e)}")
            finally:
                self._consumer = None

    def subscribe(self, topics: list[str]):
        self._consumer.subscribe(topics)
        partition = self.get_partitions()

        if partition:
            self.logger.info(f"Partitions for topic {self.topic}: {partition}")
        else:
            self.logger.warning(f"No partitions found for topic {self.topic}")

    def get_messages(self):
        try:
            for message in self._consumer:
                yield message
        except Exception as e:
            self.logger.error(f"Error occurred: {str(e)}")
            raise e
        finally:
            self.release_consumer()

    def get_partitions(self):
        return self._consumer.partitions_for_topic(self.topic)
