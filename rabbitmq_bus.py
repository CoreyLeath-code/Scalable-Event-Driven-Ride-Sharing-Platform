import json

import aio_pika

from event_bus import EventBus


class RabbitMQEventBus(EventBus):
    """RabbitMQ event-bus implementation using aio-pika."""

    def __init__(self, url="amqp://guest:guest@localhost/"):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()

    def _channel(self):
        if self.channel is None:
            raise RuntimeError("RabbitMQ channel not initialized. Call connect().")
        return self.channel

    async def publish(self, topic: str, message: dict):
        channel = self._channel()
        queue = await channel.declare_queue(topic, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()), routing_key=queue.name
        )

    async def subscribe(self, topic: str, handler):
        channel = self._channel()
        queue = await channel.declare_queue(topic, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await handler(json.loads(message.body.decode()))

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
