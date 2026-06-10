from pathlib import Path

from mta_vhep.aircraft.weights import WeightBuildUp
from mta_vhep.interfaces.io import load_project_config, load_yaml


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _weight_builder() -> WeightBuildUp:
    project = load_project_config(CONFIG_DIR)
    mission_solver = load_yaml(CONFIG_DIR / "mission_solver.yaml")["mission_solver"]
    hybrid = load_yaml(CONFIG_DIR / "hybrid_electric.yaml")["hybrid_electric"]
    return WeightBuildUp(
        mission_solver["weights"],
        hybrid_config=hybrid,
        engine_count=project.main_engine.count,
    )


def test_weight_breakdown_components_are_non_negative() -> None:
    breakdown = _weight_builder().estimate(
        fuel_kg=12000.0,
        hybrid_mass_penalty_enabled=False,
    )

    for value in (
        breakdown.payload_kg,
        breakdown.oew_kg,
        breakdown.fuel_kg,
        breakdown.main_engines_kg,
        breakdown.hybrid_fixed_mass_kg,
        breakdown.hybrid_power_mass_kg,
        breakdown.battery_mass_kg,
        breakdown.hybrid_total_mass_kg,
        breakdown.estimated_mtow_kg,
    ):
        assert value >= 0.0


def test_hybrid_case_includes_hybrid_mass_penalty() -> None:
    builder = _weight_builder()

    baseline = builder.estimate(
        fuel_kg=12000.0,
        hybrid_mass_penalty_enabled=False,
    )
    hybrid = builder.estimate(
        fuel_kg=12000.0,
        hybrid_mass_penalty_enabled=True,
        total_electric_power_W=4000000.0,
    )

    assert hybrid.hybrid_total_mass_kg > baseline.hybrid_total_mass_kg
    assert hybrid.estimated_mtow_kg > baseline.estimated_mtow_kg
