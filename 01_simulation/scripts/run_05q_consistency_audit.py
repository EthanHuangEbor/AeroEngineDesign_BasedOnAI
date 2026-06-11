"""Run V0.2-05Q sensitivity consistency and monotonicity audit."""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


SIM_ROOT = Path(__file__).resolve().parents[1]
if str(SIM_ROOT) not in sys.path:
    sys.path.insert(0, str(SIM_ROOT))

from mta_vhep.aircraft.aerodynamics import AeroModel, AeroState  # noqa: E402
from mta_vhep.analysis.sensitivity import SensitivityRunner  # noqa: E402
from mta_vhep.core.atmosphere import isa_atmosphere  # noqa: E402
from mta_vhep.core.units import kg_to_N  # noqa: E402
from mta_vhep.interfaces.csv_export import write_dataframe_csv  # noqa: E402
from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml  # noqa: E402
from mta_vhep.mission.approach_analysis import (  # noqa: E402
    ApproachForceBalanceInput,
    evaluate_approach_force_balance,
)
from mta_vhep.mission.mission_solver import MissionResult  # noqa: E402
from mta_vhep.propulsion.fuel import get_fuel  # noqa: E402


BASELINE_FIXED_CASE = "baseline_fixed_cycle_turbofan"
ADAPTIVE_CASE = "adaptive_cycle_turbofan"
HYBRID_CASE = "adaptive_cycle_plus_hybrid_electric"
NOMINAL_CASE_IDS = {
    BASELINE_FIXED_CASE: "V05-0001_baseline",
    ADAPTIVE_CASE: "V05-0001_adaptive",
    HYBRID_CASE: "V05-0001_hybrid",
}


@dataclass(frozen=True)
class CaseRecord:
    """Replayed sensitivity case with model result and config copies."""

    case_id: str
    case_family: str
    changed_parameter: str
    changed_value: str
    settings_summary: str
    result: MissionResult
    configs: dict[str, dict[str, Any]]


def main() -> None:
    """Export V0.2-05Q consistency audit CSVs and figures."""
    config_dir = SIM_ROOT / "config"
    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

    summary = pd.read_csv(csv_dir / "sensitivity_summary.csv")
    v04s = pd.read_csv(csv_dir / "approach_landing_diagnostics.csv")
    best = pd.read_csv(csv_dir / "sensitivity_best_candidates.csv")
    records = _build_case_records(config_dir)

    nominal_replay = _nominal_replay_comparison(v04s, summary)
    decomposition = _input_decomposition(summary, best, records)
    monotonicity = _engine_thrust_monotonicity(summary, records)
    audit_summary = _audit_summary(nominal_replay, monotonicity)

    write_dataframe_csv(
        nominal_replay,
        csv_dir / "sensitivity_nominal_replay_comparison.csv",
    )
    write_dataframe_csv(
        decomposition,
        csv_dir / "corrected_approach_input_decomposition.csv",
    )
    write_dataframe_csv(
        monotonicity,
        csv_dir / "engine_thrust_monotonicity_audit.csv",
    )
    write_dataframe_csv(
        audit_summary,
        csv_dir / "sensitivity_consistency_audit_summary.csv",
    )

    _plot_nominal_replay(nominal_replay, png_dir, svg_dir)
    _plot_monotonicity(monotonicity, png_dir, svg_dir)

    inconsistent_count = int(
        (nominal_replay["consistency_flag"] == "inconsistent_requires_diagnosis").sum()
    )
    monotonicity_fail_count = int(
        (monotonicity["monotonicity_flag"] == "fail").sum()
    )
    recommended_action = _recommended_next_action(nominal_replay, monotonicity)

    print("MTA-VHEP V0.2-05Q Sensitivity Consistency Audit Summary")
    print("Concept-level internal consistency audit only; no validation claim.")
    print(f"Nominal replay rows: {len(nominal_replay)}")
    print(f"Nominal replay inconsistent rows: {inconsistent_count}")
    print(f"Input decomposition rows: {len(decomposition)}")
    print(f"Engine thrust monotonicity rows: {len(monotonicity)}")
    print(f"Engine thrust monotonicity failures: {monotonicity_fail_count}")
    print(f"Recommended next action: {recommended_action}")


