from pytest import approx

from mta_vhep.electrical.bus import ElectricalBus, ElectricalLoad


def test_power_balance_residual_is_small_when_supply_meets_load() -> None:
    bus = ElectricalBus(1500, 0.985, True)
    state = bus.solve([ElectricalLoad("fan", 985.0)], generated_power_W=1000.0, battery_power_W=0.0)

    assert state.unmet_load_W == 0.0
    assert state.residual_power_W == approx(0.0, abs=1e-9)


def test_unmet_load_positive_when_load_exceeds_supply() -> None:
    bus = ElectricalBus(1500, 0.985, True)
    state = bus.solve([ElectricalLoad("fan", 2000.0)], generated_power_W=1000.0, battery_power_W=0.0)

    assert state.unmet_load_W > 0.0


def test_losses_and_thermal_load_are_non_negative() -> None:
    bus = ElectricalBus(1500, 0.985, True)
    state = bus.solve([ElectricalLoad("fan", 1000.0)], generated_power_W=800.0, battery_power_W=400.0)

    assert state.distribution_losses_W >= 0.0
    assert state.thermal_load_W >= 0.0
