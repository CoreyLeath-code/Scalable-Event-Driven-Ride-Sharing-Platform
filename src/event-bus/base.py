from abc import ABC, abstractmethod


class EventBus(ABC):
    """
    Base interface for all event bus backends.
    Kafka, Redis Streams, and RabbitMQ will all inherit from this.
    """

    @abstractmethod
    async def publish(self, topic: str, message: dict):
        """Publish a message to a topic/stream/queue."""
        pass

    @abstractmethod
    async def subscribe(self, topic: str, handler):
        """
        Subscribe to a topic/stream/queue, calling `handler(message)`
        whenever a new event arrives.
        """
        pass

    @abstractmethod
    async def connect(self):
        """Connect to the backend service."""
        pass

    @abstractmethod
    async def close(self):
        """Gracefully close connections."""
        pass
