import redis

from models import DriverLocationEvent
from utils import get_logger

logger = get_logger("DriverLocationStore")


class DriverLocationStore:
    """In-memory driver store for single-process local development."""

    def __init__(self):
        self.drivers: dict[str, DriverLocationEvent] = {}

    def upsert_driver(self, event: DriverLocationEvent) -> None:
        self.drivers[event.driver_id] = event
        logger.info(f"Updated driver {event.driver_id} at ({event.lat}, {event.lon})")

    def remove_driver(self, driver_id: str) -> None:
        if driver_id in self.drivers:
            del self.drivers[driver_id]
            logger.info(f"Removed driver {driver_id}")

    def get_all_drivers(self) -> list[DriverLocationEvent]:
        return list(self.drivers.values())

    def get_driver(self, driver_id: str) -> DriverLocationEvent | None:
        return self.drivers.get(driver_id)

    def count(self) -> int:
        return len(self.drivers)

    def clear(self) -> None:
        self.drivers.clear()
        logger.warning("Cleared all driver locations.")

    def is_ready(self) -> bool:
        return True


class RedisDriverLocationStore:
    """Redis-backed driver store for horizontally scaled API replicas."""

    redis_key = "driver-locations"

    def __init__(self, redis_url: str | None = None, client=None):
        if client is not None:
            self.client = client
        elif redis_url is not None:
            self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        else:
            raise ValueError("redis_url is required when no Redis client is provided")

    def upsert_driver(self, event: DriverLocationEvent) -> None:
        self.client.hset(self.redis_key, event.driver_id, event.model_dump_json())
        logger.info(f"Updated driver {event.driver_id} in Redis")

    def remove_driver(self, driver_id: str) -> None:
        self.client.hdel(self.redis_key, driver_id)

    def get_all_drivers(self) -> list[DriverLocationEvent]:
        return [
            DriverLocationEvent.model_validate_json(serialized)
            for serialized in self.client.hvals(self.redis_key)
        ]

    def get_driver(self, driver_id: str) -> DriverLocationEvent | None:
        serialized = self.client.hget(self.redis_key, driver_id)
        if serialized is None:
            return None
        return DriverLocationEvent.model_validate_json(serialized)

    def count(self) -> int:
        return self.client.hlen(self.redis_key)

    def clear(self) -> None:
        self.client.delete(self.redis_key)

    def is_ready(self) -> bool:
        return bool(self.client.ping())


def create_driver_store(redis_url: str | None = None):
    """Return a shared Redis store only when an explicit endpoint is configured."""
    if redis_url:
        return RedisDriverLocationStore(redis_url)
    return DriverLocationStore()
