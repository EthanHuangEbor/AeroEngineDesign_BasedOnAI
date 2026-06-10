"""Generate V0.2-04S approach/landing force-balance audit outputs."""

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

from mta_vhep.aircraft.aerodynamics import AeroModel, AeroState  # noqa: E402
from mta_vhep.core.atmosphere import isa_atmosphere  # noqa: E402
from mta_vhep.core.units import kg_to_N  # noqa: E402
from mta_vhep.interfaces.csv_export import write_dataframe_csv  # noqa: E402
from mta_vhep.interfaces.io import load_fuel_database, load_project_config, load_yaml  # noqa: E402
from mta_vhep.mission.approach_analysis import (  # noqa: E402
    ApproachForceBalanceInput,
    evaluate_approach_force_balance,
)
from mta_vhep.propulsion.fuel import get_fuel  # noqa: E402
from mta_vhep.propulsion.turbofan_vce import EngineOperatingPoint, VariableCycleTurbofan  # noqa: E402


GAMMA_SCAN_DEG = (-2.5, -3.0, -3.5)


def main() -> None:
    """Run approach/landing force-balance audit and export result artifacts."""
    config_dir = SIM_ROOT / "config"
    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

    project_config = load_project_config(config_dir)
    mission_solver_config = load_yaml(config_dir / "mission_solver.yaml")
    approach_config = mission_solver_config["approach_landing_model"]
    aero_config = load_yaml(config_dir / "aero_model.yaml")
    propulsion_config = load_yaml(config_dir / "propulsion.yaml")
    engine_config = load_yaml(config_dir / "engine_surrogate.yaml")
    hybrid_config = load_yaml(config_dir / "hybrid_electric.yaml")
    fuel = get_fuel(load_fuel_database(config_dir), "Jet-A")

    mission_segments = _load_mission_segments(csv_dir)
    approach_segments = mission_segments[
        mission_segments["segment_name"] == "approach_landing"
    ].copy()

    audit_table = _build_approach_diagnostics(
        approach_segments,
        aero_config,
        approach_config,
    )
    sensitivity_table = _build_sensitivity_scan(
        approach_segments,
        aero_config,
        approach_config,
        propulsion_config,
        engine_config,
        hybrid_config,
        project_config,
        fuel,
    )

    write_dataframe_csv(audit_table, csv_dir / "approach_landing_diagnostics.csv")
    write_dataframe_csv(sensitivity_table, csv_dir / "approach_sensitivity_scan.csv")

    _plot_approach_margin_audit(audit_table, png_dir, svg_dir)
    _plot_sensitivity_scan(sensitivity_table, png_dir, svg_dir)

    print("MTA-VHEP V0.2-04S Approach/Landing Audit Summary")
    print("Concept-level approach force balance only; no landing certification claim.")
    print(f"Approach diagnostic rows: {len(audit_table)}")
    print(f"Approach sensitivity rows: {len(sensitivity_table)}")
    print(f"Wrote: {csv_dir / 'approach_landing_diagnostics.csv'}")
    print(f"Wrote: {csv_dir / 'approach_sensitivity_scan.csv'}")


def _load_mission_segments(csv_dir: Path) -> pd.DataFrame:
    path = csv_dir / "mission_segments.csv"
    if not path.exists():
        raise FileNotFoundError(
            "mission_segments.csv is missing; run scripts/run_04_mission.py first"
        )
    return pd.read_csv(path)


def _build_approach_diagnostics(
    approach_segments: pd.DataFrame,
    aero_config: dict,
    approach_config: dict,
) -> pd.DataFrame:
    rows = []
    default_gamma_deg = float(approach_config["default_descent_angle_deg"])
    include_weight_component = bool(
        approach_config["include_weight_component_along_path"]
    )
    for _, segment in approach_segments.iterrows():
        drag_N = _compute_approach_drag_N(segment, aero_config)
        result = evaluate_approach_force_balance(
            ApproachForceBalanceInput(
                case_name=str(segment["case_name"]),
                segment_name=str(segment["segment_name"]),
                weight_N=kg_to_N(float(segment["start_mass_kg"])),
                speed_mps=float(segment["speed_mps"]),
                altitude_m=_mid_altitude_m(segment),
                gamma_deg=default_gamma_deg,
                drag_N=drag_N,
                available_thrust_N=float(segment["available_thrust_N"]),
                electric_thrust_proxy_N=float(segment["electric_thrust_proxy_N"]),
                include_weight_component_along_path=include_weight_component,
            )
        )
        row = asdict(result)
        row["mission_required_thrust_N"] = float(segment["average_required_thrust_N"])
        row["mission_thrust_margin_N"] = float(segment["thrust_margin_N"])
        row["unmet_electric_load_Wh"] = float(segment["unmet_electric_load_Wh"])
        row["constraint_flags"] = str(segment["constraint_flags"])
        rows.append(row)
    return pd.DataFrame(rows)


