"""Generate V0.2-03 hybrid-electric subsystem proxy outputs."""

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
from mta_vhep.electrical.battery_buffer import BatteryBuffer  # noqa: E402
from mta_vhep.electrical.bus import ElectricalBus, ElectricalLoad  # noqa: E402
from mta_vhep.electrical.inverter import InverterModel  # noqa: E402
from mta_vhep.electrical.motor import MotorModel  # noqa: E402
from mta_vhep.electrical.thermal import ThermalAccumulator  # noqa: E402
from mta_vhep.interfaces.csv_export import write_dataframe_csv  # noqa: E402
from mta_vhep.interfaces.io import load_project_config, load_yaml  # noqa: E402
from mta_vhep.propulsion.electric_fan import ElectricBlownFlapFan, ElectricFanCommand  # noqa: E402
from mta_vhep.propulsion.power_extraction import compute_power_extraction_penalty  # noqa: E402


def main() -> None:
    """Run V0.2-03 hybrid-electric proxy checks and export result artifacts."""
    project_config = load_project_config(SIM_ROOT / "config")
    propulsion_config = load_yaml(SIM_ROOT / "config" / "propulsion.yaml")
    hybrid_config = load_yaml(SIM_ROOT / "config" / "hybrid_electric.yaml")
    aero_config = load_yaml(SIM_ROOT / "config" / "aero_model.yaml")
    engine_config = load_yaml(SIM_ROOT / "config" / "engine_surrogate.yaml")

    hybrid = hybrid_config["hybrid_electric"]
    fan = _build_fan(hybrid)
    battery = _build_battery(hybrid)
    bus = _build_bus(hybrid)
    thermal = ThermalAccumulator(hybrid["thermal"]["coolant_loop_efficiency"])

    csv_dir = SIM_ROOT / "results" / "csv"
    png_dir = SIM_ROOT / "figures" / "png"
    svg_dir = SIM_ROOT / "figures" / "svg"
    for directory in (csv_dir, png_dir, svg_dir):
        directory.mkdir(parents=True, exist_ok=True)

    timeline, extraction = _run_operation_schedule(
        project_config,
        propulsion_config,
        hybrid,
        aero_config,
        engine_config,
        fan,
        battery,
        bus,
        thermal,
    )
    summary = _build_summary(timeline, thermal)
    mode_summary = _build_mode_summary(project_config, hybrid, aero_config, fan)
    failure_cases = _build_failure_cases(project_config, hybrid, aero_config, fan)

    write_dataframe_csv(timeline, csv_dir / "hybrid_timeline.csv")
    write_dataframe_csv(summary, csv_dir / "hybrid_summary.csv")
    write_dataframe_csv(mode_summary, csv_dir / "electric_fan_mode_summary.csv")
    write_dataframe_csv(failure_cases, csv_dir / "fan_failure_cases.csv")
    write_dataframe_csv(extraction, csv_dir / "hybrid_power_extraction_proxy.csv")

    _plot_power_soc(timeline, png_dir, svg_dir)
    _plot_fan_thrust(timeline, png_dir, svg_dir)
    _plot_thermal_load(timeline, png_dir, svg_dir)
    _plot_failure_cases(failure_cases, png_dir, svg_dir)

    print("MTA-VHEP V0.2-03 Hybrid-Electric Summary")
    print("Concept-level hybrid-electric subsystem only; no mission solver run.")
    print(f"Timeline phases: {len(timeline)}")
    print(f"SOC range: {timeline['soc_min'].min():.4f} to {timeline['soc_max'].max():.4f}")
    print(f"Failure cases: {', '.join(failure_cases['case_name'])}")
    print(f"Wrote: {csv_dir / 'hybrid_timeline.csv'}")
    print(f"Wrote: {csv_dir / 'hybrid_summary.csv'}")


def _build_fan(hybrid: dict) -> ElectricBlownFlapFan:
    fan_cfg = hybrid["electric_fan"]
    motor = MotorModel(
        efficiency=hybrid["motor"]["efficiency"],
        specific_power_kW_per_kg=hybrid["motor"]["specific_power_kW_per_kg"],
    )
    inverter = InverterModel(
        efficiency=hybrid["inverter"]["efficiency"],
        specific_power_kW_per_kg=hybrid["inverter"]["specific_power_kW_per_kg"],
    )
    return ElectricBlownFlapFan(
        nominal_power_W=fan_cfg["nominal_power_W_per_fan"],
        max_power_W_for_v02=fan_cfg["max_power_W_per_fan_for_v02"],
        propulsive_efficiency=fan_cfg["propulsive_efficiency"],
        min_effective_airspeed_mps=fan_cfg["min_effective_airspeed_mps"],
        mode_power_fractions={
            mode: data["power_fraction"] for mode, data in fan_cfg["modes"].items()
        },
        motor=motor,
        inverter=inverter,
    )


