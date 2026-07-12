from datetime import UTC, datetime

from matching_engine import MatchingEngine
from models import DriverLocationEvent, TripRequestEvent


def test_matching_engine_ranks_nearest_driver_first():
    timestamp = datetime.now(UTC)
    trip = TripRequestEvent(
        rider_id="rider-42",
        pickup_lat=40.0,
        pickup_lon=-74.0,
        dropoff_lat=40.7,
        dropoff_lon=-73.9,
        timestamp=timestamp,
    )
    drivers = [
        DriverLocationEvent(
            driver_id="far",
            lat=41.0,
            lon=-74.0,
            timestamp=timestamp,
            status="available",
        ),
        DriverLocationEvent(
            driver_id="near",
            lat=40.01,
            lon=-74.0,
            timestamp=timestamp,
            status="available",
        ),
    ]

    ranked = MatchingEngine().rank_drivers(drivers, trip, surge_multiplier=1.0)

    assert [driver.driver_id for driver in ranked] == ["near", "far"]
