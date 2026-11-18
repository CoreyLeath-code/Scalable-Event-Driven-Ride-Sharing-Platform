from math import isfinite

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
        if not isfinite(base_surge) or base_surge < 1.0:
            raise ValueError("base_surge must be finite and at least 1.0")
        if not isfinite(sensitivity) or sensitivity < 0:
            raise ValueError("sensitivity must be finite and nonnegative")
        self.base_surge = base_surge
        self.sensitivity = sensitivity
        self.logger = get_logger("PricingEngine")

    def compute_surge(self, demand: int, supply: int, zone_id: str) -> PricingEvent:
        """
        demand: number of ride requests in zone
        supply: number of available drivers in zone
        """

        if isinstance(demand, bool) or not isinstance(demand, int) or demand < 0:
            raise ValueError("demand must be a nonnegative integer")
        if isinstance(supply, bool) or not isinstance(supply, int) or supply < 0:
            raise ValueError("supply must be a nonnegative integer")
        if not zone_id or not zone_id.strip():
            raise ValueError("zone_id must not be blank")

        # Zero requests should never trigger a surge, even with zero supply.
        if demand == 0:
            surge_multiplier = self.base_surge
        elif supply == 0:
            surge_multiplier = self.base_surge * 3.0
        else:
            surge_multiplier = self.base_surge + (demand / supply * self.sensitivity)

        # Apply the advertised three-times-base cap to every demand scenario.
        surge_multiplier = round(min(max(surge_multiplier, self.base_surge), self.base_surge * 3.0), 2)

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