def _build_case_records(config_dir: Path) -> dict[str, CaseRecord]:
    runner = SensitivityRunner(
        project_config=load_project_config(config_dir),
        sensitivity_config=load_yaml(config_dir / "sensitivity.yaml"),
        mission_solver_config=load_yaml(config_dir / "mission_solver.yaml"),
        aero_config=load_yaml(config_dir / "aero_model.yaml"),
        propulsion_config=load_yaml(config_dir / "propulsion.yaml"),
        engine_config=load_yaml(config_dir / "engine_surrogate.yaml"),
        hybrid_config=load_yaml(config_dir / "hybrid_electric.yaml"),
        fuel=get_fuel(load_fuel_database(config_dir), "Jet-A"),
    )

    records: dict[str, CaseRecord] = {}
    counter = 1
    for family, settings, propulsion_filter in runner._case_settings():  # noqa: SLF001
        case_id_base = f"V05-{counter:04d}"
        counter += 1
        results, configs = runner._run_settings(settings)  # noqa: SLF001
        changed_parameter, changed_value = _changed_parameter_text(settings)
        settings_summary = _settings_summary(settings)
        for result in results:
            if propulsion_filter is not None and result.case_name != propulsion_filter:
                continue
            case_id = f"{case_id_base}_{_case_slug(result.case_name)}"
            records[case_id] = CaseRecord(
                case_id=case_id,
                case_family=family,
                changed_parameter=changed_parameter,
                changed_value=changed_value,
                settings_summary=settings_summary,
                result=result,
                configs=configs,
            )
    return records


