from pathlib import Path

import yaml

from mta_vhep.interfaces.io import load_project_config


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def test_frozen_aircraft_values() -> None:
    config = load_project_config(CONFIG_DIR)

    assert config.aircraft.payload_design_kg == 25000
    assert config.aircraft.range_design_km == 3200
    assert config.aircraft.engine_count == 2
    assert config.aircraft.electric_fan_count == 4
    assert config.aircraft.cruise_mach == 0.75
    assert config.aircraft.cruise_altitude_m == 10668
    assert config.aircraft.mtow_initial_kg == 87500
    assert config.aircraft.oew_initial_kg == 52000


def test_frozen_propulsion_values_and_future_flags() -> None:
    config = load_project_config(CONFIG_DIR)

    assert config.main_engine.count == 2
    assert config.main_engine.sea_level_static_thrust_N_per_engine_initial == 115000
    assert config.main_engine.future_hydrogen_enabled is False
    assert config.main_engine.future_detonation_enabled is False
    assert config.electric_fan.count == 4
    assert config.electric_fan.power_W_per_fan_initial == 1000000


def test_mission_and_fuel_config() -> None:
    config = load_project_config(CONFIG_DIR)

    assert config.mission.design_payload_kg == 25000
    assert config.mission.design_range_km == 3200
    assert len(config.mission.segments) >= 6
    assert "Jet-A" in config.fuels
    assert "SAF_generic" in config.fuels


def test_model_is_not_certification_grade() -> None:
    assumptions_path = CONFIG_DIR / "model_assumptions.yaml"
    with assumptions_path.open("r", encoding="utf-8") as handle:
        assumptions = yaml.safe_load(handle)

    assert assumptions["assumption_policy"]["certification_grade"] is False
    assert assumptions["assumption_policy"]["all_outputs_are_model_outputs"] is True
    assert assumptions["assumption_policy"]["no_unverified_performance_claims"] is True
