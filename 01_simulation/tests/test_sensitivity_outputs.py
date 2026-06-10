from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"
PNG_DIR = SIM_ROOT / "figures" / "png"


SENSITIVITY_CSV_FILES = {
    "sensitivity_summary.csv",
    "sensitivity_case_details.csv",
    "sensitivity_constraints.csv",
    "sensitivity_best_candidates.csv",
    "sensitivity_tornado_data.csv",
}


def test_sensitivity_csv_outputs_are_lf_separated_and_readable() -> None:
    for filename in SENSITIVITY_CSV_FILES:
        path = CSV_DIR / filename

        assert path.exists(), f"Expected generated sensitivity CSV: {path}"
        content = path.read_bytes()
        assert b"\n" in content
        assert b"\r" not in content
        assert not pd.read_csv(path).empty


def test_sensitivity_summary_contains_required_columns() -> None:
    table = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")

    assert len(table) >= 20
    assert {
        "case_id",
        "case_family",
        "changed_parameter",
        "changed_value",
        "propulsion_case",
        "mission_fuel_kg",
        "fuel_delta_vs_baseline_pct",
        "estimated_mtow_kg",
        "mtow_margin_to_upper_kg",
        "min_thrust_margin_N",
        "min_thrust_margin_ratio",
        "unmet_electric_load_Wh",
        "takeoff_proxy_index",
        "landing_proxy_index",
        "constraint_count",
        "conclusion_status",
    }.issubset(table.columns)
    assert not table["conclusion_status"].str.contains("validated").any()
    assert table[table["min_thrust_margin_N"] < 0.0]["constraint_count"].gt(0).all()


def test_sensitivity_best_candidates_include_selection_reason() -> None:
    table = pd.read_csv(CSV_DIR / "sensitivity_best_candidates.csv")

    assert "reason_selected" in table.columns
    assert "validated" not in " ".join(table["conclusion_status"].astype(str).tolist())
    assert table["reason_selected"].astype(str).str.len().gt(0).all()


def test_sensitivity_figures_exist() -> None:
    for filename in (
        "constraint_tornado.png",
        "pareto_fuel_vs_mtow.png",
        "thrust_margin_vs_engine_rating.png",
        "hybrid_power_sizing_map.png",
        "takeoff_proxy_sensitivity.png",
    ):
        assert (PNG_DIR / filename).exists()
