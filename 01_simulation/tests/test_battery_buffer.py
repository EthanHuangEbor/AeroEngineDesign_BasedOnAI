from mta_vhep.electrical.battery_buffer import BatteryBuffer


def test_soc_remains_within_zero_to_one() -> None:
    battery = BatteryBuffer(1000, 0.5, 0.2, 0.95, 1000, 500, 0.92)
    battery.update(500, 60)
    battery.update(-200, 60)

    assert 0.0 <= battery.state.soc <= 1.0


def test_battery_cannot_discharge_below_min_soc() -> None:
    battery = BatteryBuffer(1000, 0.21, 0.2, 0.95, 100000, 500, 0.92)
    battery.update(100000, 3600)

    assert battery.state.soc >= 0.2


def test_over_discharge_creates_unmet_load() -> None:
    battery = BatteryBuffer(1000, 0.21, 0.2, 0.95, 100000, 500, 0.92)
    result = battery.update(100000, 3600)

    assert result.unmet_power_W > 0.0


def test_charging_cannot_exceed_max_soc() -> None:
    battery = BatteryBuffer(1000, 0.94, 0.2, 0.95, 1000, 100000, 0.92)
    result = battery.update(-100000, 3600)

    assert battery.state.soc <= 0.95
    assert result.rejected_charge_power_W > 0.0
