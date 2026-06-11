from pathlib import Path

import pandas as pd


SIM_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = SIM_ROOT / "results" / "csv"


def test_reclassified_feasibility_outputs_are_readable() -> None:
    for filename in (
        "sensitivity_feasibility_reclassified.csv",
        "sensitivity_non_approach_constraints.csv",
    ):
        path = CSV_DIR / filename
        content = path.read_bytes()
        table = pd.read_csv(path)

        assert path.exists()
        assert b"\n" in content
        assert b"\r" not in content
        assert not table.empty


def test_feasibility_reclassification_columns_exist() -> None:
    table = pd.read_csv(CSV_DIR / "sensitivity_feasibility_reclassified.csv")

    assert {
        "case_id",
        "approach_only_corrected_margin_N",
        "non_approach_min_thrust_margin_N",
        "corrected_all_segment_min_thrust_margin_N",
        "feasible_basic_approach_corrected",
        "feasible_basic_all_segment_corrected",
        "conclusion_status_all_segment_corrected",
    }.issubset(table.columns)


def test_best_candidates_include_q2_classification_fields() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    best = pd.read_csv(CSV_DIR / "sensitivity_best_candidates.csv")

    assert {
        "candidate_class",
        "reason_selected",
        "not_validated_note",
        "feasible_basic_approach_corrected",
        "feasible_basic_all_segment_corrected",
        "all_segment_corrected_constraint_note",
    }.issubset(best.columns)
    assert best["reason_selected"].astype(str).str.len().gt(0).all()

    if summary["feasible_basic_all_segment_corrected"].any():
        assert best["feasible_basic_all_segment_corrected"].any()
    else:
        assert best["candidate_class"].astype(str).str.contains("diagnostic|approach").any()


def test_non_approach_constraint_rows_explain_remaining_driver() -> None:
    table = pd.read_csv(CSV_DIR / "sensitivity_non_approach_constraints.csv")
    constrained = table[table["non_approach_low_thrust_margin"] == True]  # noqa: E712

    assert not constrained.empty
    assert constrained["suspected_driver"].astype(str).str.len().gt(0).all()


def test_hybrid_unmet_load_remains_visible_after_q2_reclassification() -> None:
    summary = pd.read_csv(CSV_DIR / "sensitivity_summary.csv")
    hybrid = summary[
        summary["propulsion_case"] == "adaptive_cycle_plus_hybrid_electric"
    ]
    unmet = hybrid[hybrid["unmet_electric_load_Wh"] > 0.0]

    assert not unmet.empty
    assert unmet["unmet_electric_load"].all()
