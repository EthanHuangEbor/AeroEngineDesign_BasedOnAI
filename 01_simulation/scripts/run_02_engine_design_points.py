"""Generate V0.2-02 engine surrogate design-point outputs."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


SIM_ROOT = Path(__file__).resolve().parents[1]
if str(SIM_ROOT) not in sys.path:
    sys.path.insert(0, str(SIM_ROOT))

from mta_vhep.interfaces.csv_export import write_dataframe_csv  # noqa: E402
from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml  # noqa: E402
from mta_vhep.propulsion.fuel import get_fuel  # noqa: E402
from mta_vhep.propulsion.turbofan_vce import EngineOperatingPoint, VariableCycleTurbofan  # noqa: E402


VARIANTS = ("baseline_fixed_cycle", "adaptive_cycle")
POWER_SWEEP_W = (0, 500000, 1000000, 2000000, 3000000)
POWER_SWEEP_RATINGS = ("takeoff", "climb", "approach")


def main() -> None:
    """Run engine design-point and power extraction surrogate checks."""
    project_config = load_project_config(SIM_ROOT / "config")
    fuels = load_fuel_database(SIM_ROOT / "config")
    jet_a = get_fuel(fuels, "Jet-A")
    propulsion_config = load_yaml(SIM_ROOT / "config" / "propulsion.yaml")
    engine_config = load_yaml(SIM_ROOT / "config" / "engine_surrogate.yaml")

    engines = {
        variant: VariableCycleTurbofan.from_config(engine_config, variant) for variant in VARIANTS
    }
    design_points = engine_config["engine_surrogate"]["design_points"]
    mode_schedules = propulsion_config["propulsion"]["main_engine"]["modes"]

    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

    design_table = _build_design_point_table(
        engines,
        design_points,
        mode_schedules,
        jet_a,
    )
    design_csv = csv_dir / "engine_design_points.csv"
    write_dataframe_csv(design_table, design_csv)

    extraction_table = _build_power_extraction_table(
        engines["adaptive_cycle"],
        design_points,
        mode_schedules,
        jet_a,
    )
    extraction_csv = csv_dir / "engine_power_extraction_sweep.csv"
    write_dataframe_csv(extraction_table, extraction_csv)

    _plot_tsfc_mode_map(design_table, png_dir, svg_dir)
    _plot_thrust_lapse_map(design_table, png_dir, svg_dir)
    _plot_power_extraction(extraction_table, png_dir, svg_dir)

    print("MTA-VHEP V0.2-02 Engine Surrogate Summary")
    print("Concept-level engine surrogate only; no certified cycle analysis run.")
    print(f"Engine variants: {', '.join(engines)}")
    print(f"Design point rows: {len(design_table)}")
    print(f"Power extraction rows: {len(extraction_table)}")
    print(f"Wrote: {design_csv}")
    print(f"Wrote: {extraction_csv}")


def _build_design_point_table(
    engines: dict[str, VariableCycleTurbofan],
    design_points: list[dict],
    mode_schedules: dict,
    fuel,
) -> pd.DataFrame:
    rows = []
    for variant, engine in engines.items():
        for point in design_points:
            op = _make_operating_point(point, mode_schedules, fuel, 0.0)
            performance = engine.evaluate(op)
            rows.append(_performance_row(variant, point["name"], op, performance))
    return pd.DataFrame(rows)


def _build_power_extraction_table(
    engine: VariableCycleTurbofan,
    design_points: list[dict],
    mode_schedules: dict,
    fuel,
) -> pd.DataFrame:
    points_by_rating = {point["rating"]: point for point in design_points}
    rows = []
    for rating in POWER_SWEEP_RATINGS:
        point = points_by_rating[rating]
        for shaft_power_W in POWER_SWEEP_W:
            op = _make_operating_point(point, mode_schedules, fuel, float(shaft_power_W))
            performance = engine.evaluate(op)
            rows.append(
                _performance_row(
                    "adaptive_cycle",
                    f"{rating}_extraction_{shaft_power_W}",
                    op,
                    performance,
                )
            )
    return pd.DataFrame(rows)


def _make_operating_point(
    point: dict,
    mode_schedules: dict,
    fuel,
    shaft_power_extraction_W: float,
) -> EngineOperatingPoint:
    schedule = mode_schedules.get(point["rating"], {})
    return EngineOperatingPoint(
        mach=float(point["mach"]),
        altitude_m=float(point["altitude_m"]),
        throttle=float(point["throttle"]),
        rating=str(point["rating"]),
        shaft_power_extraction_W=shaft_power_extraction_W,
        third_stream_schedule=float(schedule.get("third_stream_schedule", 0.0)),
        variable_nozzle_schedule=float(schedule.get("variable_nozzle_schedule", 0.0)),
        fuel=fuel,
    )


def _performance_row(
    variant: str,
    design_point: str,
    op: EngineOperatingPoint,
    performance,
) -> dict:
    return {
        "variant": variant,
        "engine_name": performance.engine_name,
        "design_point": design_point,
        "rating": op.rating,
        "mach": op.mach,
        "altitude_m": op.altitude_m,
        "throttle": op.throttle,
        "third_stream_schedule": op.third_stream_schedule,
        "variable_nozzle_schedule": op.variable_nozzle_schedule,
        "shaft_power_extraction_W": op.shaft_power_extraction_W,
        "gross_thrust_N": performance.gross_thrust_N,
        "net_thrust_N": performance.net_thrust_N,
        "fuel_flow_kg_s": performance.fuel_flow_kg_s,
        "tsfc_kg_per_N_s": performance.tsfc_kg_per_N_s,
        "thrust_penalty_from_extraction_N": performance.thrust_penalty_from_extraction_N,
        "fuel_flow_increment_from_extraction_kg_s": (
            performance.fuel_flow_increment_from_extraction_kg_s
        ),
        "constraint_flags": ";".join(performance.constraint_flags),
    }


def _plot_tsfc_mode_map(table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    pivot = table.pivot(index="rating", columns="variant", values="tsfc_kg_per_N_s")
    ordered = pivot.reindex(["idle", "approach", "climb", "cruise", "takeoff"])
    ordered.plot(kind="bar", ax=ax)
    ax.set_xlabel("Engine rating")
    ax.set_ylabel("TSFC (kg/N/s)")
    ax.set_title("Concept Engine TSFC by Rating")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(fig, png_dir / "tsfc_mode_map.png", svg_dir / "tsfc_mode_map.svg")
    plt.close(fig)


def _plot_thrust_lapse_map(table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    for variant, subset in table.groupby("variant"):
        ordered = subset.sort_values("altitude_m")
        ax.plot(
            ordered["altitude_m"],
            ordered["net_thrust_N"],
            marker="o",
            label=variant,
        )
    ax.set_xlabel("Altitude (m)")
    ax.set_ylabel("Net thrust per engine (N)")
    ax.set_title("Concept Thrust Lapse at Design Points")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Variant")
    fig.tight_layout()
    _save_figure(fig, png_dir / "thrust_lapse_map.png", svg_dir / "thrust_lapse_map.svg")
    plt.close(fig)


def _plot_power_extraction(table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    for rating, subset in table.groupby("rating"):
        ordered = subset.sort_values("shaft_power_extraction_W")
        ax.plot(
            ordered["shaft_power_extraction_W"] / 1_000_000.0,
            ordered["thrust_penalty_from_extraction_N"],
            marker="o",
            label=f"{rating} thrust penalty",
        )
    ax.set_xlabel("Shaft power extraction per engine (MW)")
    ax.set_ylabel("Equivalent thrust penalty (N)")
    ax.grid(True, alpha=0.3)

    ax_fuel = ax.twinx()
    representative = table[table["rating"] == "climb"].sort_values("shaft_power_extraction_W")
    ax_fuel.plot(
        representative["shaft_power_extraction_W"] / 1_000_000.0,
        representative["fuel_flow_increment_from_extraction_kg_s"],
        color="#d62728",
        linestyle="--",
        marker="s",
        label="fuel flow increment",
    )
    ax_fuel.set_ylabel("Fuel flow increment (kg/s)")
    fig.suptitle("Concept Shaft Power Extraction Penalty")
    lines, labels = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax_fuel.get_legend_handles_labels()
    ax.legend(lines + lines_2, labels + labels_2, loc="upper left")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "power_extraction_penalty.png",
        svg_dir / "power_extraction_penalty.svg",
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