def _nominal_replay_comparison(
    v04s: pd.DataFrame,
    summary: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for propulsion_case, case_id in NOMINAL_CASE_IDS.items():
        v04s_row = v04s[v04s["case_name"] == propulsion_case].iloc[0]
        v05r_row = summary[summary["case_id"] == case_id].iloc[0]
        approach_only_margin_N = float(v05r_row["approach_only_corrected_margin_N"])
        all_segment_margin_N = float(
            v05r_row["corrected_all_segment_min_thrust_margin_N"]
        )
        difference_N = (
            approach_only_margin_N - float(v04s_row["thrust_margin_descent_N"])
        )
        rows.append(
            {
                "propulsion_case": propulsion_case,
                "v04s_level_margin_N": float(v04s_row["thrust_margin_level_flight_N"]),
                "v04s_descent_margin_N": float(v04s_row["thrust_margin_descent_N"]),
                "v05r_raw_min_thrust_margin_N": float(
                    v05r_row["raw_min_thrust_margin_N"]
                ),
                "v05q2_raw_all_segment_min_thrust_margin_N": float(
                    v05r_row["raw_all_segment_min_thrust_margin_N"]
                ),
                "v05q2_approach_only_corrected_margin_N": approach_only_margin_N,
                "v05q2_corrected_all_segment_min_margin_N": all_segment_margin_N,
                "v05q2_non_approach_min_thrust_margin_N": float(
                    v05r_row["non_approach_min_thrust_margin_N"]
                ),
                "v05r_corrected_approach_min_thrust_margin_N": float(
                    v05r_row["corrected_approach_min_thrust_margin_N"]
                ),
                "margin_difference_v05r_minus_v04s_N": difference_N,
                "margin_difference_q2_approach_only_minus_v04s_N": difference_N,
                "all_segment_minus_approach_only_N": (
                    all_segment_margin_N - approach_only_margin_N
                ),
                "v04s_conclusion_flag": str(v04s_row["conclusion_flag"]),
                "v05r_conclusion_status_corrected": str(
                    v05r_row["conclusion_status_approach_corrected"]
                ),
                "v05q2_conclusion_status_all_segment_corrected": str(
                    v05r_row["conclusion_status_all_segment_corrected"]
                ),
                "consistency_flag": (
                    "consistent"
                    if abs(difference_N) < 1000.0
                    else "inconsistent_requires_diagnosis"
                ),
            }
        )
    return pd.DataFrame(rows)


def _input_decomposition(
    summary: pd.DataFrame,
    best: pd.DataFrame,
    records: dict[str, CaseRecord],
) -> pd.DataFrame:
    selected_cases = [
        ("nominal_baseline", "V05-0001_baseline"),
        ("nominal_adaptive", "V05-0001_adaptive"),
        ("nominal_hybrid", "V05-0001_hybrid"),
        ("top_candidate", str(best.iloc[0]["case_id"])),
    ]
    hybrid = summary[summary["propulsion_case"] == HYBRID_CASE].copy()
    best_hybrid_unmet = hybrid.sort_values(
        by=[
            "unmet_electric_load_Wh",
            "approach_only_corrected_margin_N",
            "mission_fuel_kg",
        ],
        ascending=[True, False, True],
    ).iloc[0]
    best_hybrid_margin = hybrid.sort_values(
        by=[
            "approach_only_corrected_margin_N",
            "unmet_electric_load_Wh",
            "mission_fuel_kg",
        ],
        ascending=[False, True, True],
    ).iloc[0]
    selected_cases.extend(
        [
            ("best_hybrid_min_unmet_load", str(best_hybrid_unmet["case_id"])),
            ("best_hybrid_corrected_margin", str(best_hybrid_margin["case_id"])),
        ]
    )

    rows = []
    for selection_label, case_id in selected_cases:
        record = records[case_id]
        summary_row = summary[summary["case_id"] == case_id].iloc[0]
        rows.append(_approach_decomposition_row(record, summary_row, selection_label))
    return pd.DataFrame(rows)


def _engine_thrust_monotonicity(
    summary: pd.DataFrame,
    records: dict[str, CaseRecord],
) -> pd.DataFrame:
    rows = []
    case_ids_by_thrust = {
        115000.0: {
            BASELINE_FIXED_CASE: "V05-0001_baseline",
            ADAPTIVE_CASE: "V05-0001_adaptive",
            HYBRID_CASE: "V05-0001_hybrid",
        },
        130000.0: {
            BASELINE_FIXED_CASE: "V05-0002_baseline",
            ADAPTIVE_CASE: "V05-0002_adaptive",
            HYBRID_CASE: "V05-0002_hybrid",
        },
        150000.0: {
            BASELINE_FIXED_CASE: "V05-0003_baseline",
            ADAPTIVE_CASE: "V05-0003_adaptive",
            HYBRID_CASE: "V05-0003_hybrid",
        },
    }
    for propulsion_case in (BASELINE_FIXED_CASE, ADAPTIVE_CASE, HYBRID_CASE):
        previous: dict[str, Any] | None = None
        for thrust in (115000.0, 130000.0, 150000.0):
            case_id = case_ids_by_thrust[thrust][propulsion_case]
            row = _approach_decomposition_row(
                records[case_id],
                summary[summary["case_id"] == case_id].iloc[0],
                "engine_thrust_monotonicity",
            )
            monotonicity_flag = "reference"
            failure_cause = ""
            if previous is not None:
                monotonicity_flag, failure_cause = _monotonicity_result(previous, row)
            rows.append(
                {
                    "propulsion_case": propulsion_case,
                    "engine_static_thrust_N_per_engine": thrust,
                    "estimated_mtow_kg": row["estimated_mtow_kg"],
                    "available_thrust_N": row["available_thrust_N"],
                    "required_thrust_descent_N": row["required_thrust_descent_N"],
                    "corrected_margin_N": row["corrected_margin_N"],
                    "mission_fuel_kg": float(
                        summary[summary["case_id"] == case_id].iloc[0][
                            "mission_fuel_kg"
                        ]
                    ),
                    "monotonicity_flag": monotonicity_flag,
                    "failure_cause": failure_cause,
                }
            )
            previous = row
    return pd.DataFrame(rows)


def _approach_decomposition_row(
    record: CaseRecord,
    summary_row: pd.Series,
    selection_label: str,
) -> dict[str, Any]:
    segment = next(
        item
        for item in record.result.segment_results
        if item.segment_name == "approach_landing"
    )
    aero_config = record.configs["aero"]
    atmosphere, aero_performance, drag_N = _approach_drag_components(
        segment,
        aero_config,
    )
    approach_config = record.configs["mission_solver"]["approach_landing_model"]
    gamma_deg = float(approach_config["default_descent_angle_deg"])
    altitude_m = 0.5 * (segment.altitude_start_m + segment.altitude_end_m)
    force_balance = evaluate_approach_force_balance(
        ApproachForceBalanceInput(
            case_name=record.result.case_name,
            segment_name=segment.segment_name,
            weight_N=kg_to_N(segment.start_mass_kg),
            speed_mps=float(segment.speed_mps or 0.0),
            altitude_m=altitude_m,
            gamma_deg=gamma_deg,
            drag_N=drag_N,
            available_thrust_N=segment.available_thrust_N,
            electric_thrust_proxy_N=segment.electric_thrust_proxy_N,
            include_weight_component_along_path=bool(
                approach_config["include_weight_component_along_path"]
            ),
        )
    )
    return {
        "selection_label": selection_label,
        "case_id": record.case_id,
        "propulsion_case": record.result.case_name,
        "changed_parameter": record.changed_parameter,
        "changed_value": record.changed_value,
        "weight_kg": segment.start_mass_kg,
        "weight_N": kg_to_N(segment.start_mass_kg),
        "speed_mps": float(segment.speed_mps or 0.0),
        "altitude_m": altitude_m,
        "gamma_deg": gamma_deg,
        "density_kg_m3": atmosphere.density_kg_m3,
        "wing_area_m2": float(aero_config["aero"]["default"]["wing_area_m2"]),
        "cl": aero_performance.cl,
        "cd": aero_performance.cd,
        "ld_ratio": aero_performance.ld_ratio,
        "drag_N": drag_N,
        "weight_component_along_path_N": (
            force_balance.weight_component_along_path_N
        ),
        "required_thrust_level_flight_N": (
            force_balance.required_thrust_level_flight_N
        ),
        "required_thrust_descent_N": force_balance.required_thrust_descent_N,
        "available_thrust_N": force_balance.available_thrust_N,
        "electric_thrust_proxy_N": force_balance.electric_thrust_proxy_N,
        "net_required_thrust_after_electric_N": (
            force_balance.net_required_thrust_after_electric_N
        ),
        "corrected_margin_N": force_balance.thrust_margin_descent_N,
        "v05r_reported_corrected_min_margin_N": float(
            summary_row["corrected_approach_min_thrust_margin_N"]
        ),
        "v05q2_approach_only_corrected_margin_N": float(
            summary_row["approach_only_corrected_margin_N"]
        ),
        "v05q2_corrected_all_segment_min_margin_N": float(
            summary_row["corrected_all_segment_min_thrust_margin_N"]
        ),
        "v05q2_non_approach_min_thrust_margin_N": float(
            summary_row["non_approach_min_thrust_margin_N"]
        ),
        "approach_margin_minus_v05r_reported_min_N": (
            force_balance.thrust_margin_descent_N
            - float(summary_row["corrected_approach_min_thrust_margin_N"])
        ),
        "approach_margin_minus_v05q2_approach_only_N": (
            force_balance.thrust_margin_descent_N
            - float(summary_row["approach_only_corrected_margin_N"])
        ),
        "q2_all_segment_minus_approach_only_N": (
            float(summary_row["corrected_all_segment_min_thrust_margin_N"])
            - float(summary_row["approach_only_corrected_margin_N"])
        ),
        "raw_margin_N": segment.thrust_margin_N,
        "fuel_kg": record.result.weight_breakdown.fuel_kg,
        "estimated_mtow_kg": record.result.weight_breakdown.estimated_mtow_kg,
        "engine_static_thrust_N_per_engine": _engine_static_thrust(record),
        "engine_rating": segment.engine_rating,
        "approach_drag_multiplier": 1.0,
        "approach_rating_throttle_multiplier": 1.0,
        "unmet_electric_load_Wh": segment.unmet_electric_load_Wh,
        "conclusion_flag": _decomposition_conclusion(force_balance, summary_row),
    }


def _approach_drag_components(segment, aero_config: dict[str, Any]):
    altitude_m = 0.5 * (segment.altitude_start_m + segment.altitude_end_m)
    atmosphere = isa_atmosphere(altitude_m)
    speed_mps = float(segment.speed_mps or 0.0)
    mach = speed_mps / atmosphere.speed_of_sound_mps
    wing_area_m2 = float(aero_config["aero"]["default"]["wing_area_m2"])
    blowing = aero_config["aero"]["blowing"]
    c_mu = min(
        max(segment.blowing_momentum_coefficient, 0.0),
        float(blowing["cmu_max_for_v02"]),
    )
    performance = AeroModel.from_config(aero_config).evaluate(
        AeroState(
            mach=mach,
            altitude_m=altitude_m,
            weight_N=kg_to_N(segment.start_mass_kg),
            wing_area_m2=wing_area_m2,
            flap_mode="landing_flap",
            gear_down=True,
            blowing_momentum_coefficient=c_mu,
        ),
        atmosphere,
    )
    dynamic_pressure_Pa = 0.5 * atmosphere.density_kg_m3 * speed_mps**2
    drag_N = dynamic_pressure_Pa * wing_area_m2 * performance.cd
    return atmosphere, performance, drag_N


def _engine_static_thrust(record: CaseRecord) -> float:
    key = (
        "baseline_fixed_cycle"
        if record.result.case_name == BASELINE_FIXED_CASE
        else "adaptive_cycle"
    )
    return float(
        record.configs["engine"]["engine_surrogate"][key][
            "sea_level_static_thrust_N_per_engine"
        ]
    )


def _decomposition_conclusion(force_balance, summary_row: pd.Series) -> str:
    if "validated" in str(summary_row.get("conclusion_status_approach_corrected", "")):
        return "invalid_validated_label"
    if force_balance.thrust_margin_descent_N >= 0.0:
        return "approach_margin_positive_but_other_segment_may_limit"
    return force_balance.conclusion_flag


def _monotonicity_result(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> tuple[str, str]:
    available_ok = current["available_thrust_N"] >= previous["available_thrust_N"] - 1e-6
    margin_ok = current["corrected_margin_N"] >= previous["corrected_margin_N"] - 1e-6
    if available_ok and margin_ok:
        return "pass", ""
    if current["engine_static_thrust_N_per_engine"] <= previous[
        "engine_static_thrust_N_per_engine"
    ]:
        return "fail", "override not applied"
    if not available_ok:
        return "fail", "available thrust calculation not using override"
    if current["weight_kg"] > previous["weight_kg"] or current["drag_N"] > previous["drag_N"]:
        return "fail", "weight increase"
    return "fail", "other"


def _audit_summary(
    nominal_replay: pd.DataFrame,
    monotonicity: pd.DataFrame,
) -> pd.DataFrame:
    nominal_inconsistent = int(
        (nominal_replay["consistency_flag"] == "inconsistent_requires_diagnosis").sum()
    )
    monotonicity_fails = monotonicity[monotonicity["monotonicity_flag"] == "fail"]
    recommended = _recommended_next_action(nominal_replay, monotonicity)
    rows = [
        (
            "nominal_replay_consistent_count",
            int((nominal_replay["consistency_flag"] == "consistent").sum()),
            "nominal V0.2-04S descent margin matches V0.2-05Q2 approach-only margin within 1000 N",
        ),
        (
            "nominal_replay_inconsistent_count",
            nominal_inconsistent,
            "nominal rows where V0.2-05Q2 approach-only margin does not replay V0.2-04S approach-only margin",
        ),
        (
            "thrust_monotonicity_pass_count",
            int((monotonicity["monotonicity_flag"] == "pass").sum()),
            "non-reference thrust steps where available thrust and corrected approach margin do not worsen",
        ),
        (
            "thrust_monotonicity_fail_count",
            int(len(monotonicity_fails)),
            "non-reference thrust steps where monotonicity fails",
        ),
        (
            "suspected_override_application_issue_count",
            int((monotonicity_fails["failure_cause"] == "override not applied").sum()),
            "monotonicity failures suggesting thrust override did not propagate",
        ),
        (
            "suspected_available_thrust_issue_count",
            int(
                (
                    monotonicity_fails["failure_cause"]
                    == "available thrust calculation not using override"
                ).sum()
            ),
            "monotonicity failures suggesting available-thrust calculation mismatch",
        ),
        (
            "suspected_weight_or_drag_explanation_count",
            int((monotonicity_fails["failure_cause"] == "weight increase").sum()),
            "monotonicity failures explained by weight or drag increases",
        ),
        (
            "suspected_classification_field_mismatch_count",
            nominal_inconsistent,
            "post-Q2 count of nominal approach-only field mismatches against V0.2-04S",
        ),
        (
            "recommended_next_action",
            recommended,
            "next action before report ingestion or V0.2-05Q2 acceptance",
        ),
    ]
    return pd.DataFrame(
        [
            {
                "metric": metric,
                "value": value,
                "explanation": explanation,
                "recommended_next_action": recommended if metric == "recommended_next_action" else "",
            }
            for metric, value, explanation in rows
        ]
    )


def _recommended_next_action(
    nominal_replay: pd.DataFrame,
    monotonicity: pd.DataFrame,
) -> str:
    has_nominal_inconsistency = (
        nominal_replay["consistency_flag"] == "inconsistent_requires_diagnosis"
    ).any()
    has_monotonicity_fail = (monotonicity["monotonicity_flag"] == "fail").any()
    if has_nominal_inconsistency:
        return (
            "V0.2-05Q2 repair required: split approach-only corrected margin from "
            "all-segment corrected minimum before report ingestion."
        )
    if has_monotonicity_fail:
        return "Investigate thrust override propagation before report ingestion."
    return "Internal consistency audit passes; report ingestion can proceed with diagnostic labels."


def _plot_nominal_replay(
    nominal_replay: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=140)
    x = range(len(nominal_replay))
    width = 0.36
    ax.bar(
        [item - width / 2 for item in x],
        nominal_replay["v04s_descent_margin_N"],
        width,
        label="V0.2-04S approach margin",
    )
    ax.bar(
        [item + width / 2 for item in x],
        nominal_replay["v05r_corrected_approach_min_thrust_margin_N"],
        width,
        label="V0.2-05Q2 approach-only margin",
    )
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xticks(list(x), nominal_replay["propulsion_case"], rotation=20)
    ax.set_xlabel("Propulsion case")
    ax.set_ylabel("Thrust margin (N)")
    ax.set_title("V0.2-04S vs V0.2-05Q2 Nominal Approach Replay")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize="small")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "v04s_vs_v05r_margin_replay.png",
        svg_dir / "v04s_vs_v05r_margin_replay.svg",
    )
    plt.close(fig)


