from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class RideRequestedEvent(BaseModel):
    ride_id: UUID
    rider_id: UUID
    pickup_lat: float
    pickup_lng: float
    destination_lat: float
    destination_lng: float
    timestamp: datetime


class DriverAssignedEvent(BaseModel):
    ride_id: UUID
    driver_id: UUID
    assigned_at: datetime