def _build_battery(hybrid: dict) -> BatteryBuffer:
    battery = hybrid["battery_buffer"]
    bus = hybrid["electrical_bus"]
    return BatteryBuffer(
        capacity_Wh=battery["capacity_Wh"],
        initial_soc=battery["initial_soc"],
        min_soc=battery["min_soc"],
        max_soc=battery["max_soc"],
        max_discharge_power_W=bus["max_battery_discharge_power_W"],
        max_charge_power_W=bus["max_battery_charge_power_W"],
        roundtrip_efficiency=battery["roundtrip_efficiency"],
    )


def _build_bus(hybrid: dict) -> ElectricalBus:
    bus = hybrid["electrical_bus"]
    return ElectricalBus(
        voltage_V=bus["voltage_V"],
        cable_distribution_efficiency=bus["cable_distribution_efficiency"],
        load_shedding_enabled=bus["load_shedding_enabled"],
    )


def _run_operation_schedule(
    project_config,
    propulsion_config: dict,
    hybrid: dict,
    aero_config: dict,
    engine_config: dict,
    fan: ElectricBlownFlapFan,
    battery: BatteryBuffer,
    bus: ElectricalBus,
    thermal: ThermalAccumulator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    extraction_rows = []
    fan_count = hybrid["electric_fan"]["count"]
    wing_area_m2 = aero_config["aero"]["default"]["wing_area_m2"]
    bus_cfg = hybrid["electrical_bus"]
    generator_cfg = hybrid["generator"]
    extraction_cfg = engine_config["engine_surrogate"]["shaft_power_extraction"]

    for phase in hybrid["operation_schedule"]:
        duration_s = float(phase["duration_s"])
        airspeed_mps = float(phase["airspeed_mps"])
        altitude_m = float(phase["altitude_m"])
        atmosphere = isa_atmosphere(altitude_m)
        fan_mode = phase["fan_mode"]
        requested_per_fan_W = fan.requested_input_power_W(fan_mode)
        requested_load_W = requested_per_fan_W * fan_count
        source_required_W = (
            requested_load_W / bus.cable_distribution_efficiency
            if requested_load_W > 0.0
            else 0.0
        )
        generated_power_W = min(
            float(phase["generator_power_W_total"]),
            bus_cfg["max_generator_power_W_total_for_v02"],
        )
        battery_request_W = max(source_required_W - generated_power_W, 0.0)
        battery_request_W = min(battery_request_W, float(phase["battery_power_W_available"]))
        battery_step = battery.update(battery_request_W, duration_s)

        bus_state = bus.solve(
            loads=[ElectricalLoad(name="electric_fans", power_W=requested_load_W)],
            generated_power_W=generated_power_W,
            battery_power_W=max(battery_step.battery_power_W, 0.0),
        )
        power_scale = (
            bus_state.supplied_load_power_W / requested_load_W if requested_load_W > 0.0 else 0.0
        )

        fan_performances = [
            fan.evaluate(
                ElectricFanCommand(
                    mode=fan_mode,
                    airspeed_mps=airspeed_mps,
                    density_kg_m3=atmosphere.density_kg_m3,
                    wing_area_m2=wing_area_m2,
                    input_power_W=requested_per_fan_W * power_scale,
                )
            )
            for _ in range(fan_count)
        ]
        total_fan_input_W = sum(item.input_power_W for item in fan_performances)
        total_fan_shaft_W = sum(item.shaft_power_W for item in fan_performances)
        total_fan_thrust_N = sum(item.thrust_N for item in fan_performances)
        dynamic_pressure_Pa = 0.5 * atmosphere.density_kg_m3 * airspeed_mps**2
        c_mu_proxy = (
            total_fan_thrust_N / (dynamic_pressure_Pa * wing_area_m2)
            if dynamic_pressure_Pa > 0.0
            else 0.0
        )

        shaft_power_extraction_W_per_engine = 0.0
        generator_losses_W = 0.0
        if generated_power_W > 0.0:
            shaft_power_total_W = generated_power_W / generator_cfg["efficiency"]
            generator_losses_W = shaft_power_total_W - generated_power_W
            shaft_power_extraction_W_per_engine = shaft_power_total_W / generator_cfg["engine_count"]
        extraction_result = compute_power_extraction_penalty(
            shaft_power_extraction_W=shaft_power_extraction_W_per_engine,
            mechanical_efficiency=extraction_cfg["mechanical_efficiency"],
            propulsive_power_equivalent_efficiency=extraction_cfg[
                "propulsive_power_equivalent_efficiency"
            ],
            fuel_flow_increment_per_MW_kg_s=extraction_cfg["fuel_flow_increment_per_MW_kg_s"],
            max_extraction_W_per_engine_for_v02=extraction_cfg[
                "max_extraction_W_per_engine_for_v02"
            ],
            flight_speed_mps=airspeed_mps,
        )

        fan_heat_W = sum(item.heat_loss_W for item in fan_performances)
        heat_load_W = fan_heat_W + bus_state.thermal_load_W + generator_losses_W
        thermal_result = thermal.add_heat(heat_load_W, duration_s)
        soc_min = min(battery_step.soc_initial, battery_step.soc_final)
        soc_max = max(battery_step.soc_initial, battery_step.soc_final)

        rows.append(
            {
                "phase": phase["phase"],
                "duration_s": duration_s,
                "airspeed_mps": airspeed_mps,
                "altitude_m": altitude_m,
                "fan_mode": fan_mode,
                "requested_load_W": requested_load_W,
                "generated_power_W": generated_power_W,
                "battery_power_W": battery_step.battery_power_W,
                "battery_unmet_power_W": battery_step.unmet_power_W,
                "supplied_load_W": bus_state.supplied_load_power_W,
                "unmet_load_W": bus_state.unmet_load_W,
                "bus_losses_W": bus_state.distribution_losses_W,
                "total_fan_input_power_W": total_fan_input_W,
                "total_fan_shaft_power_W": total_fan_shaft_W,
                "total_fan_thrust_N": total_fan_thrust_N,
                "c_mu_proxy": c_mu_proxy,
                "soc_initial": battery_step.soc_initial,
                "soc_final": battery_step.soc_final,
                "soc_min": soc_min,
                "soc_max": soc_max,
                "thermal_load_W": thermal_result.heat_load_W,
                "thermal_energy_Wh": thermal_result.heat_energy_Wh,
                "rejected_heat_load_W": thermal_result.rejected_heat_load_W,
                "shaft_power_extraction_W_per_engine": shaft_power_extraction_W_per_engine,
            }
        )
        extraction_rows.append(
            {
                "phase": phase["phase"],
                "generator_power_W_total": generated_power_W,
                "generator_efficiency": generator_cfg["efficiency"],
                "engine_count": generator_cfg["engine_count"],
                "shaft_power_extraction_W_per_engine": shaft_power_extraction_W_per_engine,
                "thrust_penalty_N_per_engine": (
                    extraction_result.equivalent_thrust_penalty_N
                ),
                "fuel_flow_increment_kg_s_per_engine": (
                    extraction_result.additional_fuel_flow_kg_s
                ),
                "heat_load_note": extraction_result.heat_load_note or "",
            }
        )

    return pd.DataFrame(rows), pd.DataFrame(extraction_rows)


def _build_summary(timeline: pd.DataFrame, thermal: ThermalAccumulator) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "phase_count": len(timeline),
                "soc_min": timeline["soc_min"].min(),
                "soc_max": timeline["soc_max"].max(),
                "peak_total_fan_thrust_N": timeline["total_fan_thrust_N"].max(),
                "peak_thermal_load_W": timeline["thermal_load_W"].max(),
                "total_thermal_energy_Wh": thermal.total_heat_energy_Wh,
                "total_unmet_load_Wh": (
                    timeline["unmet_load_W"] * timeline["duration_s"] / 3600.0
                ).sum(),
            }
        ]
    )


