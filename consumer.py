from typing import Dict

from models import DriverLocationEvent
from utils import get_logger

logger = get_logger("DriverLocationConsumer")


class DriverLocationConsumer:
    """
    Listens for incoming driver telemetry updates and stores them in
    DriverLocationStore.

    Expected event format:
    {
        "driver_id": "d123",
        "lat": 40.712,
        "lon": -74.005,
        "timestamp": "...",
        "status": "available"
    }
    """

    def __init__(self, event_bus, store):
        self.event_bus = event_bus
        self.store = store
        self.logger = logger

    # ------------------------------------------------------------
    # Handle Incoming Driver Location Updates
    # ------------------------------------------------------------

    async def handle_driver_location(self, data: Dict):
        """
        Convert dictionary → Pydantic model → update store.
        """

        try:
            event = DriverLocationEvent(**data)
        except Exception as e:
            self.logger.error(f"Invalid driver location event: {e}")
            return

        # Update the driver store
        self.store.upsert_driver(event)

        self.logger.info(f"Driver update processed: {event.driver_id} @ ({event.lat}, {event.lon})")

    # ------------------------------------------------------------
    # Subscribe to EventBus Topic
    # ------------------------------------------------------------

    async def start(self):
        """
        Begins listening to driver_location_updates topic.
        """
        self.logger.info("DriverLocationConsumer listening for driver updates...")
        await self.event_bus.subscribe("driver_location_updates", self.handle_driver_location)
