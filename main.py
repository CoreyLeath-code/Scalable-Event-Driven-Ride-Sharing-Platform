from fastapi import FastAPI

import api_router
from api_router import router
from consumer import DriverLocationConsumer
from event_bus import EventBus
from location_store import DriverLocationStore
from utils import get_logger

# ------------------------------------------------------------
# INITIALIZATION
# ------------------------------------------------------------

logger = get_logger("DriverLocationMain")

event_bus = EventBus()
driver_store = DriverLocationStore()

app = FastAPI(
    title="Driver Location Service",
    description="Real-time driver location ingestion service for the ride-sharing platform.",
    version="1.0.0",
)


# ------------------------------------------------------------
# STARTUP SEQUENCE
# ------------------------------------------------------------


@app.on_event("startup")
async def startup_event():

    logger.info("Starting Driver Location Service...")

    # Inject store into API router
    api_router.DRIVER_STORE = driver_store

    # Initialize consumer
    consumer = DriverLocationConsumer(event_bus=event_bus, store=driver_store)

    # Subscribe to driver location update events
    await event_bus.subscribe("driver_location_updates", consumer.handle_driver_location)

    logger.info("Driver Location Service started successfully.")


# ------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------

app.include_router(router, prefix="/driver-location")


# ------------------------------------------------------------
# LOCAL RUNNER
# ------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
    )