def _build_mode_summary(project_config, hybrid: dict, aero_config: dict, fan: ElectricBlownFlapFan) -> pd.DataFrame:
    atmosphere = isa_atmosphere(0.0)
    rows = []
    for mode in ("off", "assist", "degraded", "failed"):
        perf = fan.evaluate(
            ElectricFanCommand(
                mode=mode,
                airspeed_mps=75.0,
                density_kg_m3=atmosphere.density_kg_m3,
                wing_area_m2=aero_config["aero"]["default"]["wing_area_m2"],
            )
        )
        rows.append(
            {
                "mode": mode,
                "input_power_W_per_fan": perf.input_power_W,
                "shaft_power_W_per_fan": perf.shaft_power_W,
                "thrust_N_per_fan": perf.thrust_N,
                "c_mu_proxy_per_fan": perf.blowing_momentum_coefficient,
                "heat_loss_W_per_fan": perf.heat_loss_W,
                "aircraft": project_config.aircraft.name,
            }
        )
    return pd.DataFrame(rows)


def _build_failure_cases(project_config, hybrid: dict, aero_config: dict, fan: ElectricBlownFlapFan) -> pd.DataFrame:
    del project_config
    atmosphere = isa_atmosphere(0.0)
    wing_area_m2 = aero_config["aero"]["default"]["wing_area_m2"]
    rows = []
    for case in hybrid["failure_cases"]:
        performances = [
            fan.evaluate(
                ElectricFanCommand(
                    mode=mode,
                    airspeed_mps=75.0,
                    density_kg_m3=atmosphere.density_kg_m3,
                    wing_area_m2=wing_area_m2,
                )
            )
            for mode in case["fan_modes"]
        ]
        total_thrust_N = sum(item.thrust_N for item in performances)
        dynamic_pressure_Pa = 0.5 * atmosphere.density_kg_m3 * 75.0**2
        rows.append(
            {
                "case_name": case["name"],
                "fan_modes": ";".join(case["fan_modes"]),
                "available_fan_count": sum(mode != "failed" for mode in case["fan_modes"]),
                "total_input_power_W": sum(item.input_power_W for item in performances),
                "total_shaft_power_W": sum(item.shaft_power_W for item in performances),
                "total_fan_thrust_N": total_thrust_N,
                "c_mu_proxy": total_thrust_N / (dynamic_pressure_Pa * wing_area_m2),
            }
        )
    return pd.DataFrame(rows)


