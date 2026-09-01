import pytest

from consumer import DriverLocationConsumer


class RecordingStore:
    def __init__(self):
        self.events = []

    def upsert_driver(self, event):
        self.events.append(event)


class RecordingLogger:
    def __init__(self):
        self.entries = []

    def info(self, message, *args):
        self.entries.append(("info", message, args))

    def error(self, message, *args):
        self.entries.append(("error", message, args))


@pytest.mark.asyncio
async def test_consumer_logs_do_not_include_coordinates():
    logger = RecordingLogger()
    consumer = DriverLocationConsumer(event_bus=None, store=RecordingStore())
    consumer.logger = logger

    await consumer.handle_driver_location(
        {
            "driver_id": "driver-1",
            "lat": 40.7128,
            "lon": -74.006,
            "timestamp": "2026-08-05T12:00:00Z",
            "status": "available",
        }
    )

    rendered = repr(logger.entries)
    assert "40.7128" not in rendered
    assert "-74.006" not in rendered
    assert "driver-1" in rendered


@pytest.mark.asyncio
async def test_invalid_consumer_log_does_not_echo_input_values():
    logger = RecordingLogger()
    consumer = DriverLocationConsumer(event_bus=None, store=RecordingStore())
    consumer.logger = logger

    await consumer.handle_driver_location(
        {
            "driver_id": "sensitive@example.com",
            "lat": "invalid-coordinate",
            "lon": -74.006,
            "status": "available",
        }
    )

    rendered = repr(logger.entries)
    assert "sensitive@example.com" not in rendered
    assert "invalid-coordinate" not in rendered
