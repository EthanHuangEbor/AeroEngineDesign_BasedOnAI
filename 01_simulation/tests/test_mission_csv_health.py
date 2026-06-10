from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


MISSION_CSV_ROW_COUNTS = {
    "mission_segments.csv": 18,
    "mission_summary.csv": 3,
    "weight_breakdown.csv": 3,
    "takeoff_landing_proxy.csv": 3,
}


def test_mission_csv_files_are_lf_separated_and_readable() -> None:
    for filename, expected_rows in MISSION_CSV_ROW_COUNTS.items():
        path = CSV_DIR / filename

        assert path.exists()
        content = path.read_bytes()
        assert content.count(b"\n") >= expected_rows + 1
        assert content.count(b"\r") == 0
        assert len(pd.read_csv(path)) == expected_rows

    constraints_path = CSV_DIR / "mission_constraint_violations.csv"
    assert constraints_path.exists()
    constraints_content = constraints_path.read_bytes()
    assert b"\n" in constraints_content
    assert b"\r" not in constraints_content
    assert len(pd.read_csv(constraints_path)) >= 1


def test_mission_summary_health_columns_exist() -> None:
    table = pd.read_csv(CSV_DIR / "mission_summary.csv")

    assert {
        "case_name",
        "block_fuel_kg",
        "reserve_fuel_kg",
        "mission_fuel_kg",
        "electric_energy_Wh",
        "max_electric_power_W",
        "max_thermal_load_W",
        "constraint_violations",
    }.issubset(table.columns)


def test_weight_breakdown_margin_columns_exist() -> None:
    table = pd.read_csv(CSV_DIR / "weight_breakdown.csv")

    assert {
        "case_name",
        "fuel_kg",
        "hybrid_total_mass_kg",
        "estimated_mtow_kg",
        "mtow_margin_kg",
        "mtow_initial_kg",
        "mtow_range_lower_kg",
        "mtow_range_upper_kg",
        "mtow_margin_to_initial_kg",
        "mtow_margin_to_upper_kg",
        "within_v01_mtow_range",
    }.issubset(table.columns)


def test_takeoff_landing_proxy_health_columns_exist() -> None:
    table = pd.read_csv(CSV_DIR / "takeoff_landing_proxy.csv")

    assert {
        "case_name",
        "takeoff_proxy_index",
        "landing_proxy_index",
    }.issubset(table.columns)


def test_mission_diagnostic_outputs_exist_and_have_expected_columns() -> None:
    diagnostics = pd.read_csv(CSV_DIR / "mission_diagnostics.csv")
    status = pd.read_csv(CSV_DIR / "mission_case_status.csv")
    proxy_components = pd.read_csv(CSV_DIR / "takeoff_landing_proxy_components.csv")

    assert len(diagnostics) == 18
    assert len(status) == 3
    assert len(proxy_components) == 3
    assert {
        "case_name",
        "segment_name",
        "segment_type",
        "required_thrust_N",
        "available_thrust_N",
        "thrust_margin_N",
        "thrust_margin_ratio",
        "fuel_burn_kg",
        "electric_energy_Wh",
        "soc_start",
        "soc_end",
        "unmet_electric_load_Wh",
        "constraint_flags",
    }.issubset(diagnostics.columns)
    assert {
        "case_name",
        "computational_success",
        "has_low_thrust_margin",
        "has_unmet_electric_load",
        "estimated_mtow_kg",
        "mtow_initial_kg",
        "mtow_range_upper_kg",
        "mtow_margin_to_initial_kg",
        "mtow_margin_to_upper_kg",
        "within_v01_mtow_range",
        "mission_fuel_kg",
        "apparent_fuel_delta_vs_baseline_pct",
        "conclusion_status",
    }.issubset(status.columns)
    assert {
        "case_name",
        "weight_kg",
        "density_kg_m3",
        "wing_area_m2",
        "clmax_effective",
        "effective_thrust_N",
        "electric_thrust_proxy_N",
        "hybrid_mass_penalty_kg",
        "takeoff_proxy_index",
        "landing_proxy_index",
    }.issubset(proxy_components.columns)
