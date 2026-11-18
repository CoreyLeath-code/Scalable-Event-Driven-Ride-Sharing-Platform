import pytest

from pricing_engine import PricingEngine


def test_pricing_engine_uses_base_surge_when_supply_exceeds_demand():
    event = PricingEngine(base_surge=1.0, sensitivity=0.15).compute_surge(
        demand=2,
        supply=10,
        zone_id="Z00",
    )

    assert event.surge_multiplier == 1.03
    assert event.zone_id == "Z00"


def test_pricing_engine_caps_zero_supply_at_high_surge():
    event = PricingEngine(base_surge=1.0, sensitivity=0.15).compute_surge(
        demand=20,
        supply=0,
        zone_id="Z99",
    )

    assert event.surge_multiplier == 3.0


@pytest.mark.parametrize(
    "demand,supply",
    [(-1, 10), (10, -1), (1.5, 2), (True, 2), (2, False)],
)
def test_pricing_rejects_invalid_counts(demand, supply):
    with pytest.raises(ValueError):
        PricingEngine().compute_surge(demand=demand, supply=supply, zone_id="Z00")


def test_pricing_zero_demand_does_not_surge():
    event = PricingEngine().compute_surge(demand=0, supply=0, zone_id="Z00")
    assert event.surge_multiplier == 1.0


def test_pricing_caps_high_demand_with_nonzero_supply():
    event = PricingEngine().compute_surge(demand=100000, supply=1, zone_id="Z00")
    assert event.surge_multiplier == 3.0


@pytest.mark.parametrize(
    "base,sensitivity",
    [(0.5, 0.15), (float("nan"), 0.15), (1.0, -0.1), (1.0, float("inf"))],
)
def test_pricing_rejects_invalid_configuration(base, sensitivity):
    with pytest.raises(ValueError):
        PricingEngine(base_surge=base, sensitivity=sensitivity)


def test_pricing_rejects_blank_zone():
    with pytest.raises(ValueError):
        PricingEngine().compute_surge(demand=1, supply=1, zone_id="  ")
