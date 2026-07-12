import argparse
import asyncio
import json
import logging
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from event_bus import EventBus
from location_store import DriverLocationStore
from matching_engine import MatchingEngine
from models import DriverLocationEvent, TripRequestEvent
from pricing_engine import PricingEngine

logging.disable(logging.CRITICAL)


def _time_ms(samples):
    return round(statistics.mean(samples) * 1000, 6)


def _driver(index, timestamp):
    return DriverLocationEvent(
        driver_id=f"driver-{index}",
        lat=40.0 + (index * 0.0001),
        lon=-74.0,
        timestamp=timestamp,
        status="available",
    )


async def benchmark_event_bus(iterations):
    bus = EventBus()
    received = 0

    async def handler(_payload):
        nonlocal received
        received += 1

    await bus.subscribe("ride.requested", handler)
    samples = []
    for index in range(iterations):
        start = time.perf_counter()
        await bus.publish("ride.requested", {"ride_id": index})
        samples.append(time.perf_counter() - start)

    return {
        "iterations": iterations,
        "avg_publish_ms": _time_ms(samples),
        "messages_delivered": received,
    }


def benchmark_matching(iterations, driver_count):
    timestamp = datetime.now(UTC)
    engine = MatchingEngine(max_candidates=25)
    drivers = [_driver(index, timestamp) for index in range(driver_count)]
    trip = TripRequestEvent(
        rider_id="rider-1",
        pickup_lat=40.001,
        pickup_lon=-74.0,
        dropoff_lat=40.7,
        dropoff_lon=-73.9,
        timestamp=timestamp,
    )

    samples = []
    selected_driver = None
    for _ in range(iterations):
        start = time.perf_counter()
        selected = engine.select_best_match(drivers, trip, surge_multiplier=1.0)
        samples.append(time.perf_counter() - start)
        selected_driver = selected.driver_id if selected else None

    return {
        "iterations": iterations,
        "candidate_drivers": driver_count,
        "avg_match_ms": _time_ms(samples),
        "selected_driver": selected_driver,
    }


def benchmark_location_store(iterations):
    timestamp = datetime.now(UTC)
    store = DriverLocationStore()
    samples = []

    for index in range(iterations):
        start = time.perf_counter()
        store.upsert_driver(_driver(index, timestamp))
        samples.append(time.perf_counter() - start)

    return {
        "iterations": iterations,
        "avg_upsert_ms": _time_ms(samples),
        "stored_drivers": store.count(),
    }


def benchmark_pricing(iterations):
    engine = PricingEngine()
    samples = []
    multiplier = None

    for index in range(iterations):
        start = time.perf_counter()
        event = engine.compute_surge(demand=50 + index % 10, supply=20, zone_id="Z01")
        samples.append(time.perf_counter() - start)
        multiplier = event.surge_multiplier

    return {
        "iterations": iterations,
        "avg_compute_ms": _time_ms(samples),
        "last_surge_multiplier": multiplier,
    }


async def run(iterations, driver_count):
    return {
        "benchmark_version": 1,
        "runtime": "python",
        "iterations": iterations,
        "event_bus": await benchmark_event_bus(iterations),
        "matching": benchmark_matching(iterations, driver_count),
        "location_store": benchmark_location_store(iterations),
        "pricing": benchmark_pricing(iterations),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--driver-count", type=int, default=100)
    parser.add_argument("--output", default="benchmark-results.json")
    args = parser.parse_args()

    results = asyncio.run(run(args.iterations, args.driver_count))
    output = Path(args.output)
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
