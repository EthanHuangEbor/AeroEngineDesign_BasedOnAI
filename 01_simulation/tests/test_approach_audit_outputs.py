from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"
PNG_DIR = SIM_ROOT / "figures" / "png"


def test_approach_audit_csv_outputs_exist_and_are_readable() -> None:
    expected = {
        "approach_landing_diagnostics.csv": 3,
        "approach_sensitivity_scan.csv": 18,
    }
    for filename, minimum_rows in expected.items():
        path = CSV_DIR / filename

        assert path.exists()
        content = path.read_bytes()
        assert b"\n" in content
        assert b"\r" not in content
        assert len(pd.read_csv(path)) >= minimum_rows


def test_approach_landing_diagnostics_columns_and_rows() -> None:
    table = pd.read_csv(CSV_DIR / "approach_landing_diagnostics.csv")

    assert len(table) == 3
    assert {
        "case_name",
        "segment_name",
        "weight_N",
        "speed_mps",
        "altitude_m",
        "gamma_deg",
        "drag_N",
        "weight_component_along_path_N",
        "required_thrust_level_flight_N",
        "required_thrust_descent_N",
        "available_thrust_N",
        "electric_thrust_proxy_N",
        "net_required_thrust_after_electric_N",
        "thrust_margin_level_flight_N",
        "thrust_margin_descent_N",
        "thrust_margin_change_due_to_descent_N",
        "conclusion_flag",
    }.issubset(table.columns)
    assert not table["conclusion_flag"].str.contains("validated").any()


def test_approach_sensitivity_scan_columns_and_no_validated_cases() -> None:
    table = pd.read_csv(CSV_DIR / "approach_sensitivity_scan.csv")

    assert len(table) >= 18
    assert {
        "case_name",
        "gamma_deg",
        "approach_drag_factor",
        "rating",
        "electric_assist_enabled",
        "thrust_margin_descent_N",
        "conclusion_flag",
    }.issubset(table.columns)
    assert not table["conclusion_flag"].str.contains("validated").any()


def test_approach_audit_png_outputs_exist() -> None:
    for filename in (
        "approach_thrust_margin_audit.png",
        "approach_sensitivity_scan.png",
    ):
        assert (PNG_DIR / filename).exists()
