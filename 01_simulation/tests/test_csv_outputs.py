from pathlib import Path

import pandas as pd
import pytest


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


CSV_EXPECTATIONS = {
    "atmosphere_table.csv": {
        "rows": 7,
        "columns": {"altitude_m", "temperature_K", "density_kg_m3"},
    },
    "aero_check_table.csv": {
        "rows": 12,
        "columns": {"flap_mode", "cl", "cd", "ld_ratio", "cl_max", "stall_speed_mps"},
    },
    "engine_design_points.csv": {
        "rows": 10,
        "columns": {
            "variant",
            "design_point",
            "net_thrust_N",
            "fuel_flow_kg_s",
            "tsfc_kg_per_N_s",
        },
    },
    "engine_power_extraction_sweep.csv": {
        "rows": 15,
        "columns": {
            "shaft_power_extraction_W",
            "net_thrust_N",
            "fuel_flow_kg_s",
            "thrust_penalty_from_extraction_N",
        },
    },
}


@pytest.mark.parametrize("filename, expectation", CSV_EXPECTATIONS.items())
def test_result_csv_has_newline_rows_and_expected_shape(filename: str, expectation: dict) -> None:
    path = CSV_DIR / filename

    assert path.exists(), f"Expected generated CSV file: {path}"
    content = path.read_bytes()
    expected_rows = expectation["rows"]

    assert content.count(b"\n") >= expected_rows
    assert len(content.splitlines()) == expected_rows + 1

    table = pd.read_csv(path)
    assert len(table) == expected_rows
    assert expectation["columns"].issubset(table.columns)
