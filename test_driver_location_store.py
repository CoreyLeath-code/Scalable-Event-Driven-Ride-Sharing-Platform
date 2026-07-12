from datetime import datetime, timezone

from location_store import DriverLocationStore
from models import DriverLocationEvent


def test_driver_location_store_updates_and_retrieves():
    store = DriverLocationStore()

    event = DriverLocationEvent(
        driver_id="d1",
        lat=40.7128,
        lon=-74.0060,
        timestamp=datetime.now(timezone.utc),
        status="available",
    )

    store.upsert_driver(event)
    result = store.get_driver("d1")

    assert store.count() == 1
    assert result == event


def test_driver_location_store_removes_and_clears():
    store = DriverLocationStore()
    event = DriverLocationEvent(
        driver_id="d1",
        lat=40.7128,
        lon=-74.0060,
        timestamp=datetime.now(timezone.utc),
        status="available",
    )

    store.upsert_driver(event)
    store.remove_driver("d1")
    assert store.get_driver("d1") is None

    store.upsert_driver(event)
    store.clear()
    assert store.count() == 0
