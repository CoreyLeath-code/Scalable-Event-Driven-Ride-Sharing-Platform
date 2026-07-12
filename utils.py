import uuid
import logging
from datetime import UTC, datetime

# ----------------------------
# Logging Setup
# ----------------------------


def get_logger(name: str):
    """
    Creates a formatted logger for any microservice.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# ----------------------------
# UUID Helper
# ----------------------------


def generate_id(prefix: str = "") -> str:
    """
    Generates unique IDs for trips, events, etc.
    """
    value = f"{prefix}{uuid.uuid4().hex[:12]}"
    return value


# ----------------------------
# Timestamp Helper
# ----------------------------


def now_timestamp() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def utc_now() -> datetime:
    """Alias used by service engines that need explicit UTC timestamps."""
    return now_timestamp()


# ----------------------------
# Zone Utility Helper
# ----------------------------


def zone_from_coordinates(lat: float, lon: float) -> str:
    """
    Converts coordinates into artificial zones.
    In a real system, this uses geohashing.
    """
    lat_bucket = int(lat * 10) % 5
    lon_bucket = int(lon * 10) % 5
    return f"Z{lat_bucket}{lon_bucket}"
