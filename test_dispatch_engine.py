from datetime import UTC, datetime

from matching_engine import MatchingEngine
from models import DriverLocationEvent, TripRequestEvent


def test_dispatch_engine_selects_closest_driver():
    engine = MatchingEngine()
    timestamp = datetime.now(UTC)

    drivers = [
        DriverLocationEvent(
            driver_id="A", lat=40.0, lon=-74.0, timestamp=timestamp, status="available"
        ),
        DriverLocationEvent(
            driver_id="B", lat=40.1, lon=-74.0, timestamp=timestamp, status="available"
        ),
        DriverLocationEvent(
            driver_id="C", lat=41.0, lon=-74.0, timestamp=timestamp, status="available"
        ),
    ]

    rider = TripRequestEvent(
        rider_id="rider-1",
        pickup_lat=40.05,
        pickup_lon=-74.0,
        dropoff_lat=40.8,
        dropoff_lon=-73.9,
        timestamp=timestamp,
    )

    selected = engine.select_best_match(drivers, rider, surge_multiplier=1.0)

    assert selected is not None
    assert selected.driver_id in {"A", "B"}
    # Both A and B are close; acceptable tie
