"""Generate V0.2-04 segmented mission solver proxy outputs."""

from dataclasses import asdict
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


SIM_ROOT = Path(__file__).resolve().parents[1]
if str(SIM_ROOT) not in sys.path:
    sys.path.insert(0, str(SIM_ROOT))

from mta_vhep.core.atmosphere import isa_atmosphere  # noqa: E402
from mta_vhep.core.units import Wh_to_J, kg_to_N  # noqa: E402
from mta_vhep.interfaces.csv_export import write_dataframe_csv  # noqa: E402
from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml  # noqa: E402
from mta_vhep.mission.mission_solver import MissionResult, SegmentedMissionSolver  # noqa: E402
from mta_vhep.mission.takeoff_landing import (  # noqa: E402
    landing_performance_proxy,
    takeoff_performance_proxy,
)
from mta_vhep.propulsion.fuel import get_fuel  # noqa: E402


def main() -> None:
    """Run the V0.2-04 concept segmented mission solver and export artifacts."""
    config_dir = SIM_ROOT / "config"
    project_config = load_project_config(config_dir)
    fuel = get_fuel(load_fuel_database(config_dir), "Jet-A")
    mission_solver_config = load_yaml(config_dir / "mission_solver.yaml")
    aero_config = load_yaml(config_dir / "aero_model.yaml")
    propulsion_config = load_yaml(config_dir / "propulsion.yaml")
    engine_config = load_yaml(config_dir / "engine_surrogate.yaml")
    hybrid_config = load_yaml(config_dir / "hybrid_electric.yaml")

    solver = SegmentedMissionSolver(
        project_config=project_config,
        mission_solver_config=mission_solver_config,
        aero_config=aero_config,
        propulsion_config=propulsion_config,
        engine_config=engine_config,
        hybrid_config=hybrid_config,
        fuel=fuel,
    )
    results = solver.run_all_cases()

    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

    segment_table = _mission_segments_table(results)
    summary_table = _mission_summary_table(results)
    weight_table = _weight_breakdown_table(results)
    diagnostics_table = _mission_diagnostics_table(results)
    case_status_table = _mission_case_status_table(results, diagnostics_table)
    constraints_table = _constraint_violations_table(results)
    proxy_table, proxy_components_table = _takeoff_landing_proxy_tables(results, aero_config)

    write_dataframe_csv(segment_table, csv_dir / "mission_segments.csv")
    write_dataframe_csv(summary_table, csv_dir / "mission_summary.csv")
    write_dataframe_csv(weight_table, csv_dir / "weight_breakdown.csv")
    write_dataframe_csv(diagnostics_table, csv_dir / "mission_diagnostics.csv")
    write_dataframe_csv(case_status_table, csv_dir / "mission_case_status.csv")
    write_dataframe_csv(constraints_table, csv_dir / "mission_constraint_violations.csv")
    write_dataframe_csv(proxy_table, csv_dir / "takeoff_landing_proxy.csv")
    write_dataframe_csv(
        proxy_components_table,
        csv_dir / "takeoff_landing_proxy_components.csv",
    )

    _plot_mission_profile(segment_table, png_dir, svg_dir)
    _plot_fuel_burn(summary_table, png_dir, svg_dir)
    _plot_energy_breakdown(summary_table, fuel.lower_heating_value_J_per_kg, png_dir, svg_dir)
    _plot_takeoff_proxy(proxy_table, png_dir, svg_dir)
    _plot_constraint_status(case_status_table, png_dir, svg_dir)

    print("MTA-VHEP V0.2-04 Segmented Mission Solver Summary")
    print("Concept-level segmented mission solver; no certified range or fuel-burn claim.")
    print(f"Mission cases: {', '.join(summary_table['case_name'])}")
    print(f"Segment rows: {len(segment_table)}")
    print(f"Summary rows: {len(summary_table)}")
    print(f"Diagnostics rows: {len(diagnostics_table)}")
    print(f"Wrote: {csv_dir / 'mission_segments.csv'}")
    print(f"Wrote: {csv_dir / 'mission_summary.csv'}")


