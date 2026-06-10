from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"
PNG_DIR = SIM_ROOT / "figures" / "png"


def test_hybrid_csv_outputs_exist() -> None:
    for filename in (
        "hybrid_timeline.csv",
        "hybrid_summary.csv",
        "electric_fan_mode_summary.csv",
        "fan_failure_cases.csv",
        "hybrid_power_extraction_proxy.csv",
    ):
        assert (CSV_DIR / filename).exists()


def test_hybrid_png_outputs_exist() -> None:
    for filename in (
        "electric_power_soc.png",
        "electric_fan_thrust_proxy.png",
        "hybrid_thermal_load.png",
        "fan_failure_power_available.png",
    ):
        assert (PNG_DIR / filename).exists()


def test_hybrid_timeline_soc_columns_stay_within_bounds() -> None:
    timeline = pd.read_csv(CSV_DIR / "hybrid_timeline.csv")

    for column in ("soc_initial", "soc_final", "soc_min", "soc_max"):
        assert timeline[column].between(0.0, 1.0).all()


def test_failure_cases_include_configured_cases_and_no_assist_case_is_zero() -> None:
    cases = pd.read_csv(CSV_DIR / "fan_failure_cases.csv")

    assert set(cases["case_name"]) == {
        "all_fans_available",
        "single_fan_failed",
        "one_side_failed",
        "all_electric_assist_unavailable",
    }
    unavailable = cases[cases["case_name"] == "all_electric_assist_unavailable"].iloc[0]
    assert unavailable["total_fan_thrust_N"] == 0.0
