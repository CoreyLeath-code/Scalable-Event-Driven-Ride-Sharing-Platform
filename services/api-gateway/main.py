from fastapi import FastAPI
from uuid import uuid4
from datetime import datetime
from shared.event_schema.ride_events import RideRequestedEvent
from shared.event_bus.kafka_producer import publish_event
from shared.config import settings
from shared.logging_config import setup_logging

app = FastAPI()
logger = setup_logging()


@app.post("/request-ride")
def request_ride(
    rider_id: str,
    pickup_lat: float,
    pickup_lng: float,
    destination_lat: float,
    destination_lng: float,
):

    ride_event = RideRequestedEvent(
        ride_id=uuid4(),
        rider_id=rider_id,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
        timestamp=datetime.utcnow(),
    )

    publish_event(settings.KAFKA_TOPIC_RIDE_REQUESTED, ride_event.dict())
    logger.info("Ride requested", extra={"ride_id": str(ride_event.ride_id)})

    return {"status": "Ride request submitted"}
