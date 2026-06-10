from pathlib import Path

import pytest

from mta_vhep.interfaces.io import load_fuel_database, load_yaml
from mta_vhep.propulsion.fuel import get_fuel
from mta_vhep.propulsion.turbofan_vce import EngineOperatingPoint, VariableCycleTurbofan


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _engine_config() -> dict:
    return load_yaml(CONFIG_DIR / "engine_surrogate.yaml")


def _fuel():
    return get_fuel(load_fuel_database(CONFIG_DIR), "Jet-A")


def _engine(variant: str) -> VariableCycleTurbofan:
    return VariableCycleTurbofan.from_config(_engine_config(), variant)


def _op(
    rating: str,
    mach: float,
    altitude_m: float,
    throttle: float,
    shaft_power_extraction_W: float = 0.0,
    third_stream_schedule: float = 0.4,
    variable_nozzle_schedule: float = 0.55,
) -> EngineOperatingPoint:
    return EngineOperatingPoint(
        mach=mach,
        altitude_m=altitude_m,
        throttle=throttle,
        rating=rating,
        shaft_power_extraction_W=shaft_power_extraction_W,
        third_stream_schedule=third_stream_schedule,
        variable_nozzle_schedule=variable_nozzle_schedule,
        fuel=_fuel(),
    )


def test_engine_surrogate_config_loads() -> None:
    config = _engine_config()

    assert config["engine_surrogate"]["model_level"] == "concept_surrogate_v02"
    assert config["engine_surrogate"]["certification_grade"] is False


def test_takeoff_nominal_thrust_exceeds_cruise() -> None:
    engine = _engine("adaptive_cycle")

    takeoff = engine.evaluate(_op("takeoff", 0.20, 0.0, 1.0, third_stream_schedule=0.10, variable_nozzle_schedule=0.85))
    cruise = engine.evaluate(_op("cruise", 0.75, 10668.0, 0.65, third_stream_schedule=0.40, variable_nozzle_schedule=0.55))

    assert takeoff.net_thrust_N > cruise.net_thrust_N


def test_idle_thrust_below_approach_and_climb() -> None:
    engine = _engine("adaptive_cycle")

    idle = engine.evaluate(_op("idle", 0.0, 0.0, 0.10, third_stream_schedule=0.30, variable_nozzle_schedule=0.40))
    approach = engine.evaluate(_op("approach", 0.22, 500.0, 0.35, third_stream_schedule=0.50, variable_nozzle_schedule=0.45))
    climb = engine.evaluate(_op("climb", 0.55, 5000.0, 0.88, third_stream_schedule=0.15, variable_nozzle_schedule=0.70))
    takeoff = engine.evaluate(_op("takeoff", 0.20, 0.0, 1.0, third_stream_schedule=0.10, variable_nozzle_schedule=0.85))

    assert idle.net_thrust_N < approach.net_thrust_N
    assert approach.net_thrust_N < climb.net_thrust_N or approach.net_thrust_N < takeoff.net_thrust_N


def test_adaptive_cruise_tsfc_below_baseline_cruise() -> None:
    baseline = _engine("baseline_fixed_cycle")
    adaptive = _engine("adaptive_cycle")
    op = _op("cruise", 0.75, 10668.0, 0.65, third_stream_schedule=0.40, variable_nozzle_schedule=0.55)

    assert adaptive.evaluate(op).tsfc_kg_per_N_s < baseline.evaluate(op).tsfc_kg_per_N_s


def test_shaft_power_extraction_reduces_net_thrust_and_increases_fuel_flow() -> None:
    engine = _engine("adaptive_cycle")
    base_op = _op("climb", 0.55, 5000.0, 0.88, shaft_power_extraction_W=0.0)
    extraction_op = _op("climb", 0.55, 5000.0, 0.88, shaft_power_extraction_W=1000000.0)

    base = engine.evaluate(base_op)
    extracted = engine.evaluate(extraction_op)

    assert extracted.net_thrust_N < base.net_thrust_N
    assert extracted.fuel_flow_kg_s > base.fuel_flow_kg_s


def test_high_third_stream_improves_adaptive_cruise_tsfc() -> None:
    engine = _engine("adaptive_cycle")
    low = engine.evaluate(_op("cruise", 0.75, 10668.0, 0.65, third_stream_schedule=0.0))
    high = engine.evaluate(_op("cruise", 0.75, 10668.0, 0.65, third_stream_schedule=1.0))

    assert high.tsfc_kg_per_N_s < low.tsfc_kg_per_N_s


def test_high_third_stream_does_not_increase_takeoff_thrust() -> None:
    engine = _engine("adaptive_cycle")
    low = engine.evaluate(
        _op("takeoff", 0.20, 0.0, 1.0, third_stream_schedule=0.0, variable_nozzle_schedule=0.85)
    )
    high = engine.evaluate(
        _op("takeoff", 0.20, 0.0, 1.0, third_stream_schedule=1.0, variable_nozzle_schedule=0.85)
    )

    assert high.net_thrust_N <= low.net_thrust_N


def test_invalid_rating_raises_value_error() -> None:
    engine = _engine("adaptive_cycle")
    with pytest.raises(ValueError, match="invalid_rating"):
        engine.evaluate(_op("military_power", 0.5, 1000.0, 0.8))