def _plot_power_soc(timeline: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax_power = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    x = range(len(timeline))
    ax_power.plot(x, timeline["requested_load_W"] / 1_000_000.0, marker="o", label="Fan load")
    ax_power.plot(x, timeline["generated_power_W"] / 1_000_000.0, marker="s", label="Generator")
    ax_power.plot(x, timeline["battery_power_W"] / 1_000_000.0, marker="^", label="Battery")
    ax_power.set_xticks(list(x), timeline["phase"], rotation=20)
    ax_power.set_ylabel("Power (MW)")
    ax_power.set_xlabel("Phase")
    ax_power.grid(True, alpha=0.3)

    ax_soc = ax_power.twinx()
    ax_soc.plot(x, timeline["soc_final"], color="#d62728", marker="D", label="SOC")
    ax_soc.set_ylabel("Battery SOC (-)")
    lines, labels = ax_power.get_legend_handles_labels()
    lines_2, labels_2 = ax_soc.get_legend_handles_labels()
    ax_power.legend(lines + lines_2, labels + labels_2, loc="best")
    fig.suptitle("Hybrid-Electric Power and SOC")
    fig.tight_layout()
    _save_figure(fig, png_dir / "electric_power_soc.png", svg_dir / "electric_power_soc.svg")
    plt.close(fig)


def _plot_fan_thrust(timeline: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.bar(timeline["phase"], timeline["total_fan_thrust_N"])
    ax.set_xlabel("Phase")
    ax.set_ylabel("Total fan thrust proxy (N)")
    ax.set_title("Electric Fan Thrust Proxy")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "electric_fan_thrust_proxy.png",
        svg_dir / "electric_fan_thrust_proxy.svg",
    )
    plt.close(fig)


def _plot_thermal_load(timeline: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.bar(timeline["phase"], timeline["thermal_load_W"] / 1000.0)
    ax.set_xlabel("Phase")
    ax.set_ylabel("Thermal load (kW)")
    ax.set_title("Hybrid-Electric Lumped Thermal Load")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(fig, png_dir / "hybrid_thermal_load.png", svg_dir / "hybrid_thermal_load.svg")
    plt.close(fig)


def _plot_failure_cases(failure_cases: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
    ax.bar(failure_cases["case_name"], failure_cases["total_input_power_W"] / 1_000_000.0)
    ax.set_xlabel("Failure case")
    ax.set_ylabel("Available fan input power (MW)")
    ax.set_title("Fan Failure Case Power Available")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    _save_figure(
        fig,
        png_dir / "fan_failure_power_available.png",
        svg_dir / "fan_failure_power_available.svg",
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
