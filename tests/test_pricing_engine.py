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