def _plot_monotonicity(
    monotonicity: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=140)
    for propulsion_case, group in monotonicity.groupby("propulsion_case"):
        ordered = group.sort_values("engine_static_thrust_N_per_engine")
        ax.plot(
            ordered["engine_static_thrust_N_per_engine"],
            ordered["corrected_margin_N"],
            marker="o",
            label=propulsion_case,
        )
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xlabel("Sea-level static thrust per engine (N)")
    ax.set_ylabel("Corrected approach margin (N)")
    ax.set_title("Engine Thrust Monotonicity Audit")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize="small")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "engine_thrust_monotonicity_audit.png",
        svg_dir / "engine_thrust_monotonicity_audit.svg",
    )
    plt.close(fig)


def _save_figure(fig, png_path: Path, svg_path: Path) -> None:
    fig.savefig(png_path)
    fig.savefig(svg_path)
    _strip_trailing_whitespace(svg_path)


def _strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def _case_slug(case_name: str) -> str:
    return {
        BASELINE_FIXED_CASE: "baseline",
        ADAPTIVE_CASE: "adaptive",
        HYBRID_CASE: "hybrid",
    }.get(case_name, case_name.replace("_", "-"))


def _changed_parameter_text(settings: dict[str, float]) -> tuple[str, str]:
    if not settings:
        return "baseline", "baseline"
    if len(settings) == 1:
        key, value = next(iter(settings.items()))
        return key, str(value)
    return "selected_grid", _settings_summary(settings)


def _settings_summary(settings: dict[str, float]) -> str:
    if not settings:
        return "baseline"
    return ";".join(f"{key}={value:g}" for key, value in sorted(settings.items()))


if __name__ == "__main__":
    main()
