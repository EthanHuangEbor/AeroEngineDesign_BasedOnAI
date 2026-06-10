"""Smoke test for MTA-VHEP V0.2 configuration loading."""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mta_vhep.interfaces.io import load_project_config  # noqa: E402


def build_summary() -> str:
    """Load config and return a concise text summary using SI units."""
    config = load_project_config(REPO_ROOT / "config")
    summed_distance_km = sum(
        segment.distance_km for segment in config.mission.segments if segment.distance_km is not None
    )
    fuel_names = ", ".join(sorted(config.fuels))

    lines = [
        "MTA-VHEP V0.2 Smoke Test Summary",
        "Concept-level configuration load only; no propulsion physics run.",
        f"Aircraft name: {config.aircraft.name}",
        f"Payload design: {config.aircraft.payload_design_kg:g} kg",
        f"Design range: {config.aircraft.range_design_km:g} km",
        f"Cruise Mach: {config.aircraft.cruise_mach:g}",
        f"Cruise altitude: {config.aircraft.cruise_altitude_m:g} m",
        f"MTOW initial: {config.aircraft.mtow_initial_kg:g} kg",
        f"OEW initial: {config.aircraft.oew_initial_kg:g} kg",
        f"Main engine type: {config.main_engine.engine_type}",
        f"Main engine count: {config.main_engine.count}",
        "Per-engine initial static thrust: "
        f"{config.main_engine.sea_level_static_thrust_N_per_engine_initial:g} N",
        f"Electric fan count: {config.electric_fan.count}",
        f"Per-fan initial power: {config.electric_fan.power_W_per_fan_initial:g} W",
        f"Fuel names: {fuel_names}",
        f"Mission name: {config.mission.name}",
        f"Mission segment count: {len(config.mission.segments)}",
        f"Summed nominal mission distance: {summed_distance_km:g} km",
    ]
    return "\n".join(lines)


def main() -> None:
    """Run the smoke test and write a log summary."""
    summary = build_summary()
    print(summary)

    log_dir = REPO_ROOT / "results" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "smoke_test_summary.txt").write_text(summary + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
