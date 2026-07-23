import asyncio
import random

from src.common.utils import get_logger, now_timestamp


class DispatchProducer:
    """
    Produces simulated TripRequest events and publishes them to the event bus.
    Used for:
    - Load testing
    - Demo scenarios
    - End-to-end pipeline validation
    """

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.logger = get_logger("DispatchProducer")

    # ------------------------------------------------------------
    # Generate Random Trip Requests
    # ------------------------------------------------------------

    async def generate_trip_requests(self):
        """
        Simulates realistic rider pickup/dropoff coordinates.
        Coordinates centered loosely around NYC grid for demo.
        """

        while True:
            event = {
                "rider_id": f"rider_{random.randint(1000,9999)}",
                "pickup_lat": round(40.70 + random.random() * 0.06, 6),
                "pickup_lon": round(-74.01 + random.random() * 0.06, 6),
                "dropoff_lat": round(40.70 + random.random() * 0.06, 6),
                "dropoff_lon": round(-74.01 + random.random() * 0.06, 6),
                "timestamp": now_timestamp(),
            }

            await self.event_bus.publish("trip_requests", event)

            self.logger.info(f"[PRODUCER] Published TripRequestEvent: {event}")

            # Frequency of trip events
            await asyncio.sleep(1)

    # ------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------

    async def start(self):
        """
        Launches continuous trip request simulation.
        """
        self.logger.info("DispatchProducer started...")
        await self.generate_trip_requests()
