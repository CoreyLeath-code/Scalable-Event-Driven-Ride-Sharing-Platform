from datetime import datetime

from pydantic import BaseModel

# ----------------------------
# Pricing Events
# ----------------------------


class PricingEvent(BaseModel):
    zone_id: str
    demand: int
    supply: int
    surge_multiplier: float
    timestamp: datetime


# ----------------------------
# Driver Telemetry Events
# ----------------------------


class DriverLocationEvent(BaseModel):
    driver_id: str
    lat: float
    lon: float
    timestamp: datetime
    status: str  # ("available", "en_route", "on_trip")


# ----------------------------
# Rider Trip Request Events
# ----------------------------


class TripRequestEvent(BaseModel):
    rider_id: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    timestamp: datetime


# ----------------------------
# Trip Matching Results
# ----------------------------


class MatchResultEvent(BaseModel):
    trip_id: str
    driver_id: str
    rider_id: str
    eta_minutes: float
    surge_multiplier: float
    timestamp: datetime


# ----------------------------
# Optional expansion events:
# - PaymentEvent
# - DriverEarningsEvent
# - RideCompletionEvent
# - ZoneAggregationEvent
# ----------------------------


class PaymentEvent(BaseModel):
    trip_id: str
    rider_id: str
    driver_id: str
    total_cost: float
    surge_multiplier: float
    timestamp: datetime
