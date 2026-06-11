from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


CORRECTED_COLUMNS = {
    "raw_min_thrust_margin_N",
    "raw_min_thrust_margin_ratio",
    "raw_low_thrust_margin",
    "raw_limiting_segment",
    "corrected_approach_min_thrust_margin_N",
    "corrected_approach_min_thrust_margin_ratio",
    "corrected_low_thrust_margin",
    "approach_model_sensitive",
    "sizing_or_schedule_low_thrust",
    "unmet_electric_load",
    "unmet_electric_load_Wh",
    "within_mtow_upper_bound",
    "feasible_basic_raw",
    "feasible_basic_corrected",
    "conclusion_status_raw",
    "conclusion_status_corrected",
}


def test_corrected_constraint_columns_exist() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    details = pd.read_csv(CSV_DIR / "sensitivity_case_details.csv")

    assert CORRECTED_COLUMNS.issubset(summary.columns)
    assert "raw_min_margin_segment_name" in details.columns


def test_corrected_constraint_outputs_are_readable_and_lf_separated() -> None:
    for filename in (
        "sensitivity_corrected_constraint_summary.csv",
        "sensitivity_approach_classification.csv",
    ):
        path = CSV_DIR / filename
        content = path.read_bytes()

        assert path.exists()
        assert b"\n" in content
        assert b"\r" not in content
        assert not pd.read_csv(path).empty


def test_corrected_low_thrust_count_does_not_exceed_raw_count() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    raw_count = int(summary["raw_low_thrust_margin"].sum())
    corrected_count = int(summary["corrected_low_thrust_margin"].sum())
    approach_sensitive_count = int(summary["approach_model_sensitive"].sum())

    assert raw_count >= corrected_count
    assert approach_sensitive_count >= 0


def test_no_corrected_sensitivity_case_is_marked_validated() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")

    combined_status = " ".join(
        summary[
            ["conclusion_status", "conclusion_status_raw", "conclusion_status_corrected"]
        ]
        .astype(str)
        .to_numpy()
        .ravel()
    )
    assert "validated" not in combined_status


def test_best_candidates_follow_corrected_feasibility_logic() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    best = pd.read_csv(CSV_DIR / "sensitivity_best_candidates.csv")

    assert {"reason_selected", "feasible_basic_corrected"}.issubset(best.columns)
    if summary["feasible_basic_corrected"].any():
        assert best["feasible_basic_corrected"].any()
    else:
        assert best["reason_selected"].astype(str).str.len().gt(0).all()


def test_hybrid_unmet_electric_load_is_not_hidden() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    hybrid = summary[
        summary["propulsion_case"] == "adaptive_cycle_plus_hybrid_electric"
    ]
    unmet_rows = hybrid[hybrid["unmet_electric_load_Wh"] > 0.0]

    assert not unmet_rows.empty
    assert unmet_rows["unmet_electric_load"].all()
