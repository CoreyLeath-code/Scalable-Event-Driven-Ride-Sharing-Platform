from kafka import KafkaProducer
import json
from shared.config import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def publish_event(topic: str, payload: dict):
    producer.send(topic, payload)
    producer.flush()