def _mission_segments_table(results: list[MissionResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        for segment in result.segment_results:
            row = asdict(segment)
            row["constraint_flags"] = ";".join(segment.constraint_flags)
            rows.append(row)
    return pd.DataFrame(rows)


def _mission_summary_table(results: list[MissionResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append(
            {
                "case_name": result.case_name,
                "block_fuel_kg": result.block_fuel_kg,
                "reserve_fuel_kg": result.reserve_fuel_kg,
                "mission_fuel_kg": result.mission_fuel_kg,
                "start_mass_kg": result.start_mass_kg,
                "final_mass_kg": result.final_mass_kg,
                "final_fuel_kg": result.final_fuel_kg,
                "electric_energy_Wh": result.electric_energy_Wh,
                "max_electric_power_W": result.max_electric_power_W,
                "max_thermal_load_W": result.max_thermal_load_W,
                "constraint_violations": ";".join(result.constraint_violations),
            }
        )
    return pd.DataFrame(rows)


def _weight_breakdown_table(results: list[MissionResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        row = asdict(result.weight_breakdown)
        row["case_name"] = result.case_name
        rows.append(row)
    return pd.DataFrame(rows)


def _mission_diagnostics_table(results: list[MissionResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        for segment in result.segment_results:
            required_thrust_N = segment.average_required_thrust_N
            thrust_margin_ratio = (
                segment.thrust_margin_N / required_thrust_N
                if required_thrust_N > 0.0
                else 0.0
            )
            rows.append(
                {
                    "case_name": result.case_name,
                    "segment_name": segment.segment_name,
                    "segment_type": segment.segment_type,
                    "required_thrust_N": required_thrust_N,
                    "available_thrust_N": segment.available_thrust_N,
                    "thrust_margin_N": segment.thrust_margin_N,
                    "thrust_margin_ratio": thrust_margin_ratio,
                    "fuel_burn_kg": segment.fuel_burn_kg,
                    "electric_energy_Wh": segment.electric_energy_Wh,
                    "soc_start": segment.soc_start,
                    "soc_end": segment.soc_end,
                    "unmet_electric_load_Wh": segment.unmet_electric_load_Wh,
                    "constraint_flags": ";".join(segment.constraint_flags),
                }
            )
    return pd.DataFrame(rows)


def _mission_case_status_table(
    results: list[MissionResult],
    diagnostics_table: pd.DataFrame,
) -> pd.DataFrame:
    baseline_fuel = next(
        result.mission_fuel_kg
        for result in results
        if result.case_name == "baseline_fixed_cycle_turbofan"
    )
    rows = []
    for result in results:
        case_diagnostics = diagnostics_table[
            diagnostics_table["case_name"] == result.case_name
        ]
        positive_required = case_diagnostics[
            case_diagnostics["required_thrust_N"] > 0.0
        ]
        if positive_required.empty:
            min_margin_row = case_diagnostics.iloc[0]
        else:
            min_margin_row = positive_required.sort_values("thrust_margin_N").iloc[0]

        has_low_thrust_margin = "low_thrust_margin" in result.constraint_violations
        has_unmet_electric_load = "unmet_electric_load" in result.constraint_violations
        major_constraint = has_low_thrust_margin or has_unmet_electric_load
        if major_constraint:
            conclusion_status = "diagnostic_only_constraint_flagged"
        else:
            conclusion_status = "candidate_for_sensitivity_study"

        rows.append(
            {
                "case_name": result.case_name,
                "computational_success": True,
                "has_low_thrust_margin": has_low_thrust_margin,
                "has_unmet_electric_load": has_unmet_electric_load,
                "estimated_mtow_kg": result.weight_breakdown.estimated_mtow_kg,
                "mtow_initial_kg": result.weight_breakdown.mtow_initial_kg,
                "mtow_range_upper_kg": result.weight_breakdown.mtow_range_upper_kg,
                "mtow_margin_to_initial_kg": (
                    result.weight_breakdown.mtow_margin_to_initial_kg
                ),
                "mtow_margin_to_upper_kg": result.weight_breakdown.mtow_margin_to_upper_kg,
                "within_v01_mtow_range": result.weight_breakdown.within_v01_mtow_range,
                "mission_fuel_kg": result.mission_fuel_kg,
                "apparent_fuel_delta_vs_baseline_pct": (
                    (result.mission_fuel_kg - baseline_fuel) / baseline_fuel * 100.0
                ),
                "minimum_thrust_margin_N": float(min_margin_row["thrust_margin_N"]),
                "minimum_thrust_margin_ratio": float(
                    min_margin_row["thrust_margin_ratio"]
                ),
                "minimum_thrust_margin_segment": str(min_margin_row["segment_name"]),
                "conclusion_status": conclusion_status,
            }
        )
    return pd.DataFrame(rows)


def _constraint_violations_table(results: list[MissionResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        for segment in result.segment_results:
            for flag in segment.constraint_flags:
                value, threshold, explanation = _violation_details(segment, flag)
                rows.append(
                    {
                        "case_name": result.case_name,
                        "segment_name": segment.segment_name,
                        "violation_type": flag,
                        "value": value,
                        "threshold": threshold,
                        "explanation": explanation,
                    }
                )
    return pd.DataFrame(
        rows,
        columns=(
            "case_name",
            "segment_name",
            "violation_type",
            "value",
            "threshold",
            "explanation",
        ),
    )


def _violation_details(segment, flag: str) -> tuple[float, float, str]:
    if flag == "low_thrust_margin":
        return (
            segment.thrust_margin_N,
            0.0,
            "available thrust is below required thrust in this mission segment",
        )
    if flag == "unmet_electric_load":
        peak_unmet_W = (
            segment.unmet_electric_load_Wh * 3600.0 / segment.duration_s
            if segment.duration_s > 0.0
            else 0.0
        )
        return (
            segment.unmet_electric_load_Wh,
            0.0,
            f"electric load not met; peak unmet load proxy {peak_unmet_W:.1f} W",
        )
    return (1.0, 0.0, "constraint flag emitted by concept mission solver")


def _takeoff_landing_proxy_tables(
    results: list[MissionResult],
    aero_config: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    atmosphere = isa_atmosphere(0.0)
    wing_area_m2 = aero_config["aero"]["default"]["wing_area_m2"]
    takeoff_clmax = aero_config["aero"]["clmax"]["takeoff_flap"]
    landing_clmax = aero_config["aero"]["clmax"]["landing_flap"]
    blowing = aero_config["aero"]["blowing"]
    rows = []
    component_rows = []
    for result in results:
        takeoff_segment = _segment_by_type(result, "takeoff")
        approach_segment = _segment_by_type(result, "approach")
        takeoff_clmax_effective = _effective_clmax(
            takeoff_clmax,
            takeoff_segment.blowing_momentum_coefficient,
            blowing,
        )
        landing_clmax_effective = _effective_clmax(
            landing_clmax,
            approach_segment.blowing_momentum_coefficient,
            blowing,
        )
        takeoff_proxy = takeoff_performance_proxy(
            weight_N=kg_to_N(takeoff_segment.start_mass_kg),
            density_kg_m3=atmosphere.density_kg_m3,
            wing_area_m2=wing_area_m2,
            clmax=takeoff_clmax_effective,
            effective_thrust_N=takeoff_segment.available_thrust_N,
        )
        landing_proxy = landing_performance_proxy(
            weight_N=kg_to_N(approach_segment.end_mass_kg),
            density_kg_m3=atmosphere.density_kg_m3,
            wing_area_m2=wing_area_m2,
            clmax=landing_clmax_effective,
            effective_thrust_N=approach_segment.available_thrust_N,
        )
        rows.append(
            {
                "case_name": result.case_name,
                "takeoff_proxy_index": takeoff_proxy.field_length_index,
                "landing_proxy_index": landing_proxy.field_length_index,
                "takeoff_clmax": takeoff_proxy.clmax,
                "landing_clmax": landing_proxy.clmax,
                "takeoff_effective_thrust_N": takeoff_segment.available_thrust_N,
                "landing_effective_thrust_N": approach_segment.available_thrust_N,
                "note": "proxy_indicator_not_certified_field_length",
            }
        )
        component_rows.append(
            {
                "case_name": result.case_name,
                "weight_kg": takeoff_segment.start_mass_kg,
                "density_kg_m3": atmosphere.density_kg_m3,
                "wing_area_m2": wing_area_m2,
                "clmax_effective": takeoff_clmax_effective,
                "effective_thrust_N": takeoff_segment.available_thrust_N,
                "electric_thrust_proxy_N": takeoff_segment.electric_thrust_proxy_N,
                "hybrid_mass_penalty_kg": result.weight_breakdown.hybrid_total_mass_kg,
                "takeoff_proxy_index": takeoff_proxy.field_length_index,
                "landing_proxy_index": landing_proxy.field_length_index,
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(component_rows)


def _effective_clmax(base_clmax: float, c_mu_proxy: float, blowing: dict) -> float:
    cmu = min(max(c_mu_proxy, 0.0), blowing["cmu_max_for_v02"])
    return base_clmax + blowing["clmax_increment_per_cmu"] * cmu


def _segment_by_type(result: MissionResult, segment_type: str):
    for segment in result.segment_results:
        if segment.segment_type == segment_type:
            return segment
    raise ValueError(f"Missing segment type: {segment_type}")


def _plot_mission_profile(
    segment_table: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    first_case = segment_table["case_name"].iloc[0]
    case_segments = segment_table[segment_table["case_name"] == first_case]
    x = [0.0]
    y = [float(case_segments.iloc[0]["altitude_start_m"])]
    cumulative = 0.0
    for _, row in case_segments.iterrows():
        cumulative += float(row["distance_km"])
        x.append(cumulative)
        y.append(float(row["altitude_end_m"]))

    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.plot(x, y, marker="o")
    ax.set_xlabel("Cumulative distance (km)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Mission Altitude Profile")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save_figure(fig, png_dir / "mission_profile.png", svg_dir / "mission_profile.svg")
    plt.close(fig)


def _plot_fuel_burn(summary_table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.bar(summary_table["case_name"], summary_table["block_fuel_kg"])
    ax.set_xlabel("Mission case")
    ax.set_ylabel("Block fuel model output (kg)")
    ax.set_title("Concept Mission Fuel Burn")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "fuel_burn_comparison.png",
        svg_dir / "fuel_burn_comparison.svg",
    )
    plt.close(fig)


def _plot_energy_breakdown(
    summary_table: pd.DataFrame,
    fuel_lhv_J_per_kg: float,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    fuel_energy_GJ = summary_table["mission_fuel_kg"] * fuel_lhv_J_per_kg / 1.0e9
    electric_energy_GJ = summary_table["electric_energy_Wh"].apply(Wh_to_J) / 1.0e9
    x = range(len(summary_table))
    width = 0.36
    ax.bar([item - width / 2 for item in x], fuel_energy_GJ, width, label="Fuel")
    ax.bar([item + width / 2 for item in x], electric_energy_GJ, width, label="Electric")
    ax.set_xticks(list(x), summary_table["case_name"], rotation=20)
    ax.set_xlabel("Mission case")
    ax.set_ylabel("Energy model output (GJ)")
    ax.set_title("Mission Energy Breakdown")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "mission_energy_breakdown.png",
        svg_dir / "mission_energy_breakdown.svg",
    )
    plt.close(fig)


def _plot_takeoff_proxy(proxy_table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.bar(proxy_table["case_name"], proxy_table["takeoff_proxy_index"])
    ax.set_xlabel("Mission case")
    ax.set_ylabel("Takeoff proxy index (-)")
    ax.set_title("Takeoff Proxy Comparison")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "takeoff_proxy_comparison.png",
        svg_dir / "takeoff_proxy_comparison.svg",
    )
    plt.close(fig)


def _plot_constraint_status(
    case_status_table: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    colors = [
        "#d62728" if flag else "#2ca02c"
        for flag in case_status_table["has_low_thrust_margin"]
    ]
    ax.bar(
        case_status_table["case_name"],
        case_status_table["minimum_thrust_margin_N"],
        color=colors,
    )
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xlabel("Mission case")
    ax.set_ylabel("Minimum thrust margin (N)")
    ax.set_title("Mission Constraint Status")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "mission_constraint_status.png",
        svg_dir / "mission_constraint_status.svg",
    )
    plt.close(fig)


def _save_figure(fig, png_path: Path, svg_path: Path) -> None:
    fig.savefig(png_path)
    fig.savefig(svg_path)
    _strip_trailing_whitespace(svg_path)


def _strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