def _build_sensitivity_scan(
    approach_segments: pd.DataFrame,
    aero_config: dict,
    approach_config: dict,
    propulsion_config: dict,
    engine_config: dict,
    hybrid_config: dict,
    project_config,
    fuel,
) -> pd.DataFrame:
    rows = []
    mode_schedules = propulsion_config["propulsion"]["main_engine"]["modes"]
    case_configs = {
        item["name"]: item for item in load_yaml(SIM_ROOT / "config" / "mission_solver.yaml")["mission_solver"]["cases"]
    }
    drag_factors = [float(value) for value in approach_config["approach_drag_factor_scan"]]
    ratings = [str(value) for value in approach_config["approach_rating_scan"]]
    include_weight_component = bool(
        approach_config["include_weight_component_along_path"]
    )
    engine_count = project_config.main_engine.count

    for _, segment in approach_segments.iterrows():
        case_name = str(segment["case_name"])
        case_config = case_configs[case_name]
        engine = VariableCycleTurbofan.from_config(
            engine_config,
            _engine_variant_key(str(case_config["engine_variant"])),
        )
        base_drag_N = _compute_approach_drag_N(segment, aero_config)
        electric_options = _electric_options(case_name)
        altitude_m = _mid_altitude_m(segment)
        speed_mps = float(segment["speed_mps"])
        mach = speed_mps / isa_atmosphere(altitude_m).speed_of_sound_mps

        for gamma_deg in GAMMA_SCAN_DEG:
            for drag_factor in drag_factors:
                for rating in ratings:
                    for electric_assist_enabled in electric_options:
                        electric_thrust_N = (
                            float(segment["electric_thrust_proxy_N"])
                            if electric_assist_enabled
                            else 0.0
                        )
                        shaft_power_W = (
                            _approach_shaft_extraction_W_per_engine(hybrid_config)
                            if electric_assist_enabled
                            else 0.0
                        )
                        engine_available_N = _engine_available_thrust_N(
                            engine,
                            rating,
                            mach,
                            altitude_m,
                            shaft_power_W,
                            mode_schedules,
                            bool(case_config["adaptive_third_stream_enabled"]),
                            fuel,
                            engine_count,
                        )
                        available_thrust_N = engine_available_N + electric_thrust_N
                        result = evaluate_approach_force_balance(
                            ApproachForceBalanceInput(
                                case_name=case_name,
                                segment_name=str(segment["segment_name"]),
                                weight_N=kg_to_N(float(segment["start_mass_kg"])),
                                speed_mps=speed_mps,
                                altitude_m=altitude_m,
                                gamma_deg=float(gamma_deg),
                                drag_N=base_drag_N * drag_factor,
                                available_thrust_N=available_thrust_N,
                                electric_thrust_proxy_N=electric_thrust_N,
                                include_weight_component_along_path=include_weight_component,
                            )
                        )
                        row = asdict(result)
                        row["approach_drag_factor"] = drag_factor
                        row["rating"] = rating
                        row["electric_assist_enabled"] = electric_assist_enabled
                        row["engine_available_thrust_N"] = engine_available_N
                        row["mission_required_thrust_N"] = float(
                            segment["average_required_thrust_N"]
                        )
                        row["mission_thrust_margin_N"] = float(segment["thrust_margin_N"])
                        row["unmet_electric_load_Wh"] = float(
                            segment["unmet_electric_load_Wh"]
                        )
                        rows.append(row)
    return pd.DataFrame(rows)


