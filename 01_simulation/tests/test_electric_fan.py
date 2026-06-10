from mta_vhep.electrical.inverter import InverterModel
from mta_vhep.electrical.motor import MotorModel
from mta_vhep.propulsion.electric_fan import ElectricBlownFlapFan, ElectricFanCommand


def _fan() -> ElectricBlownFlapFan:
    return ElectricBlownFlapFan(
        nominal_power_W=1_000_000,
        max_power_W_for_v02=2_000_000,
        propulsive_efficiency=0.72,
        min_effective_airspeed_mps=35.0,
        mode_power_fractions={"off": 0.0, "assist": 1.0, "degraded": 0.5, "failed": 0.0},
        motor=MotorModel(0.95, 6.0),
        inverter=InverterModel(0.98, 12.0),
    )


def _command(mode: str, input_power_W: float | None = None) -> ElectricFanCommand:
    return ElectricFanCommand(
        mode=mode,
        airspeed_mps=75.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        input_power_W=input_power_W,
    )


def test_off_and_failed_modes_produce_zero_outputs() -> None:
    fan = _fan()

    for mode in ("off", "failed"):
        result = fan.evaluate(_command(mode))
        assert result.shaft_power_W == 0.0
        assert result.thrust_N == 0.0
        assert result.blowing_momentum_coefficient == 0.0


def test_assist_mode_produces_positive_power_and_thrust() -> None:
    result = _fan().evaluate(_command("assist"))

    assert result.shaft_power_W > 0.0
    assert result.thrust_N > 0.0


def test_higher_power_increases_thrust_and_cmu() -> None:
    fan = _fan()
    low = fan.evaluate(_command("assist", input_power_W=250_000))
    high = fan.evaluate(_command("assist", input_power_W=1_000_000))

    assert high.thrust_N > low.thrust_N
    assert high.blowing_momentum_coefficient > low.blowing_momentum_coefficient


def test_degraded_mode_uses_less_power_than_assist() -> None:
    fan = _fan()

    assert fan.evaluate(_command("degraded")).input_power_W < fan.evaluate(
        _command("assist")
    ).input_power_W
