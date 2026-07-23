from models import DriverLocationEvent
from utils import get_logger

logger = get_logger("DriverLocationStore")


class DriverLocationStore:
    """
    In-memory real-time driver store.

    Responsibilities:
    - Maintain driver availability
    - Update driver coordinates
    - Remove offline drivers
    - Provide list of active drivers for Dispatch Service

    This version is intentionally simple, but the interface allows
    easy migration to Redis, MongoDB, or a geospatial index (H3).
    """

    def __init__(self):
        # driver_id → DriverLocationEvent
        self.drivers: dict[str, DriverLocationEvent] = {}

    # ------------------------------------------------------------
    # Core Operations
    # ------------------------------------------------------------

    def upsert_driver(self, event: DriverLocationEvent) -> None:
        """
        Add or update driver in the store.
        """
        self.drivers[event.driver_id] = event
        logger.info(f"Updated driver {event.driver_id} at ({event.lat}, {event.lon})")

    def remove_driver(self, driver_id: str) -> None:
        """
        Remove a driver from the store.
        """
        if driver_id in self.drivers:
            del self.drivers[driver_id]
            logger.info(f"Removed driver {driver_id}")

    # ------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------

    def get_all_drivers(self) -> list[DriverLocationEvent]:
        """
        Return a list of all active drivers.
        """
        return list(self.drivers.values())

    def get_driver(self, driver_id: str) -> DriverLocationEvent | None:
        """
        Fetch a single driver by ID.
        """
        return self.drivers.get(driver_id)

    # ------------------------------------------------------------
    # Debug Utilities
    # ------------------------------------------------------------

    def count(self) -> int:
        """
        Count active drivers.
        """
        return len(self.drivers)

    def clear(self) -> None:
        """
        Remove all drivers (reset state).
        """
        self.drivers.clear()
        logger.warning("Cleared all driver locations.")
