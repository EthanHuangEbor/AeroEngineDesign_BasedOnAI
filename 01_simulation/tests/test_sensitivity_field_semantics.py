from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


def test_q2_semantic_fields_exist() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")

    assert {
        "approach_only_corrected_margin_N",
        "corrected_all_segment_min_thrust_margin_N",
        "non_approach_min_thrust_margin_N",
        "feasible_basic_approach_corrected",
        "feasible_basic_all_segment_corrected",
        "conclusion_status_approach_corrected",
        "conclusion_status_all_segment_corrected",
    }.issubset(summary.columns)


def test_all_segment_corrected_margin_is_minimum_of_component_margins() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    expected = summary[
        ["approach_only_corrected_margin_N", "non_approach_min_thrust_margin_N"]
    ].min(axis=1)

    delta = (summary["corrected_all_segment_min_thrust_margin_N"] - expected).abs()

    assert delta.max() < 1.0e-6


def test_field_semantics_audit_marks_deprecated_alias() -> None:
    path = CSV_DIR / "sensitivity_field_semantics_audit.csv"
    content = path.read_bytes()
    table = pd.read_csv(path)

    assert b"\n" in content
    assert b"\r" not in content
    assert not table.empty

    alias = table[
        table["field_name"] == "corrected_approach_min_thrust_margin_N"
    ].iloc[0]
    assert alias["status"] == "replaced"
    assert "approach_only_corrected_margin_N" in str(alias["new_meaning"])


def test_nominal_approach_replay_is_consistent_with_v04s() -> None:
    replay = pd.read_csv(CSV_DIR / "sensitivity_nominal_replay_comparison.csv")

    assert len(replay) == 3
    assert (replay["consistency_flag"] == "consistent").all()
    assert replay["margin_difference_q2_approach_only_minus_v04s_N"].abs().max() < 1000.0


def test_no_q2_sensitivity_status_is_marked_validated() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    status_columns = [
        "conclusion_status",
        "conclusion_status_raw",
        "conclusion_status_approach_corrected",
        "conclusion_status_all_segment_corrected",
        "conclusion_status_corrected",
    ]
    combined = " ".join(summary[status_columns].astype(str).to_numpy().ravel())

    assert "validated" not in combined
