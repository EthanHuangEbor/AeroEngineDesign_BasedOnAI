from pathlib import Path

from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml
from mta_vhep.mission.mission_solver import SegmentedMissionSolver
from mta_vhep.propulsion.fuel import get_fuel


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _solver() -> SegmentedMissionSolver:
    return SegmentedMissionSolver(
        project_config=load_project_config(CONFIG_DIR),
        mission_solver_config=load_yaml(CONFIG_DIR / "mission_solver.yaml"),
        aero_config=load_yaml(CONFIG_DIR / "aero_model.yaml"),
        propulsion_config=load_yaml(CONFIG_DIR / "propulsion.yaml"),
        engine_config=load_yaml(CONFIG_DIR / "engine_surrogate.yaml"),
        hybrid_config=load_yaml(CONFIG_DIR / "hybrid_electric.yaml"),
        fuel=get_fuel(load_fuel_database(CONFIG_DIR), "Jet-A"),
    )


def test_mission_summary_has_three_cases() -> None:
    results = _solver().run_all_cases()

    assert len(results) == 3
    assert {result.case_name for result in results} == {
        "baseline_fixed_cycle_turbofan",
        "adaptive_cycle_turbofan",
        "adaptive_cycle_plus_hybrid_electric",
    }


def test_mission_fuel_burn_is_positive_and_final_mass_decreases() -> None:
    results = _solver().run_all_cases()

    for result in results:
        assert result.block_fuel_kg > 0.0
        assert result.mission_fuel_kg > result.block_fuel_kg
        assert result.final_mass_kg < result.start_mass_kg


def test_constraint_flags_are_exportable_lists() -> None:
    results = _solver().run_all_cases()

    for result in results:
        assert isinstance(result.constraint_violations, list)
        assert all(isinstance(flag, str) for flag in result.constraint_violations)
        for segment in result.segment_results:
            assert isinstance(segment.constraint_flags, list)


def test_hybrid_case_records_electric_energy_and_soc() -> None:
    results = {result.case_name: result for result in _solver().run_all_cases()}
    hybrid = results["adaptive_cycle_plus_hybrid_electric"]

    assert hybrid.electric_energy_Wh > 0.0
    assert hybrid.max_electric_power_W > 0.0
    assert any(segment.soc_start is not None for segment in hybrid.segment_results)
    assert any(segment.soc_end is not None for segment in hybrid.segment_results)


def test_turning_electric_assist_off_removes_electric_energy_use() -> None:
    results = {result.case_name: result for result in _solver().run_all_cases()}

    assert results["baseline_fixed_cycle_turbofan"].electric_energy_Wh == 0.0
    assert results["adaptive_cycle_turbofan"].electric_energy_Wh == 0.0
