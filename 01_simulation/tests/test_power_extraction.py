from pathlib import Path

import pytest

from mta_vhep.interfaces.io import load_yaml
from mta_vhep.propulsion.power_extraction import compute_power_extraction_penalty


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _power_config() -> dict:
    config = load_yaml(CONFIG_DIR / "engine_surrogate.yaml")
    return config["engine_surrogate"]["shaft_power_extraction"]


def test_zero_extraction_has_zero_penalties() -> None:
    cfg = _power_config()
    result = compute_power_extraction_penalty(
        shaft_power_extraction_W=0.0,
        mechanical_efficiency=cfg["mechanical_efficiency"],
        propulsive_power_equivalent_efficiency=cfg["propulsive_power_equivalent_efficiency"],
        fuel_flow_increment_per_MW_kg_s=cfg["fuel_flow_increment_per_MW_kg_s"],
        max_extraction_W_per_engine_for_v02=cfg["max_extraction_W_per_engine_for_v02"],
        flight_speed_mps=100.0,
    )

    assert result.equivalent_thrust_penalty_N == 0.0
    assert result.additional_fuel_flow_kg_s == 0.0


def test_positive_extraction_has_positive_penalties() -> None:
    cfg = _power_config()
    result = compute_power_extraction_penalty(
        shaft_power_extraction_W=500000.0,
        mechanical_efficiency=cfg["mechanical_efficiency"],
        propulsive_power_equivalent_efficiency=cfg["propulsive_power_equivalent_efficiency"],
        fuel_flow_increment_per_MW_kg_s=cfg["fuel_flow_increment_per_MW_kg_s"],
        max_extraction_W_per_engine_for_v02=cfg["max_extraction_W_per_engine_for_v02"],
        flight_speed_mps=100.0,
    )

    assert result.equivalent_thrust_penalty_N > 0.0
    assert result.additional_fuel_flow_kg_s > 0.0


def test_extraction_above_limit_raises_value_error() -> None:
    cfg = _power_config()
    with pytest.raises(ValueError):
        compute_power_extraction_penalty(
            shaft_power_extraction_W=cfg["max_extraction_W_per_engine_for_v02"] + 1.0,
            mechanical_efficiency=cfg["mechanical_efficiency"],
            propulsive_power_equivalent_efficiency=cfg["propulsive_power_equivalent_efficiency"],
            fuel_flow_increment_per_MW_kg_s=cfg["fuel_flow_increment_per_MW_kg_s"],
            max_extraction_W_per_engine_for_v02=cfg["max_extraction_W_per_engine_for_v02"],
            flight_speed_mps=100.0,
        )


def test_negative_extraction_raises_value_error() -> None:
    cfg = _power_config()
    with pytest.raises(ValueError):
        compute_power_extraction_penalty(
            shaft_power_extraction_W=-1.0,
            mechanical_efficiency=cfg["mechanical_efficiency"],
            propulsive_power_equivalent_efficiency=cfg["propulsive_power_equivalent_efficiency"],
            fuel_flow_increment_per_MW_kg_s=cfg["fuel_flow_increment_per_MW_kg_s"],
            max_extraction_W_per_engine_for_v02=cfg["max_extraction_W_per_engine_for_v02"],
            flight_speed_mps=100.0,
        )
