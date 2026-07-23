import json

import aioredis

from .base import EventBus


class RedisEventBus(EventBus):
    """
    Redis Streams based implementation.
    Great for lightweight event-driven pipelines.
    """

    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def publish(self, topic: str, message: dict):
        await self.redis.xadd(topic, {"data": json.dumps(message)})

    async def subscribe(self, topic: str, handler):
        last_id = "$"
        while True:
            streams = await self.redis.xread({topic: last_id}, timeout=5000)
            if streams:
                _, messages = streams[0]
                for msg_id, fields in messages:
                    last_id = msg_id
                    data = json.loads(fields["data"])
                    await handler(data)

    async def close(self):
        if self.redis:
            await self.redis.close()