def _compute_approach_drag_N(segment: pd.Series, aero_config: dict) -> float:
    altitude_m = _mid_altitude_m(segment)
    atmosphere = isa_atmosphere(altitude_m)
    speed_mps = float(segment["speed_mps"])
    mach = speed_mps / atmosphere.speed_of_sound_mps
    wing_area_m2 = float(aero_config["aero"]["default"]["wing_area_m2"])
    model = AeroModel.from_config(aero_config)
    performance = model.evaluate(
        AeroState(
            mach=mach,
            altitude_m=altitude_m,
            weight_N=kg_to_N(float(segment["start_mass_kg"])),
            wing_area_m2=wing_area_m2,
            flap_mode="landing_flap",
            gear_down=True,
            blowing_momentum_coefficient=float(
                segment["blowing_momentum_coefficient"]
            ),
        ),
        atmosphere,
    )
    dynamic_pressure_Pa = 0.5 * atmosphere.density_kg_m3 * speed_mps**2
    return dynamic_pressure_Pa * wing_area_m2 * performance.cd


def _engine_available_thrust_N(
    engine: VariableCycleTurbofan,
    rating: str,
    mach: float,
    altitude_m: float,
    shaft_power_extraction_W: float,
    mode_schedules: dict,
    adaptive_enabled: bool,
    fuel,
    engine_count: int,
) -> float:
    schedule = mode_schedules[rating]
    performance = engine.evaluate(
        EngineOperatingPoint(
            mach=mach,
            altitude_m=altitude_m,
            throttle=float(schedule["throttle"]),
            rating=rating,
            shaft_power_extraction_W=shaft_power_extraction_W,
            third_stream_schedule=(
                float(schedule["third_stream_schedule"]) if adaptive_enabled else 0.0
            ),
            variable_nozzle_schedule=(
                float(schedule["variable_nozzle_schedule"]) if adaptive_enabled else 0.0
            ),
            fuel=fuel,
        )
    )
    return performance.net_thrust_N * engine_count


def _approach_shaft_extraction_W_per_engine(hybrid_config: dict) -> float:
    hybrid = hybrid_config["hybrid_electric"]
    generator = hybrid["generator"]
    for phase in hybrid["operation_schedule"]:
        if phase["phase"] == "approach":
            return (
                float(phase["generator_power_W_total"])
                / float(generator["efficiency"])
                / float(generator["engine_count"])
            )
    return 0.0


def _engine_variant_key(engine_variant: str) -> str:
    if engine_variant == "baseline_fixed_cycle_turbofan":
        return "baseline_fixed_cycle"
    if engine_variant == "three_stream_variable_cycle_turbofan":
        return "adaptive_cycle"
    raise ValueError(f"Unsupported engine variant: {engine_variant}")


def _electric_options(case_name: str) -> tuple[bool, ...]:
    if case_name == "adaptive_cycle_plus_hybrid_electric":
        return (False, True)
    return (False,)


def _mid_altitude_m(segment: pd.Series) -> float:
    return 0.5 * (float(segment["altitude_start_m"]) + float(segment["altitude_end_m"]))


def _plot_approach_margin_audit(
    audit_table: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    x = range(len(audit_table))
    width = 0.36
    ax.bar(
        [item - width / 2 for item in x],
        audit_table["thrust_margin_level_flight_N"],
        width,
        label="Level-flight balance",
    )
    ax.bar(
        [item + width / 2 for item in x],
        audit_table["thrust_margin_descent_N"],
        width,
        label="Descent balance",
    )
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xticks(list(x), audit_table["case_name"], rotation=20)
    ax.set_xlabel("Mission case")
    ax.set_ylabel("Approach thrust margin (N)")
    ax.set_title("Approach Thrust Margin Audit")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "approach_thrust_margin_audit.png",
        svg_dir / "approach_thrust_margin_audit.svg",
    )
    plt.close(fig)


def _plot_sensitivity_scan(
    scan_table: pd.DataFrame,
    png_dir: Path,
    svg_dir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    subset = scan_table[
        (scan_table["approach_drag_factor"] == 1.0)
        & (scan_table["electric_assist_enabled"] == scan_table["case_name"].eq("adaptive_cycle_plus_hybrid_electric"))
    ]
    for (case_name, rating), group in subset.groupby(["case_name", "rating"]):
        ordered = group.sort_values("gamma_deg")
        ax.plot(
            ordered["gamma_deg"],
            ordered["thrust_margin_descent_N"],
            marker="o",
            label=f"{case_name} / {rating}",
        )
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_xlabel("Descent angle gamma (deg)")
    ax.set_ylabel("Descent thrust margin (N)")
    ax.set_title("Approach Sensitivity Scan")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize="small")
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "approach_sensitivity_scan.png",
        svg_dir / "approach_sensitivity_scan.svg",
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
