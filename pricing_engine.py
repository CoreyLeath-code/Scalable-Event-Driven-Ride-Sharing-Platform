from models import PricingEvent
from utils import get_logger, utc_now


class PricingEngine:
    """
    Dynamic surge pricing engine.
    Computes surge multipliers based on supply/demand
    in specific geographic zones.
    """

    def __init__(self, base_surge: float = 1.0, sensitivity: float = 0.15):
        """
        base_surge: minimum multiplier
        sensitivity: how strongly demand affects pricing
        """
        self.base_surge = base_surge
        self.sensitivity = sensitivity
        self.logger = get_logger("PricingEngine")

    def compute_surge(self, demand: int, supply: int, zone_id: str) -> PricingEvent:
        """
        demand: number of ride requests in zone
        supply: number of available drivers in zone
        """

        if supply == 0:
            surge_multiplier = self.base_surge * 3.0  # high surge cap
        else:
            ratio = demand / supply
            surge_multiplier = self.base_surge + (ratio * self.sensitivity)

        surge_multiplier = round(max(surge_multiplier, 1.0), 2)

        self.logger.info(
            f"[Zone {zone_id}] Demand={demand}, Supply={supply}, Surge={surge_multiplier}"
        )

        return PricingEvent(
            zone_id=zone_id,
            demand=demand,
            supply=supply,
            surge_multiplier=surge_multiplier,
            timestamp=utc_now(),
        )
