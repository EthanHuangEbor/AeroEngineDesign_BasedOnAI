"""Generate V0.2-01 atmosphere, fuel, and basic aero verification outputs."""

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
from mta_vhep.interfaces.io import load_project_config, load_yaml  # noqa: E402
from mta_vhep.propulsion.fuel import blend_fuel, get_fuel  # noqa: E402


ATMOSPHERE_ALTITUDES_M = [0, 1000, 3000, 6000, 9000, 10668, 12000]
FLAP_MODES = ["clean", "takeoff_flap", "landing_flap"]
BLOWING_CMU_VALUES = [0.0, 0.04, 0.08, 0.12]


def main() -> None:
    """Run the V0.2-01 verification outputs."""
    config = load_project_config(SIM_ROOT / "config")
    aero_config = load_yaml(SIM_ROOT / "config" / "aero_model.yaml")
    aero_model = AeroModel.from_config(aero_config)

    jet_a = get_fuel(config.fuels, "Jet-A")
    saf = get_fuel(config.fuels, "SAF_generic")
    saf_50 = blend_fuel(jet_a, saf, 0.5)

    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

    atmosphere_table = _build_atmosphere_table()
    atmosphere_csv = csv_dir / "atmosphere_table.csv"
    write_dataframe_csv(atmosphere_table, atmosphere_csv)

    aero_table = _build_aero_table(config, aero_model)
    aero_csv = csv_dir / "aero_check_table.csv"
    write_dataframe_csv(aero_table, aero_csv)

    _plot_atmosphere(atmosphere_table, png_dir, svg_dir)
    _plot_stall_speed(aero_table, png_dir, svg_dir)

    print("MTA-VHEP V0.2-01 Environment/Aero Summary")
    print("Concept-level atmosphere, fuel properties, and drag polar only.")
    print(f"Atmosphere rows: {len(atmosphere_table)}")
    print(f"Aero check rows: {len(aero_table)}")
    print(f"Fuel names: {', '.join(sorted(config.fuels))}")
    print(f"50% SAF blend LHV: {saf_50.lower_heating_value_J_per_kg:g} J/kg")
    print(f"Wrote: {atmosphere_csv}")
    print(f"Wrote: {aero_csv}")


def _build_atmosphere_table() -> pd.DataFrame:
    rows = []
    for altitude_m in ATMOSPHERE_ALTITUDES_M:
        state = isa_atmosphere(float(altitude_m))
        rows.append(
            {
                "altitude_m": state.altitude_m,
                "delta_isa_K": state.delta_isa_K,
                "temperature_K": state.temperature_K,
                "pressure_Pa": state.pressure_Pa,
                "density_kg_m3": state.density_kg_m3,
                "speed_of_sound_mps": state.speed_of_sound_mps,
            }
        )
    return pd.DataFrame(rows)


def _build_aero_table(config, aero_model: AeroModel) -> pd.DataFrame:
    atmosphere = isa_atmosphere(config.aircraft.cruise_altitude_m)
    weight_N = kg_to_N(config.aircraft.mtow_initial_kg)
    rows = []

    for flap_mode in FLAP_MODES:
        for cmu in BLOWING_CMU_VALUES:
            performance = aero_model.evaluate(
                AeroState(
                    mach=config.aircraft.cruise_mach,
                    altitude_m=config.aircraft.cruise_altitude_m,
                    weight_N=weight_N,
                    wing_area_m2=config.geometry.wing_area_m2_initial,
                    flap_mode=flap_mode,
                    gear_down=flap_mode == "landing_flap",
                    blowing_momentum_coefficient=cmu,
                ),
                atmosphere,
            )
            rows.append(
                {
                    "mach": config.aircraft.cruise_mach,
                    "altitude_m": config.aircraft.cruise_altitude_m,
                    "weight_N": weight_N,
                    "wing_area_m2": config.geometry.wing_area_m2_initial,
                    "flap_mode": flap_mode,
                    "gear_down": flap_mode == "landing_flap",
                    "blowing_momentum_coefficient": cmu,
                    "cl": performance.cl,
                    "cd": performance.cd,
                    "ld_ratio": performance.ld_ratio,
                    "cl_max": performance.cl_max,
                    "stall_speed_mps": performance.stall_speed_mps,
                }
            )

    return pd.DataFrame(rows)


def _plot_atmosphere(table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax_density = plt.subplots(figsize=(7.0, 4.5), dpi=140)
    ax_density.plot(
        table["altitude_m"],
        table["density_kg_m3"],
        marker="o",
        label="Density",
        color="#1f77b4",
    )
    ax_density.set_xlabel("Altitude (m)")
    ax_density.set_ylabel("Density (kg/m^3)", color="#1f77b4")
    ax_density.tick_params(axis="y", labelcolor="#1f77b4")
    ax_density.grid(True, alpha=0.3)

    ax_sound = ax_density.twinx()
    ax_sound.plot(
        table["altitude_m"],
        table["speed_of_sound_mps"],
        marker="s",
        label="Speed of sound",
        color="#d62728",
    )
    ax_sound.set_ylabel("Speed of sound (m/s)", color="#d62728")
    ax_sound.tick_params(axis="y", labelcolor="#d62728")
    fig.suptitle("ISA Atmosphere Profile")
    fig.tight_layout()
    fig.savefig(png_dir / "atmosphere_profile.png")
    fig.savefig(svg_dir / "atmosphere_profile.svg")
    plt.close(fig)


def _plot_stall_speed(table: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.5), dpi=140)
    for flap_mode, subset in table.groupby("flap_mode"):
        ordered = subset.sort_values("cl_max")
        ax.plot(
            ordered["cl_max"],
            ordered["stall_speed_mps"],
            marker="o",
            label=flap_mode,
        )
    ax.set_xlabel("CLmax (-)")
    ax.set_ylabel("Stall speed (m/s)")
    ax.set_title("Concept Stall Speed vs CLmax")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Flap mode")
    fig.tight_layout()
    fig.savefig(png_dir / "stall_speed_vs_clmax.png")
    fig.savefig(svg_dir / "stall_speed_vs_clmax.svg")
    plt.close(fig)


if __name__ == "__main__":
    main()
