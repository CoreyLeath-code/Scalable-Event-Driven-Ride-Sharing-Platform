from typing import List, Optional
from math import sqrt

from models import DriverLocationEvent, MatchResultEvent, TripRequestEvent
from utils import get_logger, now_timestamp


class MatchingEngine:
    """
    Core driver–rider matching algorithm.

    This version uses:
    - Euclidean distance heuristic
    - Simple ETA estimation
    - Surge-aware scoring
    - Top-K candidate ranking

    In real systems (Uber, Lyft), this would expand into:
    - H3 geospatial indexing
    - ML-based ETA prediction
    - Supply/demand balancing
    """

    def __init__(self, max_candidates: int = 25):
        self.max_candidates = max_candidates
        self.logger = get_logger("MatchingEngine")

    # ------------------------------------------------------------
    # Distance Heuristic
    # ------------------------------------------------------------

    def _distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Simple Euclidean distance for demo purposes.
        Replace with Haversine or H3 index for production.
        """
        return sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

    # ------------------------------------------------------------
    # ETA Estimation
    # ------------------------------------------------------------

    def _estimate_eta(self, distance: float) -> float:
        """
        ETA calculation: distance * factor
        In real systems: ML model or traffic-aware routing system.
        """
        return round(distance * 4, 2)  # 4 minutes per distance unit heuristic

    # ------------------------------------------------------------
    # Score Function
    # ------------------------------------------------------------

    def _score_driver(self, distance: float, surge_multiplier: float) -> float:
        """
        Higher score = better match.
        Lower distance = higher score.
        Surge slightly boosts score to balance rider demand.
        """
        return max(0.01, (1 / (distance + 0.01))) * surge_multiplier

    # ------------------------------------------------------------
    # Candidate Ranking
    # ------------------------------------------------------------

    def rank_drivers(
        self,
        drivers: List[DriverLocationEvent],
        trip: TripRequestEvent,
        surge_multiplier: float,
    ) -> List[DriverLocationEvent]:
        """
        Sort drivers by score (descending).
        """
        scored = []

        for d in drivers:
            dist = self._distance(d.lat, d.lon, trip.pickup_lat, trip.pickup_lon)

            score = self._score_driver(dist, surge_multiplier)
            scored.append((score, d))

        ranked = sorted(scored, key=lambda x: x[0], reverse=True)
        top_ranked = [d for _, d in ranked[: self.max_candidates]]

        self.logger.info(f"Ranked {len(top_ranked)} drivers for trip {trip.rider_id}")
        return top_ranked

    # ------------------------------------------------------------
    # Match Selection
    # ------------------------------------------------------------

    def select_best_match(
        self,
        drivers: List[DriverLocationEvent],
        trip: TripRequestEvent,
        surge_multiplier: float,
    ) -> Optional[MatchResultEvent]:
        """
        Selects the highest-ranked driver and returns a MatchResultEvent.
        """
        if not drivers:
            self.logger.warning("No available drivers for matching.")
            return None

        ranked = self.rank_drivers(drivers, trip, surge_multiplier)
        best = ranked[0]

        distance = self._distance(best.lat, best.lon, trip.pickup_lat, trip.pickup_lon)
        eta = self._estimate_eta(distance)

        match_event = MatchResultEvent(
            trip_id=f"trip_{trip.rider_id}_{now_timestamp().timestamp()}",
            driver_id=best.driver_id,
            rider_id=trip.rider_id,
            eta_minutes=eta,
            surge_multiplier=surge_multiplier,
            timestamp=now_timestamp(),
        )

        self.logger.info(
            f"Selected driver {best.driver_id} for rider {trip.rider_id} "
            f"(ETA: {eta} mins, Surge: {surge_multiplier})"
        )

        return match_event
