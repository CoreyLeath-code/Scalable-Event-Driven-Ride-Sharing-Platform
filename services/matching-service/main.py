from datetime import UTC, datetime
from uuid import uuid4

from shared.config import settings
from shared.event_bus.kafka_consumer import create_consumer
from shared.event_bus.kafka_producer import publish_event
from shared.event_schema.ride_events import DriverAssignedEvent


def run():
    consumer = create_consumer(settings.KAFKA_TOPIC_RIDE_REQUESTED)

    for message in consumer:
        ride_data = message.value

        driver_assigned = DriverAssignedEvent(
            ride_id=ride_data["ride_id"], driver_id=uuid4(), assigned_at=datetime.now(UTC)
        )

        publish_event(settings.KAFKA_TOPIC_DRIVER_ASSIGNED, driver_assigned.dict())


if __name__ == "__main__":
    run()
