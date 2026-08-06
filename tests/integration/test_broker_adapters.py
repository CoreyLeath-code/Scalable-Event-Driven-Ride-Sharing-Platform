"""Round-trip integration tests against Docker-hosted broker implementations."""

import asyncio
import importlib.util
import sys
import types
import uuid
from contextlib import suppress
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE_ADAPTER = ROOT / "src" / "event-bus" / "base.py"


def load_adapter_module(module_name: str):
    """Load root adapters beneath a temporary package so their relative base import resolves."""
    package_name = f"_integration_adapter_{uuid.uuid4().hex}"
    package = types.ModuleType(package_name)
    package.__path__ = [str(ROOT)]
    sys.modules[package_name] = package

    base_spec = importlib.util.spec_from_file_location(f"{package_name}.base", BASE_ADAPTER)
    base_module = importlib.util.module_from_spec(base_spec)
    sys.modules[base_spec.name] = base_module
    base_spec.loader.exec_module(base_module)

    adapter_spec = importlib.util.spec_from_file_location(
        f"{package_name}.{module_name}", ROOT / f"{module_name}.py"
    )
    adapter_module = importlib.util.module_from_spec(adapter_spec)
    sys.modules[adapter_spec.name] = adapter_module
    adapter_spec.loader.exec_module(adapter_module)
    return adapter_module


async def stop_subscription(task: asyncio.Task) -> None:
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


@pytest.mark.integration
@pytest.mark.asyncio
async def test_kafka_adapter_round_trip():
    adapter = load_adapter_module("kafka_bus")
    topic = f"ride-location-{uuid.uuid4().hex}"
    payload = {"driver_id": "driver-1", "status": "available"}
    received = asyncio.Event()
    messages = []

    async def handler(message):
        messages.append(message)
        received.set()

    bus = adapter.KafkaEventBus(bootstrap_servers="localhost:9092", group_id=f"test-{uuid.uuid4()}")
    await bus.connect()
    subscription = asyncio.create_task(bus.subscribe(topic, handler))
    try:
        await asyncio.sleep(1)
        await bus.publish(topic, payload)
        await asyncio.wait_for(received.wait(), timeout=30)
        assert messages == [payload]
    finally:
        await stop_subscription(subscription)
        await bus.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_adapter_round_trip():
    adapter = load_adapter_module("redis_bus")
    topic = f"ride-location-{uuid.uuid4().hex}"
    payload = {"driver_id": "driver-2", "status": "en_route"}
    received = asyncio.Event()
    messages = []

    async def handler(message):
        messages.append(message)
        received.set()

    bus = adapter.RedisEventBus(redis_url="redis://localhost:6379/15")
    await bus.connect()
    subscription = asyncio.create_task(bus.subscribe(topic, handler))
    try:
        await asyncio.sleep(1)
        await bus.publish(topic, payload)
        await asyncio.wait_for(received.wait(), timeout=30)
        assert messages == [payload]
    finally:
        await stop_subscription(subscription)
        await bus.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rabbitmq_adapter_round_trip():
    adapter = load_adapter_module("rabbitmq_bus")
    topic = f"ride-location-{uuid.uuid4().hex}"
    payload = {"driver_id": "driver-3", "status": "on_trip"}
    received = asyncio.Event()
    messages = []

    async def handler(message):
        messages.append(message)
        received.set()

    bus = adapter.RabbitMQEventBus(url="amqp://guest:guest@localhost/")
    await bus.connect()
    subscription = asyncio.create_task(bus.subscribe(topic, handler))
    try:
        await asyncio.sleep(1)
        await bus.publish(topic, payload)
        await asyncio.wait_for(received.wait(), timeout=30)
        assert messages == [payload]
    finally:
        await stop_subscription(subscription)
        await bus.close()
