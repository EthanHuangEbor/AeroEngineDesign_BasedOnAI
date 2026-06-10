"""Segmented concept mission solver for MTA-VHEP V0.2-04."""

from dataclasses import dataclass
from typing import Any

from mta_vhep.aircraft.aerodynamics import AeroModel, AeroState
from mta_vhep.aircraft.weights import WeightBreakdown, WeightBuildUp
from mta_vhep.core.atmosphere import isa_atmosphere
from mta_vhep.core.units import kg_to_N, km_to_m
from mta_vhep.electrical.battery_buffer import BatteryBuffer
from mta_vhep.electrical.bus import ElectricalBus, ElectricalLoad
from mta_vhep.electrical.inverter import InverterModel
from mta_vhep.electrical.motor import MotorModel
from mta_vhep.interfaces.schemas import FuelProperties, MissionSegment, ProjectConfig
from mta_vhep.mission.segment import MissionSegmentResult
from mta_vhep.propulsion.electric_fan import ElectricBlownFlapFan, ElectricFanCommand
from mta_vhep.propulsion.turbofan_vce import EngineOperatingPoint, VariableCycleTurbofan


@dataclass(frozen=True)
class MissionResult:
    """Mission result for one case using SI units except distance in km."""

    case_name: str
    segment_results: list[MissionSegmentResult]
    weight_breakdown: WeightBreakdown
    block_fuel_kg: float
    reserve_fuel_kg: float
    mission_fuel_kg: float
    start_mass_kg: float
    final_mass_kg: float
    final_fuel_kg: float
    electric_energy_Wh: float
    max_electric_power_W: float
    max_thermal_load_W: float
    constraint_violations: list[str]


@dataclass(frozen=True)
class _ElectricSegmentOutput:
    total_fan_thrust_N: float
    c_mu_proxy: float
    electric_energy_Wh: float
    max_electric_power_W: float
    max_thermal_load_W: float
    soc_start: float | None
    soc_end: float | None
    unmet_electric_load_Wh: float
    shaft_power_extraction_W_per_engine: float
    constraint_flags: list[str]


