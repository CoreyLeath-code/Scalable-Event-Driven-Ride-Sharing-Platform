import os
import secrets
import socket

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import api_router
from api_router import router
from consumer import DriverLocationConsumer
from event_bus import EventBus
from location_store import create_driver_store
from utils import get_logger

# ------------------------------------------------------------
# INITIALIZATION
# ------------------------------------------------------------

logger = get_logger("DriverLocationMain")

event_bus = EventBus()
driver_store = create_driver_store(os.getenv("DRIVER_LOCATION_REDIS_URL"))

app = FastAPI(
    title="Driver Location Service",
    description="Real-time driver location ingestion service for the ride-sharing platform.",
    version="1.0.0",
)


@app.middleware("http")
async def require_driver_location_api_key(request: Request, call_next):
    """Fail closed for sensitive driver-location reads without a configured API key."""
    path = request.url.path
    protected = path == "/driver-location/count" or path.startswith("/driver-location/drivers")
    if protected:
        expected = os.getenv("DRIVER_LOCATION_API_KEY", "")
        if not expected:
            return JSONResponse(status_code=503, content={"detail": "API authorization unavailable"})
        supplied = request.headers.get("X-Driver-API-Key", "")
        if not secrets.compare_digest(supplied, expected):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)


@app.middleware("http")
async def optional_instance_id_header(request: Request, call_next):
    """Expose a container identity only when Compose smoke tests request it."""
    response = await call_next(request)
    if os.getenv("EXPOSE_INSTANCE_ID") == "true":
        response.headers["X-Instance-ID"] = os.getenv("INSTANCE_ID", socket.gethostname())
    return response


# ------------------------------------------------------------
# STARTUP SEQUENCE
# ------------------------------------------------------------


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Driver Location Service...")
    api_router.DRIVER_STORE = driver_store
    consumer = DriverLocationConsumer(event_bus=event_bus, store=driver_store)
    await event_bus.subscribe("driver_location_updates", consumer.handle_driver_location)
    logger.info("Driver Location Service started successfully.")


app.include_router(router, prefix="/driver-location")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
    )
