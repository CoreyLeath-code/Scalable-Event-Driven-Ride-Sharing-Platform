import asyncio

from event_bus import EventBus


def test_event_bus_publish_and_subscribe():
    asyncio.run(_publish_and_subscribe())


async def _publish_and_subscribe():
    bus = EventBus()
    received_messages = []

    async def handler(payload):
        received_messages.append(payload)

    # Subscribe
    await bus.subscribe("test_topic", handler)

    # Publish event
    await bus.publish("test_topic", {"value": 123})

    # Allow async loop to process event
    await asyncio.sleep(0.1)

    assert len(received_messages) == 1
    assert received_messages[0]["value"] == 123


def test_event_bus_no_subscribers_is_safe():
    asyncio.run(_publish_without_subscribers())


async def _publish_without_subscribers():
    bus = EventBus()

    await bus.publish("missing_topic", {"value": "ignored"})

    assert "missing_topic" not in bus.subscribers
