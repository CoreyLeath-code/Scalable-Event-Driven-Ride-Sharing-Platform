import json

import redis.asyncio as redis

from event_bus import EventBus


class RedisEventBus(EventBus):
    """Redis Streams event-bus implementation."""

    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)

    def _client(self):
        if self.redis is None:
            raise RuntimeError("Redis client not initialized. Call connect().")
        return self.redis

    async def publish(self, topic: str, message: dict):
        await self._client().xadd(topic, {"data": json.dumps(message)})

    async def subscribe(self, topic: str, handler):
        client = self._client()
        last_id = "$"
        while True:
            streams = await client.xread({topic: last_id}, block=5000)
            if streams:
                _, messages = streams[0]
                for message_id, fields in messages:
                    last_id = message_id
                    data = json.loads(fields["data"])
                    await handler(data)

    async def close(self):
        if self.redis:
            await self.redis.aclose()
            self.redis = None
