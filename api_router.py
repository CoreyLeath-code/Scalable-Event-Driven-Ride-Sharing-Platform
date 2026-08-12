from fastapi import APIRouter, HTTPException

from utils import get_logger

logger = get_logger("DriverLocationAPI")
router = APIRouter()

# These will be set by main.py
DRIVER_STORE = None


@router.get("/drivers")
async def get_all_drivers():
    """
    Returns all active drivers and their current coordinates.
    """
    if DRIVER_STORE is None:
        raise HTTPException(500, "Driver store not initialized.")

    drivers = DRIVER_STORE.get_all_drivers()
    return {"count": len(drivers), "drivers": drivers}


@router.get("/drivers/{driver_id}")
async def get_driver(driver_id: str):
    """
    Returns location data for a specific driver.
    """
    if DRIVER_STORE is None:
        raise HTTPException(500, "Driver store not initialized.")

    driver = DRIVER_STORE.get_driver(driver_id)
    if not driver:
        raise HTTPException(404, f"Driver {driver_id} not found.")

    return driver


@router.get("/count")
async def get_driver_count():
    """
    Quick counter to see how many drivers are active.
    """
    if DRIVER_STORE is None:
        raise HTTPException(500, "Driver store not initialized.")

    return {"active_drivers": DRIVER_STORE.count()}


@router.get("/health")
async def health_check():
    """Liveness probe: the API process can serve requests."""
    return {"status": "OK", "service": "driver-location-service"}


@router.get("/ready")
async def readiness_check():
    """Readiness probe: the configured driver-location store is reachable."""
    if DRIVER_STORE is None:
        raise HTTPException(503, "Driver store not initialized.")

    try:
        ready = DRIVER_STORE.is_ready()
    except Exception as exc:
        logger.error("Driver store readiness check failed: %s", exc)
        raise HTTPException(503, "Driver store is unavailable.") from exc

    if not ready:
        raise HTTPException(503, "Driver store is unavailable.")
    return {"status": "OK", "service": "driver-location-service"}
