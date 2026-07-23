import asyncio
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from utils import get_logger

logger = get_logger("EventBus")


class EventBus:
    """
    A simple in-memory asynchronous event bus that provides:
    - publish(topic, message)
    - subscribe(topic, callback)

    In production this can be replaced with Kafka, Redis Streams,
    NATS, RabbitMQ, AWS SNS/SQS, GCP PubSub, etc.
    """

    def __init__(self):
        # topic → list of subscriber callback functions
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        # lock to avoid race conditions when adding/removing subscribers
        self.lock = asyncio.Lock()

    async def publish(self, topic: str, message: Any):
        """
        Publish an event to a topic.
        Invokes all subscribers concurrently.
        """
        if topic not in self.subscribers:
            logger.warning(f"[EVENT BUS] No subscribers for topic '{topic}'.")
            return

        logger.info(f"[EVENT BUS] Publishing to {topic}: {message}")

        callbacks = list(self.subscribers[topic])

        # Run all subscribers concurrently
        await asyncio.gather(*(callback(message) for callback in callbacks))

    async def subscribe(self, topic: str, callback: Callable):
        """
        Register a subscriber callback for a topic.
        """
        async with self.lock:
            self.subscribers[topic].append(callback)
            logger.info(f"[EVENT BUS] Subscriber added for topic '{topic}'.")
