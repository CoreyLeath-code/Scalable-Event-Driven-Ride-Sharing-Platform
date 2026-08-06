from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

import api_router
from consumer import DriverLocationConsumer
from models import DriverLocationEvent


class RecordingStore:
    def __init__(self, drivers=None):
        self.drivers = {driver.driver_id: driver for driver in drivers or []}
        self.upserts = []

    def get_all_drivers(self):
        return list(self.drivers.values())

    def get_driver(self, driver_id):
        return self.drivers.get(driver_id)

    def count(self):
        return len(self.drivers)

    def upsert_driver(self, event):
        self.upserts.append(event)
        self.drivers[event.driver_id] = event


class RecordingBus:
    def __init__(self):
        self.subscriptions = []

    async def subscribe(self, topic, handler):
        self.subscriptions.append((topic, handler))


@pytest.fixture(autouse=True)
def reset_driver_store():
    api_router.DRIVER_STORE = None
    yield
    api_router.DRIVER_STORE = None


def driver_event(driver_id="driver-1"):
    return DriverLocationEvent(
        driver_id=driver_id,
        lat=40.7128,
        lon=-74.006,
        timestamp=datetime(2026, 8, 5, tzinfo=timezone.utc),
        status="available",
    )


@pytest.mark.asyncio
async def test_driver_endpoints_return_store_backed_results():
    driver = driver_event()
    api_router.DRIVER_STORE = RecordingStore([driver])

    all_drivers = await api_router.get_all_drivers()
    single_driver = await api_router.get_driver(driver.driver_id)
    count = await api_router.get_driver_count()

    assert all_drivers == {"count": 1, "drivers": [driver]}
    assert single_driver == driver
    assert count == {"active_drivers": 1}


@pytest.mark.asyncio
async def test_driver_endpoints_handle_empty_and_missing_driver():
    api_router.DRIVER_STORE = RecordingStore()

    assert await api_router.get_all_drivers() == {"count": 0, "drivers": []}
    assert await api_router.get_driver_count() == {"active_drivers": 0}

    with pytest.raises(HTTPException) as exc_info:
        await api_router.get_driver("unknown-driver")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Driver unknown-driver not found."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    [api_router.get_all_drivers, api_router.get_driver_count],
)
async def test_driver_collection_endpoints_reject_uninitialized_store(endpoint):
    with pytest.raises(HTTPException) as exc_info:
        await endpoint()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Driver store not initialized."


@pytest.mark.asyncio
async def test_get_driver_rejects_uninitialized_store():
    with pytest.raises(HTTPException) as exc_info:
        await api_router.get_driver("driver-1")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Driver store not initialized."


@pytest.mark.asyncio
async def test_consumer_stores_valid_driver_location_event():
    store = RecordingStore()
    consumer = DriverLocationConsumer(event_bus=RecordingBus(), store=store)

    await consumer.handle_driver_location(
        {
            "driver_id": "driver-1",
            "lat": 40.7128,
            "lon": -74.006,
            "timestamp": "2026-08-05T12:00:00Z",
            "status": "available",
        }
    )

    assert len(store.upserts) == 1
    assert store.upserts[0].driver_id == "driver-1"
    assert store.upserts[0].status == "available"


@pytest.mark.asyncio
async def test_consumer_discards_malformed_event_without_mutating_store():
    store = RecordingStore()
    consumer = DriverLocationConsumer(event_bus=RecordingBus(), store=store)

    await consumer.handle_driver_location(
        {
            "driver_id": "driver-1",
            "lat": "not-a-coordinate",
            "lon": -74.006,
            "status": "available",
        }
    )

    assert store.upserts == []
    assert store.count() == 0


@pytest.mark.asyncio
async def test_consumer_start_registers_expected_topic_and_propagates_bus_errors():
    bus = RecordingBus()
    consumer = DriverLocationConsumer(event_bus=bus, store=RecordingStore())

    await consumer.start()

    assert bus.subscriptions == [("driver_location_updates", consumer.handle_driver_location)]

    class FailingBus:
        async def subscribe(self, _topic, _handler):
            raise RuntimeError("broker unavailable")

    with pytest.raises(RuntimeError, match="broker unavailable"):
        await DriverLocationConsumer(event_bus=FailingBus(), store=RecordingStore()).start()
