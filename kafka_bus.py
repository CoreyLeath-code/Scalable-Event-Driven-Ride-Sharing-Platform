import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from event_bus import EventBus


class KafkaEventBus(EventBus):
    """Kafka implementation using aiokafka for async publish/subscribe."""

    def __init__(self, bootstrap_servers="localhost:9092", group_id="ride-sharing"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.producer = None

    async def connect(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        await self.producer.start()

    async def publish(self, topic: str, message: dict):
        if not self.producer:
            raise RuntimeError("Kafka producer not initialized. Call connect().")
        await self.producer.send_and_wait(topic, message)

    async def subscribe(self, topic: str, handler):
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )
        await consumer.start()
        try:
            async for message in consumer:
                await handler(message.value)
        finally:
            await consumer.stop()

    async def close(self):
        if self.producer:
            await self.producer.stop()
            self.producer = None
