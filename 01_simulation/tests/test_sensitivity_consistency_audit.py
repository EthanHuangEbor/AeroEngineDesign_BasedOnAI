from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


AUDIT_CSV_FILES = {
    "sensitivity_nominal_replay_comparison.csv": 3,
    "corrected_approach_input_decomposition.csv": 6,
    "engine_thrust_monotonicity_audit.csv": 3,
    "sensitivity_consistency_audit_summary.csv": 1,
}


def test_sensitivity_consistency_audit_outputs_exist_and_are_readable() -> None:
    for filename, minimum_rows in AUDIT_CSV_FILES.items():
        path = CSV_DIR / filename
        content = path.read_bytes()
        table = pd.read_csv(path)

        assert path.exists()
        assert b"\n" in content
        assert b"\r" not in content
        assert len(table) >= minimum_rows


def test_nominal_replay_has_three_rows() -> None:
    table = pd.read_csv(CSV_DIR / "sensitivity_nominal_replay_comparison.csv")

    assert len(table) == 3
    assert {
        "propulsion_case",
        "v04s_descent_margin_N",
        "v05r_corrected_approach_min_thrust_margin_N",
        "consistency_flag",
    }.issubset(table.columns)


def test_corrected_approach_decomposition_has_required_rows_and_columns() -> None:
    table = pd.read_csv(CSV_DIR / "corrected_approach_input_decomposition.csv")

    assert len(table) >= 6
    assert {
        "selection_label",
        "case_id",
        "propulsion_case",
        "weight_kg",
        "drag_N",
        "required_thrust_descent_N",
        "available_thrust_N",
        "corrected_margin_N",
        "raw_margin_N",
        "v05r_reported_corrected_min_margin_N",
        "approach_margin_minus_v05r_reported_min_N",
        "conclusion_flag",
    }.issubset(table.columns)


def test_engine_thrust_monotonicity_has_failure_causes_when_needed() -> None:
    table = pd.read_csv(CSV_DIR / "engine_thrust_monotonicity_audit.csv")
    failures = table[table["monotonicity_flag"] == "fail"]

    assert len(table) >= 3
    if not failures.empty:
        assert failures["failure_cause"].fillna("").astype(str).str.len().gt(0).all()


def test_audit_outputs_do_not_mark_anything_validated() -> None:
    for filename in AUDIT_CSV_FILES:
        table = pd.read_csv(CSV_DIR / filename)
        text = " ".join(table.astype(str).to_numpy().ravel())

        assert "validated" not in text


def test_inconsistency_has_recommended_next_action() -> None:
    replay = pd.read_csv(CSV_DIR / "sensitivity_nominal_replay_comparison.csv")
    audit_summary = pd.read_csv(CSV_DIR / "sensitivity_consistency_audit_summary.csv")

    if (replay["consistency_flag"] == "inconsistent_requires_diagnosis").any():
        action = audit_summary.loc[
            audit_summary["metric"] == "recommended_next_action",
            "recommended_next_action",
        ].iloc[0]
        assert isinstance(action, str)
        assert len(action) > 0
