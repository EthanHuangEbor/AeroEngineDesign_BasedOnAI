"""Run V0.2-05 concept sensitivity analysis and candidate screening."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


SIM_ROOT = Path(__file__).resolve().parents[1]
if str(SIM_ROOT) not in sys.path:
    sys.path.insert(0, str(SIM_ROOT))

from mta_vhep.analysis.sensitivity import SensitivityRunner  # noqa: E402
from mta_vhep.interfaces.csv_export import write_dataframe_csv  # noqa: E402
from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml  # noqa: E402
from mta_vhep.propulsion.fuel import get_fuel  # noqa: E402


def main() -> None:
    """Run configured V0.2-05 sensitivity cases and export CSV/figure outputs."""
    config_dir = SIM_ROOT / "config"
    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

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
    tables = runner.run()

    summary = tables["summary"]
    details = tables["details"]
    constraints = tables["constraints"]
    best = tables["best_candidates"]
    tornado = tables["tornado"]
    corrected_constraint_summary = tables["corrected_constraint_summary"]
    approach_classification = tables["approach_classification"]
    field_semantics = tables["field_semantics"]
    feasibility_reclassified = tables["feasibility_reclassified"]
    non_approach_constraints = tables["non_approach_constraints"]

    write_dataframe_csv(summary, csv_dir / "sensitivity_summary.csv")
    write_dataframe_csv(details, csv_dir / "sensitivity_case_details.csv")
    write_dataframe_csv(constraints, csv_dir / "sensitivity_constraints.csv")
    write_dataframe_csv(best, csv_dir / "sensitivity_best_candidates.csv")
    write_dataframe_csv(tornado, csv_dir / "sensitivity_tornado_data.csv")
    write_dataframe_csv(
        corrected_constraint_summary,
        csv_dir / "sensitivity_corrected_constraint_summary.csv",
    )
    write_dataframe_csv(
        approach_classification,
        csv_dir / "sensitivity_approach_classification.csv",
    )
    write_dataframe_csv(
        field_semantics,
        csv_dir / "sensitivity_field_semantics_audit.csv",
    )
    write_dataframe_csv(
        feasibility_reclassified,
        csv_dir / "sensitivity_feasibility_reclassified.csv",
    )
    write_dataframe_csv(
        non_approach_constraints,
        csv_dir / "sensitivity_non_approach_constraints.csv",
    )

    merged = summary.merge(details, on=["case_id", "case_family", "propulsion_case"], how="left")
    _plot_constraint_tornado(tornado, png_dir, svg_dir)
    _plot_pareto_fuel_vs_mtow(summary, png_dir, svg_dir)
    _plot_thrust_margin_vs_engine_rating(summary, png_dir, svg_dir)
    _plot_hybrid_power_sizing_map(merged, png_dir, svg_dir)
    _plot_takeoff_proxy_sensitivity(merged, png_dir, svg_dir)
    _plot_corrected_constraint_feasibility_map(summary, png_dir, svg_dir)
    _plot_raw_vs_corrected_thrust_margin(summary, png_dir, svg_dir)
    _plot_approach_model_sensitivity_classification(
        corrected_constraint_summary,
        png_dir,
        svg_dir,
    )
    _plot_approach_only_vs_all_segment_margin(summary, png_dir, svg_dir)
    _plot_sensitivity_feasibility_reclassified(summary, png_dir, svg_dir)
    _plot_non_approach_constraint_drivers(non_approach_constraints, png_dir, svg_dir)

    raw_low_thrust_cases = int(summary["raw_low_thrust_margin"].sum())
    approach_only_low_thrust_cases = int(
        summary["approach_only_corrected_low_thrust_margin"].sum()
    )
    all_segment_corrected_low_thrust_cases = int(
        summary["corrected_all_segment_low_thrust_margin"].sum()
    )
    approach_model_sensitive_cases = int(
        summary["approach_only_model_sensitive"].sum()
    )
    sizing_or_schedule_cases = int(summary["sizing_or_schedule_low_thrust"].sum())
    unmet_cases = int(summary["unmet_electric_load"].sum())
    approach_corrected_feasible_cases = int(
        summary["feasible_basic_approach_corrected"].sum()
    )
    all_segment_corrected_feasible_cases = int(
        summary["feasible_basic_all_segment_corrected"].sum()
    )

    print("MTA-VHEP V0.2-05 Sensitivity Analysis Summary")
    print("Concept-level screening only; no validated design or certified performance claim.")
    print(f"Sensitivity case rows: {len(summary)}")
    print(f"Rows with raw low thrust margin: {raw_low_thrust_cases}")
    print(f"Rows with approach-only corrected low thrust margin: {approach_only_low_thrust_cases}")
    print(
        "Rows with all-segment corrected low thrust margin: "
        f"{all_segment_corrected_low_thrust_cases}"
    )
    print(f"Rows classified approach-model-sensitive: {approach_model_sensitive_cases}")
    print(f"Rows classified sizing/schedule low thrust: {sizing_or_schedule_cases}")
    print(f"Rows with unmet electric load: {unmet_cases}")
    print(f"Rows passing approach-only corrected screen: {approach_corrected_feasible_cases}")
    print(
        "Rows passing all-segment corrected screen: "
        f"{all_segment_corrected_feasible_cases}"
    )
    print(f"Best-candidate rows: {len(best)}")
    print(f"Wrote: {csv_dir / 'sensitivity_summary.csv'}")
    print(f"Wrote: {csv_dir / 'sensitivity_best_candidates.csv'}")


def _plot_constraint_tornado(
    tornado: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=140)
    if tornado.empty:
        ax.text(0.5, 0.5, "No tornado data", ha="center", va="center")
        ax.set_axis_off()
    else:
        plot_data = (
            tornado.groupby("changed_parameter", as_index=False)["max_abs_fuel_delta_pct"]
            .max()
            .sort_values("max_abs_fuel_delta_pct")
            .tail(10)
        )
        ax.barh(plot_data["changed_parameter"], plot_data["max_abs_fuel_delta_pct"])
        ax.set_xlabel("Maximum absolute mission fuel delta (%)")
        ax.set_ylabel("Changed parameter")
        ax.set_title("Sensitivity Tornado")
        ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    _save_figure(fig, png_dir / "constraint_tornado.png", svg_dir / "constraint_tornado.svg")
    plt.close(fig)


def _plot_pareto_fuel_vs_mtow(
    summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    scatter = ax.scatter(
        summary["estimated_mtow_kg"],
        summary["mission_fuel_kg"],
        c=summary["constraint_count"],
        cmap="viridis",
        alpha=0.78,
        edgecolors="none",
    )
    ax.set_xlabel("Estimated MTOW (kg)")
    ax.set_ylabel("Mission fuel model output (kg)")
    ax.set_title("Sensitivity Fuel vs MTOW")
    ax.grid(True, alpha=0.3)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Constraint row count")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "pareto_fuel_vs_mtow.png",
        svg_dir / "pareto_fuel_vs_mtow.svg",
    )
    plt.close(fig)


def _plot_thrust_margin_vs_engine_rating(
    summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    baseline = summary[summary["case_family"] == "baseline"].copy()
    baseline["engine_thrust_N"] = 115000.0
    sweep = summary[
        summary["changed_parameter"] == "sea_level_static_thrust_N_per_engine"
    ].copy()
    if not sweep.empty:
        sweep["engine_thrust_N"] = sweep["changed_value"].astype(float)
    plot_data = pd.concat([baseline, sweep], ignore_index=True)
    for case_name, group in plot_data.groupby("propulsion_case"):
        ordered = group.sort_values("engine_thrust_N")
        ax.plot(
            ordered["engine_thrust_N"],
            ordered["min_thrust_margin_N"],
            marker="o",
            label=case_name,
        )
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xlabel("Sea-level static thrust per engine (N)")
    ax.set_ylabel("Minimum thrust margin (N)")
    ax.set_title("Thrust Margin vs Engine Rating")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize="small")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "thrust_margin_vs_engine_rating.png",
        svg_dir / "thrust_margin_vs_engine_rating.svg",
    )
    plt.close(fig)


def _plot_hybrid_power_sizing_map(
    merged: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    hybrid = merged[merged["propulsion_case"] == "adaptive_cycle_plus_hybrid_electric"]
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    if hybrid.empty:
        ax.text(0.5, 0.5, "No hybrid cases", ha="center", va="center")
        ax.set_axis_off()
    else:
        scatter = ax.scatter(
            hybrid["total_electric_power_W"] / 1.0e6,
            hybrid["unmet_electric_load_Wh"],
            c=hybrid["battery_capacity_Wh"] / 1000.0,
            cmap="plasma",
            alpha=0.78,
            edgecolors="none",
        )
        ax.set_xlabel("Total electric fan power assumption (MW)")
        ax.set_ylabel("Unmet electric load (Wh)")
        ax.set_title("Hybrid Power Sizing Map")
        ax.grid(True, alpha=0.3)
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label("Battery capacity (kWh)")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "hybrid_power_sizing_map.png",
        svg_dir / "hybrid_power_sizing_map.svg",
    )
    plt.close(fig)


def _plot_takeoff_proxy_sensitivity(
    merged: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    hybrid = merged[merged["propulsion_case"] == "adaptive_cycle_plus_hybrid_electric"]
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    if hybrid.empty:
        ax.text(0.5, 0.5, "No hybrid cases", ha="center", va="center")
        ax.set_axis_off()
    else:
        scatter = ax.scatter(
            hybrid["total_electric_power_W"] / 1.0e6,
            hybrid["takeoff_proxy_index"],
            c=hybrid["hybrid_mass_per_MW_kg"],
            cmap="cividis",
            alpha=0.78,
            edgecolors="none",
        )
        ax.set_xlabel("Total electric fan power assumption (MW)")
        ax.set_ylabel("Takeoff proxy index (-)")
        ax.set_title("Takeoff Proxy Sensitivity")
        ax.grid(True, alpha=0.3)
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label("Hybrid mass per MW (kg/MW)")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "takeoff_proxy_sensitivity.png",
        svg_dir / "takeoff_proxy_sensitivity.svg",
    )
    plt.close(fig)


def _plot_corrected_constraint_feasibility_map(
    summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    colors = summary["feasible_basic_corrected"].map({True: "#2ca02c", False: "#d62728"})
    ax.scatter(
        summary["estimated_mtow_kg"],
        summary["mission_fuel_kg"],
        c=colors,
        alpha=0.78,
        edgecolors="none",
    )
    ax.set_xlabel("Estimated MTOW (kg)")
    ax.set_ylabel("Mission fuel model output (kg)")
    ax.set_title("Corrected Basic Feasibility Screen")
    ax.grid(True, alpha=0.3)
    _add_boolean_legend(ax, "All-segment corrected feasible")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "corrected_constraint_feasibility_map.png",
        svg_dir / "corrected_constraint_feasibility_map.svg",
    )
    plt.close(fig)


def _plot_raw_vs_corrected_thrust_margin(
    summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    colors = summary["approach_only_model_sensitive"].map(
        {True: "#2ca02c", False: "#d62728"}
    )
    ax.scatter(
        summary["raw_all_segment_min_thrust_margin_N"],
        summary["corrected_all_segment_min_thrust_margin_N"],
        c=colors,
        alpha=0.78,
        edgecolors="none",
    )
    min_axis = min(
        float(summary["raw_all_segment_min_thrust_margin_N"].min()),
        float(summary["corrected_all_segment_min_thrust_margin_N"].min()),
        0.0,
    )
    max_axis = max(
        float(summary["raw_all_segment_min_thrust_margin_N"].max()),
        float(summary["corrected_all_segment_min_thrust_margin_N"].max()),
        0.0,
    )
    ax.plot([min_axis, max_axis], [min_axis, max_axis], color="black", linewidth=1.0)
    ax.axhline(0.0, color="gray", linewidth=1.0, linestyle="--")
    ax.axvline(0.0, color="gray", linewidth=1.0, linestyle="--")
    ax.set_xlabel("Raw all-segment minimum thrust margin (N)")
    ax.set_ylabel("Corrected all-segment minimum thrust margin (N)")
    ax.set_title("Raw vs Corrected All-Segment Thrust Margin")
    ax.grid(True, alpha=0.3)
    _add_boolean_legend(ax, "Approach-model sensitive")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "raw_vs_corrected_thrust_margin.png",
        svg_dir / "raw_vs_corrected_thrust_margin.svg",
    )
    plt.close(fig)


def _plot_approach_model_sensitivity_classification(
    corrected_summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    wanted = [
        "low_thrust_margin",
        "approach_only_corrected_low_thrust_margin",
        "corrected_all_segment_low_thrust_margin",
        "approach_only_model_sensitive",
        "sizing_or_schedule_low_thrust",
        "feasible_basic_approach_corrected",
        "feasible_basic_all_segment_corrected",
    ]
    table = corrected_summary[corrected_summary["metric"].isin(wanted)].copy()
    table["plot_count"] = table["corrected_count"]
    table.loc[table["metric"] == "low_thrust_margin", "plot_count"] = table.loc[
        table["metric"] == "low_thrust_margin",
        "raw_count",
    ]

    fig, ax = plt.subplots(figsize=(8.4, 4.8), dpi=140)
    ax.bar(table["metric"], table["plot_count"])
    ax.set_xlabel("Classification metric")
    ax.set_ylabel("Case count")
    ax.set_title("Approach Classification Counts")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "approach_model_sensitivity_classification.png",
        svg_dir / "approach_model_sensitivity_classification.svg",
    )
    plt.close(fig)


def _plot_approach_only_vs_all_segment_margin(
    summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    colors = summary["feasible_basic_all_segment_corrected"].map(
        {True: "#2ca02c", False: "#d62728"}
    )
    ax.scatter(
        summary["approach_only_corrected_margin_N"],
        summary["corrected_all_segment_min_thrust_margin_N"],
        c=colors,
        alpha=0.78,
        edgecolors="none",
    )
    min_axis = min(
        float(summary["approach_only_corrected_margin_N"].min()),
        float(summary["corrected_all_segment_min_thrust_margin_N"].min()),
        0.0,
    )
    max_axis = max(
        float(summary["approach_only_corrected_margin_N"].max()),
        float(summary["corrected_all_segment_min_thrust_margin_N"].max()),
        0.0,
    )
    ax.plot([min_axis, max_axis], [min_axis, max_axis], color="black", linewidth=1.0)
    ax.axhline(0.0, color="gray", linewidth=1.0, linestyle="--")
    ax.axvline(0.0, color="gray", linewidth=1.0, linestyle="--")
    ax.set_xlabel("Approach-only corrected margin (N)")
    ax.set_ylabel("All-segment corrected minimum margin (N)")
    ax.set_title("Approach-Only vs All-Segment Corrected Margin")
    ax.grid(True, alpha=0.3)
    _add_boolean_legend(ax, "All-segment corrected feasible")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "approach_only_vs_all_segment_margin.png",
        svg_dir / "approach_only_vs_all_segment_margin.svg",
    )
    plt.close(fig)


def _plot_sensitivity_feasibility_reclassified(
    summary: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    counts = pd.DataFrame(
        [
            {
                "screen": "Raw",
                "count": int(summary["feasible_basic_raw"].sum()),
            },
            {
                "screen": "Approach-only corrected",
                "count": int(summary["feasible_basic_approach_corrected"].sum()),
            },
            {
                "screen": "All-segment corrected",
                "count": int(summary["feasible_basic_all_segment_corrected"].sum()),
            },
        ]
    )
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.bar(counts["screen"], counts["count"], color=["#7f7f7f", "#1f77b4", "#2ca02c"])
    ax.set_xlabel("Basic screening basis")
    ax.set_ylabel("Case count")
    ax.set_title("Sensitivity Feasibility Reclassification")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "sensitivity_feasibility_reclassified.png",
        svg_dir / "sensitivity_feasibility_reclassified.svg",
    )
    plt.close(fig)


def _plot_non_approach_constraint_drivers(
    non_approach_constraints: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    if non_approach_constraints.empty:
        ax.text(0.5, 0.5, "No non-approach constraint rows", ha="center", va="center")
        ax.set_axis_off()
    else:
        table = (
            non_approach_constraints[
                non_approach_constraints["non_approach_low_thrust_margin"].astype(bool)
            ]
            .groupby("non_approach_limiting_segment", as_index=False)
            .size()
            .sort_values("size", ascending=False)
        )
        if table.empty:
            ax.text(0.5, 0.5, "No non-approach low-thrust rows", ha="center", va="center")
            ax.set_axis_off()
        else:
            ax.bar(table["non_approach_limiting_segment"], table["size"])
            ax.set_xlabel("Non-approach limiting segment")
            ax.set_ylabel("Case count")
            ax.set_title("Non-Approach Constraint Drivers")
            ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "non_approach_constraint_drivers.png",
        svg_dir / "non_approach_constraint_drivers.svg",
    )
    plt.close(fig)


def _add_boolean_legend(ax, label: str) -> None:
    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#2ca02c",
            label=f"{label}: yes",
            markersize=8,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#d62728",
            label=f"{label}: no",
            markersize=8,
        ),
    ]
    ax.legend(handles=handles, fontsize="small")


def _save_figure(fig, png_path: Path, svg_path: Path) -> None:
    fig.savefig(png_path)
    fig.savefig(svg_path)
    _strip_trailing_whitespace(svg_path)


def _strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
