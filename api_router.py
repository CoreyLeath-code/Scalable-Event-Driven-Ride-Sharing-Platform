from fastapi import APIRouter, Depends, HTTPException

from auth import require_authenticated_request
from utils import get_logger

logger = get_logger("DriverLocationAPI")
router = APIRouter()

# These will be set by main.py
DRIVER_STORE = None


@router.get("/drivers", dependencies=[Depends(require_authenticated_request)])
async def get_all_drivers():
    """Return active drivers and current coordinates to authenticated callers."""
    if DRIVER_STORE is None:
        raise HTTPException(500, "Driver store not initialized.")

    drivers = DRIVER_STORE.get_all_drivers()
    return {"count": len(drivers), "drivers": drivers}


@router.get("/drivers/{driver_id}", dependencies=[Depends(require_authenticated_request)])
async def get_driver(driver_id: str):
    """Return location data for a specific driver to an authenticated caller."""
    if DRIVER_STORE is None:
        raise HTTPException(500, "Driver store not initialized.")

    driver = DRIVER_STORE.get_driver(driver_id)
    if not driver:
        raise HTTPException(404, f"Driver {driver_id} not found.")

    return driver


@router.get("/count", dependencies=[Depends(require_authenticated_request)])
async def get_driver_count():
    """Return the number of active drivers to an authenticated caller."""
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
        logger.error("Driver store readiness check failed")
        raise HTTPException(503, "Driver store is unavailable.") from exc

    if not ready:
        raise HTTPException(503, "Driver store is unavailable.")
    return {"status": "OK", "service": "driver-location-service"}
