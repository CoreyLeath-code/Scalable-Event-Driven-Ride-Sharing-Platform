import json
import aio_pika
from .base import EventBus


class RabbitMQEventBus(EventBus):
    """
    RabbitMQ implementation using aio-pika.
    Queue-based, good for job/task style processing.
    """

    def __init__(self, url="amqp://guest:guest@localhost/"):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()

    async def publish(self, topic: str, message: dict):
        queue = await self.channel.declare_queue(topic, durable=True)
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()), routing_key=queue.name
        )

    async def subscribe(self, topic: str, handler):
        queue = await self.channel.declare_queue(topic, durable=True)

        async with queue.iterator() as queue_iter:
            async for msg in queue_iter:
                async with msg.process():
                    await handler(json.loads(msg.body.decode()))

    async def close(self):
        if self.connection:
            await self.connection.close()
