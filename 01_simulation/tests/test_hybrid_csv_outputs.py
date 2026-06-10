from pathlib import Path

import pandas as pd
import pytest


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"

HYBRID_CSV_EXPECTATIONS = {
    "hybrid_timeline.csv": {
        "min_rows": 4,
        "columns": {
            "phase",
            "soc_initial",
            "soc_final",
            "total_fan_thrust_N",
            "unmet_load_W",
            "shaft_power_extraction_W_per_engine",
        },
    },
    "hybrid_summary.csv": {
        "min_rows": 1,
        "columns": {
            "phase_count",
            "soc_min",
            "soc_max",
            "peak_total_fan_thrust_N",
            "total_unmet_load_Wh",
        },
    },
    "electric_fan_mode_summary.csv": {
        "min_rows": 4,
        "columns": {"mode", "input_power_W_per_fan", "thrust_N_per_fan"},
    },
    "fan_failure_cases.csv": {
        "min_rows": 4,
        "columns": {"case_name", "available_fan_count", "total_fan_thrust_N", "c_mu_proxy"},
    },
    "hybrid_power_extraction_proxy.csv": {
        "min_rows": 3,
        "columns": {
            "phase",
            "shaft_power_extraction_W_per_engine",
            "thrust_penalty_from_extraction_N",
            "fuel_flow_increment_from_extraction_kg_s",
        },
    },
}


@pytest.mark.parametrize("filename, expectation", HYBRID_CSV_EXPECTATIONS.items())
def test_hybrid_csv_files_have_newline_rows_and_expected_columns(
    filename: str,
    expectation: dict,
) -> None:
    path = CSV_DIR / filename

    assert path.exists(), f"Expected generated hybrid CSV file: {path}"
    content = path.read_bytes()
    lines = content.splitlines()
    assert len(lines) >= expectation["min_rows"] + 1
    assert content.count(b"\n") >= expectation["min_rows"]
    assert b"\r" not in content

    table = pd.read_csv(path)
    assert len(table) >= expectation["min_rows"]
    assert expectation["columns"].issubset(table.columns)


def test_hybrid_timeline_soc_values_stay_within_zero_to_one() -> None:
    timeline = pd.read_csv(CSV_DIR / "hybrid_timeline.csv")

    for column in ("soc_initial", "soc_final", "soc_min", "soc_max"):
        assert timeline[column].between(0.0, 1.0).all()


def test_hybrid_failure_cases_are_directionally_consistent() -> None:
    cases = pd.read_csv(CSV_DIR / "fan_failure_cases.csv").set_index("case_name")

    assert cases.loc["all_electric_assist_unavailable", "total_fan_thrust_N"] == 0.0
    assert (
        cases.loc["all_fans_available", "total_fan_thrust_N"]
        > cases.loc["single_fan_failed", "total_fan_thrust_N"]
    )
