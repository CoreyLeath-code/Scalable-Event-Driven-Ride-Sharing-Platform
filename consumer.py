from models import DriverLocationEvent
from utils import get_logger

logger = get_logger("DriverLocationConsumer")


class DriverLocationConsumer:
    """Validate driver telemetry updates and store accepted events."""

    def __init__(self, event_bus, store):
        self.event_bus = event_bus
        self.store = store
        self.logger = logger

    async def handle_driver_location(self, data: dict):
        """Convert a dictionary to the typed event model and update the store."""
        try:
            event = DriverLocationEvent(**data)
        except (TypeError, ValueError):
            self.logger.error("Invalid driver location event rejected")
            return

        self.store.upsert_driver(event)
        self.logger.info("Driver update processed: %s", event.driver_id)

    async def start(self):
        """Begin listening to the driver_location_updates topic."""
        self.logger.info("DriverLocationConsumer listening for driver updates...")
        await self.event_bus.subscribe("driver_location_updates", self.handle_driver_location)
