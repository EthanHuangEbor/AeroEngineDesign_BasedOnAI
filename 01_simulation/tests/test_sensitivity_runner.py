from pathlib import Path

import pytest

from mta_vhep.analysis.sensitivity import SensitivityRunner
from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml
from mta_vhep.propulsion.fuel import get_fuel


SIM_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = SIM_ROOT / "config"


@pytest.fixture(scope="module")
def sensitivity_tables():
    runner = SensitivityRunner(
        project_config=load_project_config(CONFIG_DIR),
        sensitivity_config=load_yaml(CONFIG_DIR / "sensitivity.yaml"),
        mission_solver_config=load_yaml(CONFIG_DIR / "mission_solver.yaml"),
        aero_config=load_yaml(CONFIG_DIR / "aero_model.yaml"),
        propulsion_config=load_yaml(CONFIG_DIR / "propulsion.yaml"),
        engine_config=load_yaml(CONFIG_DIR / "engine_surrogate.yaml"),
        hybrid_config=load_yaml(CONFIG_DIR / "hybrid_electric.yaml"),
        fuel=get_fuel(load_fuel_database(CONFIG_DIR), "Jet-A"),
    )
    return runner.run()


def test_sensitivity_runner_creates_screening_cases(sensitivity_tables) -> None:
    summary = sensitivity_tables["summary"]

    assert len(summary) >= 20
    assert set(summary[summary["case_family"] == "baseline"]["propulsion_case"]) == {
        "baseline_fixed_cycle_turbofan",
        "adaptive_cycle_turbofan",
        "adaptive_cycle_plus_hybrid_electric",
    }


def test_sensitivity_outputs_are_not_marked_validated(sensitivity_tables) -> None:
    summary = sensitivity_tables["summary"]

    assert not summary["conclusion_status"].str.contains("validated").any()


def test_low_thrust_margin_cases_remain_flagged(sensitivity_tables) -> None:
    summary = sensitivity_tables["summary"]
    low_margin = summary[summary["min_thrust_margin_N"] < 0.0]

    assert not low_margin.empty
    assert (
        (low_margin["constraint_count"] > 0)
        | (low_margin["conclusion_status"] == "rejected_low_thrust_margin")
    ).all()


def test_increasing_engine_thrust_improves_minimum_margin(sensitivity_tables) -> None:
    summary = sensitivity_tables["summary"]
    baseline = summary[
        (summary["case_family"] == "baseline")
        & (summary["propulsion_case"] == "adaptive_cycle_turbofan")
    ].iloc[0]
    thrust_sweep = summary[
        (summary["changed_parameter"] == "sea_level_static_thrust_N_per_engine")
        & (summary["propulsion_case"] == "adaptive_cycle_turbofan")
    ].copy()
    thrust_sweep["changed_value_float"] = thrust_sweep["changed_value"].astype(float)
    ordered = thrust_sweep.sort_values("changed_value_float")

    assert ordered.iloc[0]["min_thrust_margin_N"] >= baseline["min_thrust_margin_N"]
    assert ordered.iloc[-1]["min_thrust_margin_N"] >= ordered.iloc[0]["min_thrust_margin_N"]


def test_increasing_battery_capacity_does_not_worsen_unmet_load(sensitivity_tables) -> None:
    summary = sensitivity_tables["summary"]
    battery_sweep = summary[
        (summary["changed_parameter"] == "battery_capacity_Wh")
        & (summary["propulsion_case"] == "adaptive_cycle_plus_hybrid_electric")
    ].copy()
    battery_sweep["changed_value_float"] = battery_sweep["changed_value"].astype(float)
    low_capacity = battery_sweep[
        battery_sweep["changed_value_float"] == battery_sweep["changed_value_float"].min()
    ].iloc[0]
    high_capacity = battery_sweep[
        battery_sweep["changed_value_float"] == battery_sweep["changed_value_float"].max()
    ].iloc[0]

    assert high_capacity["unmet_electric_load_Wh"] <= low_capacity["unmet_electric_load_Wh"]


def test_increasing_hybrid_mass_worsens_or_preserves_mtow(sensitivity_tables) -> None:
    summary = sensitivity_tables["summary"]
    mass_sweep = summary[
        (summary["changed_parameter"] == "hybrid_mass_per_MW_kg")
        & (summary["propulsion_case"] == "adaptive_cycle_plus_hybrid_electric")
    ].copy()
    mass_sweep["changed_value_float"] = mass_sweep["changed_value"].astype(float)
    low_mass = mass_sweep[
        mass_sweep["changed_value_float"] == mass_sweep["changed_value_float"].min()
    ].iloc[0]
    high_mass = mass_sweep[
        mass_sweep["changed_value_float"] == mass_sweep["changed_value_float"].max()
    ].iloc[0]

    assert high_mass["estimated_mtow_kg"] >= low_mass["estimated_mtow_kg"]