class SegmentedMissionSolver:
    """Quasi-steady segmented mission solver for concept comparisons."""

    def __init__(
        self,
        project_config: ProjectConfig,
        mission_solver_config: dict[str, Any],
        aero_config: dict[str, Any],
        propulsion_config: dict[str, Any],
        engine_config: dict[str, Any],
        hybrid_config: dict[str, Any],
        fuel: FuelProperties,
    ) -> None:
        self.project_config = project_config
        self.root = _mapping(mission_solver_config, "mission_solver")
        if bool(self.root.get("certification_grade", True)):
            raise ValueError("mission_solver.certification_grade must be false")
        self.segment_defaults = _mapping(self.root, "segment_defaults")
        self.weights_config = _mapping(self.root, "weights")
        self.aero_solver_config = _mapping(self.root, "aero")
        self.numerical = _mapping(self.root, "numerical")
        self.constraints = _mapping(self.root, "constraints")
        self.aero_config = aero_config
        self.propulsion_config = propulsion_config
        self.engine_config = engine_config
        self.hybrid_config = _mapping(hybrid_config, "hybrid_electric")
        self.fuel = fuel
        self.aero_model = AeroModel.from_config(aero_config)
        self.mode_schedules = propulsion_config["propulsion"]["main_engine"]["modes"]

    def run_all_cases(self) -> list[MissionResult]:
        """Run every mission case configured in mission_solver.yaml."""
        return [self.run_case(case) for case in self.root["cases"]]

    def run_case(self, case_config: dict[str, Any]) -> MissionResult:
        """Run one configured mission case and return concept-level outputs."""
        case_name = str(case_config["name"])
        fuel_capacity_kg = _number(
            self.weights_config, "usable_fuel_capacity_kg_assumption"
        )
        total_electric_power_W = (
            self._total_electric_power_W()
            if bool(case_config["hybrid_mass_penalty_enabled"])
            else 0.0
        )
        weight_builder = WeightBuildUp(
            self.weights_config,
            hybrid_config=self.hybrid_config,
            engine_count=self.project_config.main_engine.count,
        )

        fuel_estimate_kg = fuel_capacity_kg
        final_result: MissionResult | None = None
        max_iterations = int(_number(self.numerical, "max_iterations_weight_closure"))
        convergence_fuel_kg = _number(self.numerical, "convergence_fuel_kg")

        for iteration in range(max_iterations):
            weight_breakdown = weight_builder.estimate(
                fuel_kg=fuel_estimate_kg,
                hybrid_mass_penalty_enabled=bool(
                    case_config["hybrid_mass_penalty_enabled"]
                ),
                total_electric_power_W=total_electric_power_W,
            )
            segment_results = self._run_segments(case_config, weight_breakdown)
            block_fuel_kg = sum(item.fuel_burn_kg for item in segment_results)
            reserve_fuel_kg = block_fuel_kg * _number(
                self.segment_defaults, "reserve_fraction_initial"
            )
            mission_fuel_kg = block_fuel_kg + reserve_fuel_kg
            next_fuel_kg = min(mission_fuel_kg, fuel_capacity_kg)
            final_result = self._build_result(
                case_name,
                segment_results,
                weight_breakdown,
                block_fuel_kg,
                reserve_fuel_kg,
                mission_fuel_kg,
                fuel_capacity_kg,
            )
            if (
                abs(next_fuel_kg - fuel_estimate_kg) <= convergence_fuel_kg
                or iteration == max_iterations - 1
            ):
                break
            fuel_estimate_kg = next_fuel_kg

        if final_result is None:
            raise RuntimeError("mission solver did not produce a result")
        return final_result

    def _run_segments(
        self,
        case_config: dict[str, Any],
        weight_breakdown: WeightBreakdown,
    ) -> list[MissionSegmentResult]:
        engine = VariableCycleTurbofan.from_config(
            self.engine_config,
            _engine_variant_key(str(case_config["engine_variant"])),
        )
        electric_enabled = bool(case_config["electric_assist_enabled"])
        fan = self._build_fan() if electric_enabled else None
        battery = self._build_battery() if electric_enabled else None
        bus = self._build_bus() if electric_enabled else None
        current_mass_kg = weight_breakdown.estimated_mtow_kg
        results: list[MissionSegmentResult] = []

        for segment in self.project_config.mission.segments:
            kinematics = self._segment_kinematics(segment)
            electric = self._evaluate_electric_segment(
                segment,
                kinematics["speed_mps"],
                kinematics["duration_s"],
                kinematics["altitude_mid_m"],
                electric_enabled,
                fan,
                battery,
                bus,
            )
            required_thrust_N = self._required_thrust_N(
                segment,
                current_mass_kg,
                kinematics["mach"],
                kinematics["altitude_mid_m"],
                electric.c_mu_proxy,
            )
            engine_perf = self._engine_performance(
                engine,
                case_config,
                segment.engine_rating,
                kinematics["mach"],
                kinematics["altitude_mid_m"],
                electric.shaft_power_extraction_W_per_engine,
            )
            engine_count = self.project_config.main_engine.count
            engine_available_thrust_N = engine_perf.net_thrust_N * engine_count
            available_thrust_N = engine_available_thrust_N + electric.total_fan_thrust_N
            thrust_margin_N = available_thrust_N - required_thrust_N

            segment_flags = list(kinematics["constraint_flags"])
            segment_flags.extend(engine_perf.constraint_flags)
            segment_flags.extend(electric.constraint_flags)
            if thrust_margin_N < _number(self.numerical, "min_net_thrust_margin_N"):
                segment_flags.append("low_thrust_margin")

            fuel_flow_kg_s = self._segment_fuel_flow_kg_s(
                engine,
                case_config,
                segment,
                kinematics["mach"],
                kinematics["altitude_mid_m"],
                engine_perf.fuel_flow_kg_s * engine_count,
                required_thrust_N,
                available_thrust_N,
            )
            fuel_burn_kg = max(fuel_flow_kg_s * kinematics["duration_s"], 0.0)
            end_mass_kg = current_mass_kg - fuel_burn_kg
            results.append(
                MissionSegmentResult(
                    case_name=str(case_config["name"]),
                    segment_name=segment.name,
                    segment_type=segment.segment_type,
                    distance_km=kinematics["distance_km"],
                    duration_s=kinematics["duration_s"],
                    altitude_start_m=segment.altitude_start_m,
                    altitude_end_m=segment.altitude_end_m,
                    mach=kinematics["mach"] if kinematics["mach"] > 0.0 else None,
                    speed_mps=(
                        kinematics["speed_mps"] if kinematics["speed_mps"] > 0.0 else None
                    ),
                    engine_rating=segment.engine_rating,
                    electric_fan_mode=segment.electric_fan_mode,
                    start_mass_kg=current_mass_kg,
                    end_mass_kg=end_mass_kg,
                    fuel_burn_kg=fuel_burn_kg,
                    electric_energy_Wh=electric.electric_energy_Wh,
                    max_electric_power_W=electric.max_electric_power_W,
                    max_thermal_load_W=electric.max_thermal_load_W,
                    average_required_thrust_N=required_thrust_N,
                    available_thrust_N=available_thrust_N,
                    thrust_margin_N=thrust_margin_N,
                    soc_start=electric.soc_start,
                    soc_end=electric.soc_end,
                    unmet_electric_load_Wh=electric.unmet_electric_load_Wh,
                    constraint_flags=sorted(set(segment_flags)),
                )
            )
            current_mass_kg = end_mass_kg

        return results

    def _build_result(
        self,
        case_name: str,
        segment_results: list[MissionSegmentResult],
        weight_breakdown: WeightBreakdown,
        block_fuel_kg: float,
        reserve_fuel_kg: float,
        mission_fuel_kg: float,
        fuel_capacity_kg: float,
    ) -> MissionResult:
        final_mass_kg = segment_results[-1].end_mass_kg
        final_fuel_kg = weight_breakdown.fuel_kg - block_fuel_kg
        electric_energy_Wh = sum(item.electric_energy_Wh for item in segment_results)
        max_electric_power_W = max(item.max_electric_power_W for item in segment_results)
        max_thermal_load_W = max(item.max_thermal_load_W for item in segment_results)
        violations: list[str] = []
        if self.constraints.get("report_fuel_capacity_exceeded", True):
            if mission_fuel_kg > fuel_capacity_kg:
                violations.append("fuel_capacity_exceeded")
        if self.constraints.get("report_negative_final_fuel", True):
            if final_fuel_kg < 0.0:
                violations.append("negative_final_fuel")
        if self.constraints.get("report_soc_below_min", True):
            min_soc = _number(self.hybrid_config["battery_buffer"], "min_soc")
            for item in segment_results:
                if item.soc_end is not None and item.soc_end < min_soc:
                    violations.append("soc_below_min")
                    break
        if self.constraints.get("report_unmet_electric_load", True):
            if any(item.unmet_electric_load_Wh > 0.0 for item in segment_results):
                violations.append("unmet_electric_load")
        if self.constraints.get("report_low_thrust_margin", True):
            if any("low_thrust_margin" in item.constraint_flags for item in segment_results):
                violations.append("low_thrust_margin")
        if any("invalid_segment" in item.constraint_flags for item in segment_results):
            violations.append("invalid_segment")

        return MissionResult(
            case_name=case_name,
            segment_results=segment_results,
            weight_breakdown=weight_breakdown,
            block_fuel_kg=block_fuel_kg,
            reserve_fuel_kg=reserve_fuel_kg,
            mission_fuel_kg=mission_fuel_kg,
            start_mass_kg=weight_breakdown.estimated_mtow_kg,
            final_mass_kg=final_mass_kg,
            final_fuel_kg=final_fuel_kg,
            electric_energy_Wh=electric_energy_Wh,
            max_electric_power_W=max_electric_power_W,
            max_thermal_load_W=max_thermal_load_W,
            constraint_violations=sorted(set(violations)),
        )

    def _evaluate_electric_segment(
        self,
        segment: MissionSegment,
        speed_mps: float,
        duration_s: float,
        altitude_m: float,
        electric_enabled: bool,
        fan: ElectricBlownFlapFan | None,
        battery: BatteryBuffer | None,
        bus: ElectricalBus | None,
    ) -> _ElectricSegmentOutput:
        if (
            not electric_enabled
            or segment.electric_fan_mode == "off"
            or fan is None
            or battery is None
            or bus is None
        ):
            soc = battery.state.soc if battery is not None else None
            return _ElectricSegmentOutput(
                total_fan_thrust_N=0.0,
                c_mu_proxy=0.0,
                electric_energy_Wh=0.0,
                max_electric_power_W=0.0,
                max_thermal_load_W=0.0,
                soc_start=soc,
                soc_end=soc,
                unmet_electric_load_Wh=0.0,
                shaft_power_extraction_W_per_engine=0.0,
                constraint_flags=[],
            )

        atmosphere = isa_atmosphere(altitude_m)
        fan_count = int(_number(self.hybrid_config["electric_fan"], "count"))
        wing_area_m2 = _number(self.aero_config["aero"]["default"], "wing_area_m2")
        bus_config = self.hybrid_config["electrical_bus"]
        generator_config = self.hybrid_config["generator"]
        schedule = self._hybrid_schedule_for_segment(segment)

        requested_per_fan_W = fan.requested_input_power_W(segment.electric_fan_mode)
        requested_load_W = requested_per_fan_W * fan_count
        if requested_load_W <= 0.0:
            soc = battery.state.soc
            return _ElectricSegmentOutput(
                total_fan_thrust_N=0.0,
                c_mu_proxy=0.0,
                electric_energy_Wh=0.0,
                max_electric_power_W=0.0,
                max_thermal_load_W=0.0,
                soc_start=soc,
                soc_end=soc,
                unmet_electric_load_Wh=0.0,
                shaft_power_extraction_W_per_engine=0.0,
                constraint_flags=[],
            )

        generated_power_W = min(
            float(schedule.get("generator_power_W_total", 0.0)),
            _number(bus_config, "max_generator_power_W_total_for_v02"),
        )
        source_required_W = requested_load_W / bus.cable_distribution_efficiency
        battery_request_W = max(source_required_W - generated_power_W, 0.0)
        battery_request_W = min(
            battery_request_W,
            float(schedule.get("battery_power_W_available", 0.0)),
        )
        battery_step = battery.update(battery_request_W, duration_s)
        bus_state = bus.solve(
            loads=[ElectricalLoad(name="mission_electric_fans", power_W=requested_load_W)],
            generated_power_W=generated_power_W,
            battery_power_W=max(battery_step.battery_power_W, 0.0),
        )
        power_scale = bus_state.supplied_load_power_W / requested_load_W

        fan_performances = [
            fan.evaluate(
                ElectricFanCommand(
                    mode=segment.electric_fan_mode,
                    airspeed_mps=speed_mps,
                    density_kg_m3=atmosphere.density_kg_m3,
                    wing_area_m2=wing_area_m2,
                    input_power_W=requested_per_fan_W * power_scale,
                )
            )
            for _ in range(fan_count)
        ]
        total_fan_thrust_N = sum(item.thrust_N for item in fan_performances)
        dynamic_pressure_Pa = 0.5 * atmosphere.density_kg_m3 * speed_mps**2
        c_mu_proxy = (
            total_fan_thrust_N / (dynamic_pressure_Pa * wing_area_m2)
            if dynamic_pressure_Pa > 0.0
            else 0.0
        )
        generator_losses_W = 0.0
        shaft_power_extraction_W_per_engine = 0.0
        if generated_power_W > 0.0:
            shaft_power_total_W = generated_power_W / _number(generator_config, "efficiency")
            generator_losses_W = shaft_power_total_W - generated_power_W
            shaft_power_extraction_W_per_engine = shaft_power_total_W / _number(
                generator_config, "engine_count"
            )
        fan_heat_W = sum(item.heat_loss_W for item in fan_performances)
        thermal_load_W = fan_heat_W + bus_state.thermal_load_W + generator_losses_W

        flags: list[str] = []
        unmet_electric_load_Wh = bus_state.unmet_load_W * duration_s / 3600.0
        if unmet_electric_load_Wh > 0.0:
            flags.append("unmet_electric_load")

        return _ElectricSegmentOutput(
            total_fan_thrust_N=total_fan_thrust_N,
            c_mu_proxy=c_mu_proxy,
            electric_energy_Wh=bus_state.supplied_load_power_W * duration_s / 3600.0,
            max_electric_power_W=bus_state.supplied_load_power_W,
            max_thermal_load_W=thermal_load_W,
            soc_start=battery_step.soc_initial,
            soc_end=battery_step.soc_final,
            unmet_electric_load_Wh=unmet_electric_load_Wh,
            shaft_power_extraction_W_per_engine=shaft_power_extraction_W_per_engine,
            constraint_flags=flags,
        )

    def _required_thrust_N(
        self,
        segment: MissionSegment,
        mass_kg: float,
        mach: float,
        altitude_m: float,
        c_mu_proxy: float,
    ) -> float:
        if segment.segment_type == "taxi":
            return 0.0

        atmosphere = isa_atmosphere(altitude_m)
        weight_N = kg_to_N(mass_kg)
        flap_mode = _flap_mode(segment.segment_type)
        aero = self.aero_model.evaluate(
            AeroState(
                mach=max(mach, 0.03),
                altitude_m=altitude_m,
                weight_N=weight_N,
                wing_area_m2=_number(self.aero_config["aero"]["default"], "wing_area_m2"),
                flap_mode=flap_mode,
                gear_down=segment.segment_type in ("takeoff", "approach"),
                blowing_momentum_coefficient=min(
                    c_mu_proxy,
                    _number(self.aero_config["aero"]["blowing"], "cmu_max_for_v02"),
                ),
            ),
            atmosphere,
        )
        ld_ratio = aero.ld_ratio
        if segment.segment_type == "cruise":
            override = self.aero_solver_config.get("cruise_ld_override")
            if override is not None:
                ld_ratio = float(override)
            return weight_N / max(ld_ratio, 1.0e-6)
        if segment.segment_type == "climb":
            climb_drag_N = weight_N / max(
                ld_ratio * _number(self.aero_solver_config, "climb_ld_factor"),
                1.0e-6,
            )
            return climb_drag_N + 0.025 * weight_N
        if segment.segment_type == "descent":
            return (weight_N / max(ld_ratio, 1.0e-6)) * _number(
                self.aero_solver_config, "descent_ld_factor"
            )
        if segment.segment_type == "approach":
            return weight_N / max(
                ld_ratio * _number(self.aero_solver_config, "approach_ld_factor"),
                1.0e-6,
            )
        if segment.segment_type == "takeoff":
            return max(weight_N / max(ld_ratio, 1.0e-6), 0.16 * weight_N)
        return weight_N / max(ld_ratio, 1.0e-6)

    def _segment_fuel_flow_kg_s(
        self,
        engine: VariableCycleTurbofan,
        case_config: dict[str, Any],
        segment: MissionSegment,
        mach: float,
        altitude_m: float,
        total_engine_fuel_flow_at_rating_kg_s: float,
        required_thrust_N: float,
        available_thrust_N: float,
    ) -> float:
        if segment.segment_type == "taxi":
            return (
                total_engine_fuel_flow_at_rating_kg_s
                * _number(self.segment_defaults, "taxi_fuel_flow_fraction_idle")
            )
        if segment.segment_type == "descent":
            cruise = self._engine_performance(
                engine,
                case_config,
                "cruise",
                max(mach, 0.30),
                altitude_m,
                0.0,
            )
            return (
                cruise.fuel_flow_kg_s
                * self.project_config.main_engine.count
                * _number(self.segment_defaults, "descent_fuel_flow_fraction_cruise")
            )

        ratio = required_thrust_N / available_thrust_N if available_thrust_N > 0.0 else 1.0
        idle_floor = engine.rating_throttle_floor.get(segment.engine_rating, 0.08)
        fuel_flow_kg_s = (
            min(max(ratio, idle_floor), 1.0) * total_engine_fuel_flow_at_rating_kg_s
        )
        if segment.segment_type == "approach":
            takeoff = self._engine_performance(
                engine,
                case_config,
                "takeoff",
                max(mach, 0.15),
                altitude_m,
                0.0,
            )
            approach_floor_kg_s = (
                takeoff.fuel_flow_kg_s
                * self.project_config.main_engine.count
                * _number(self.segment_defaults, "approach_fuel_flow_fraction_takeoff")
            )
            fuel_flow_kg_s = max(fuel_flow_kg_s, approach_floor_kg_s)
        return fuel_flow_kg_s

    def _engine_performance(
        self,
        engine: VariableCycleTurbofan,
        case_config: dict[str, Any],
        rating: str,
        mach: float,
        altitude_m: float,
        shaft_power_extraction_W: float,
    ):
        schedule = self.mode_schedules.get(rating, {})
        adaptive_enabled = bool(case_config["adaptive_third_stream_enabled"])
        op = EngineOperatingPoint(
            mach=max(mach, 0.0),
            altitude_m=altitude_m,
            throttle=float(schedule.get("throttle", engine.rating_throttle_floor[rating])),
            rating=rating,
            shaft_power_extraction_W=shaft_power_extraction_W,
            third_stream_schedule=(
                float(schedule.get("third_stream_schedule", 0.0)) if adaptive_enabled else 0.0
            ),
            variable_nozzle_schedule=(
                float(schedule.get("variable_nozzle_schedule", 0.0))
                if adaptive_enabled
                else 0.0
            ),
            fuel=self.fuel,
        )
        return engine.evaluate(op)

    def _segment_kinematics(self, segment: MissionSegment) -> dict[str, Any]:
        altitude_mid_m = 0.5 * (segment.altitude_start_m + segment.altitude_end_m)
        atmosphere = isa_atmosphere(altitude_mid_m)
        flags: list[str] = []
        if segment.speed_mps is not None:
            speed_mps = segment.speed_mps
            mach = speed_mps / atmosphere.speed_of_sound_mps
        elif segment.mach is not None:
            mach = segment.mach
            speed_mps = mach * atmosphere.speed_of_sound_mps
        else:
            mach = 0.0
            speed_mps = 0.0

        distance_km = float(segment.distance_km or 0.0)
        if segment.duration_s is not None:
            duration_s = segment.duration_s
        elif distance_km > 0.0 and speed_mps > 0.0:
            duration_s = km_to_m(distance_km) / speed_mps
        else:
            duration_s = _number(self.numerical, "min_segment_duration_s")
            flags.append("invalid_segment")
        duration_s = max(duration_s, _number(self.numerical, "min_segment_duration_s"))

        return {
            "altitude_mid_m": altitude_mid_m,
            "mach": mach,
            "speed_mps": speed_mps,
            "distance_km": distance_km,
            "duration_s": duration_s,
            "constraint_flags": flags,
        }

    def _hybrid_schedule_for_segment(self, segment: MissionSegment) -> dict[str, Any]:
        key_by_segment = {
            "takeoff": "takeoff",
            "climb": "initial_climb",
            "cruise": "cruise",
            "descent": "cruise",
            "approach": "approach",
            "taxi": "cruise",
        }
        phase = key_by_segment.get(segment.segment_type, "cruise")
        for schedule in self.hybrid_config["operation_schedule"]:
            if schedule["phase"] == phase:
                return schedule
        return {}

    def _build_fan(self) -> ElectricBlownFlapFan:
        fan_config = self.hybrid_config["electric_fan"]
        motor = MotorModel(
            efficiency=_number(self.hybrid_config["motor"], "efficiency"),
            specific_power_kW_per_kg=_number(
                self.hybrid_config["motor"], "specific_power_kW_per_kg"
            ),
        )
        inverter = InverterModel(
            efficiency=_number(self.hybrid_config["inverter"], "efficiency"),
            specific_power_kW_per_kg=_number(
                self.hybrid_config["inverter"], "specific_power_kW_per_kg"
            ),
        )
        return ElectricBlownFlapFan(
            nominal_power_W=_number(fan_config, "nominal_power_W_per_fan"),
            max_power_W_for_v02=_number(fan_config, "max_power_W_per_fan_for_v02"),
            propulsive_efficiency=_number(fan_config, "propulsive_efficiency"),
            min_effective_airspeed_mps=_number(
                fan_config, "min_effective_airspeed_mps"
            ),
            mode_power_fractions={
                mode: _number(data, "power_fraction")
                for mode, data in fan_config["modes"].items()
            },
            motor=motor,
            inverter=inverter,
        )

    def _build_battery(self) -> BatteryBuffer:
        battery = self.hybrid_config["battery_buffer"]
        bus = self.hybrid_config["electrical_bus"]
        return BatteryBuffer(
            capacity_Wh=_number(battery, "capacity_Wh"),
            initial_soc=_number(battery, "initial_soc"),
            min_soc=_number(battery, "min_soc"),
            max_soc=_number(battery, "max_soc"),
            max_discharge_power_W=_number(bus, "max_battery_discharge_power_W"),
            max_charge_power_W=_number(bus, "max_battery_charge_power_W"),
            roundtrip_efficiency=_number(battery, "roundtrip_efficiency"),
        )

    def _build_bus(self) -> ElectricalBus:
        bus = self.hybrid_config["electrical_bus"]
        return ElectricalBus(
            voltage_V=_number(bus, "voltage_V"),
            cable_distribution_efficiency=_number(bus, "cable_distribution_efficiency"),
            load_shedding_enabled=bool(bus["load_shedding_enabled"]),
        )

    def _total_electric_power_W(self) -> float:
        fan = self.hybrid_config["electric_fan"]
        return _number(fan, "count") * _number(fan, "nominal_power_W_per_fan")


def _engine_variant_key(engine_variant: str) -> str:
    if engine_variant == "baseline_fixed_cycle_turbofan":
        return "baseline_fixed_cycle"
    if engine_variant == "three_stream_variable_cycle_turbofan":
        return "adaptive_cycle"
    raise ValueError(f"Unsupported engine variant: {engine_variant}")


def _flap_mode(segment_type: str) -> str:
    if segment_type == "takeoff":
        return "takeoff_flap"
    if segment_type == "approach":
        return "landing_flap"
    return "clean"


def _mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def _number(data: dict[str, Any], key: str) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")
    return float(value)
