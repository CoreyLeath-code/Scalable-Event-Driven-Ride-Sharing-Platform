import asyncio
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from utils import get_logger

logger = get_logger("EventBus")


class EventBus:
    """Simple in-memory asynchronous publish/subscribe event bus."""

    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def publish(self, topic: str, message: Any):
        """Publish an event without logging the payload contents."""
        if topic not in self.subscribers:
            logger.warning("[EVENT BUS] No subscribers for topic '%s'.", topic)
            return

        logger.info("[EVENT BUS] Publishing event to topic '%s'.", topic)
        callbacks = list(self.subscribers[topic])
        await asyncio.gather(*(callback(message) for callback in callbacks))

    async def subscribe(self, topic: str, callback: Callable):
        """Register a subscriber callback for a topic."""
        async with self.lock:
            self.subscribers[topic].append(callback)
            logger.info("[EVENT BUS] Subscriber added for topic '%s'.", topic)
