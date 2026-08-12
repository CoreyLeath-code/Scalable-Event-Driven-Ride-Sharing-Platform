from datetime import datetime, timezone

from location_store import RedisDriverLocationStore
from models import DriverLocationEvent


class FakeRedis:
    def __init__(self):
        self.values = {}

    def hset(self, name, key, value):
        self.values.setdefault(name, {})[key] = value

    def hget(self, name, key):
        return self.values.get(name, {}).get(key)

    def hvals(self, name):
        return list(self.values.get(name, {}).values())

    def hlen(self, name):
        return len(self.values.get(name, {}))

    def hdel(self, name, key):
        self.values.get(name, {}).pop(key, None)

    def delete(self, name):
        self.values.pop(name, None)

    def ping(self):
        return True


def test_redis_driver_store_round_trip_and_readiness():
    store = RedisDriverLocationStore(client=FakeRedis())
    event = DriverLocationEvent(
        driver_id="d1",
        lat=40.7128,
        lon=-74.0060,
        timestamp=datetime.now(timezone.utc),
        status="available",
    )

    store.upsert_driver(event)

    assert store.is_ready()
    assert store.count() == 1
    assert store.get_driver("d1") == event
    assert store.get_all_drivers() == [event]

    store.remove_driver(event.driver_id)
    assert store.get_driver(event.driver_id) is None
