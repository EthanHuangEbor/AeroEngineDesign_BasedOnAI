"""Sensitivity analysis runner for MTA-VHEP V0.2-05."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import pandas as pd

from mta_vhep.aircraft.aerodynamics import AeroModel, AeroState
from mta_vhep.core.atmosphere import isa_atmosphere
from mta_vhep.core.units import kg_to_N
from mta_vhep.interfaces.schemas import FuelProperties, ProjectConfig
from mta_vhep.mission.approach_analysis import (
    ApproachForceBalanceInput,
    evaluate_approach_force_balance,
)
from mta_vhep.mission.mission_solver import MissionResult, SegmentedMissionSolver
from mta_vhep.mission.segment import MissionSegmentResult
from mta_vhep.mission.takeoff_landing import (
    landing_performance_proxy,
    takeoff_performance_proxy,
)


BASELINE_FIXED_CASE = "baseline_fixed_cycle_turbofan"
HYBRID_CASE = "adaptive_cycle_plus_hybrid_electric"


@dataclass(frozen=True)
class SensitivityParameter:
    """One sensitivity parameter and candidate values."""

    name: str
    values: list[float]
    baseline_value: float | None


@dataclass(frozen=True)
class SensitivityCaseResult:
    """Sensitivity row summary using SI units except dimensionless ratios."""

    case_id: str
    case_family: str
    changed_parameter: str
    changed_value: str
    propulsion_case: str
    mission_fuel_kg: float
    fuel_delta_vs_baseline_pct: float
    estimated_mtow_kg: float
    mtow_margin_to_upper_kg: float
    min_thrust_margin_N: float
    min_thrust_margin_ratio: float
    unmet_electric_load_Wh: float
    takeoff_proxy_index: float
    landing_proxy_index: float
    constraint_count: int
    conclusion_status: str


class SensitivityRunner:
    """Run V0.2-05 one-at-a-time and selected-grid sensitivity cases."""

    def __init__(
        self,
        project_config: ProjectConfig,
        sensitivity_config: dict[str, Any],
        mission_solver_config: dict[str, Any],
        aero_config: dict[str, Any],
        propulsion_config: dict[str, Any],
        engine_config: dict[str, Any],
        hybrid_config: dict[str, Any],
        fuel: FuelProperties,
    ) -> None:
        self.project_config = project_config
        self.sensitivity_root = sensitivity_config["sensitivity"]
        if bool(self.sensitivity_root.get("certification_grade", True)):
            raise ValueError("sensitivity.certification_grade must be false")
        self.mission_solver_config = mission_solver_config
        self.aero_config = aero_config
        self.propulsion_config = propulsion_config
        self.engine_config = engine_config
        self.hybrid_config = hybrid_config
        self.fuel = fuel
        self._baseline_fixed_fuel_kg: float | None = None

    def run(self) -> dict[str, pd.DataFrame]:
        """Run configured sensitivity cases and return result DataFrames."""
        case_rows: list[dict[str, Any]] = []
        detail_rows: list[dict[str, Any]] = []
        constraint_rows: list[dict[str, Any]] = []
        counter = 1

        for family, settings, propulsion_filter in self._case_settings():
            case_id_base = f"V05-{counter:04d}"
            counter += 1
            results, configs = self._run_settings(settings)
            rows = self._result_rows(case_id_base, family, settings, results, configs)
            for row_bundle in rows:
                if propulsion_filter is not None and row_bundle["propulsion_case"] != propulsion_filter:
                    continue
                case_rows.append(row_bundle["summary"])
                detail_rows.append(row_bundle["details"])
                constraint_rows.extend(row_bundle["constraints"])

        summary = pd.DataFrame(case_rows)
        details = pd.DataFrame(detail_rows)
        constraints = pd.DataFrame(constraint_rows)
        tornado = self._tornado_data(summary)
        best = self._best_candidates(summary, details)

        return {
            "summary": summary,
            "details": details,
            "constraints": constraints,
            "best_candidates": best,
            "tornado": tornado,
        }

    def _case_settings(self) -> list[tuple[str, dict[str, float], str | None]]:
        settings: list[tuple[str, dict[str, float], str | None]] = [
            ("baseline", {}, None)
        ]
        variables = self._parameters()

        if self.sensitivity_root["strategy"]["one_at_a_time_enabled"]:
            for parameter in variables:
                for value in parameter.values:
                    if parameter.baseline_value is not None and value == parameter.baseline_value:
                        continue
                    settings.append(("one_at_a_time", {parameter.name: value}, None))

        if self.sensitivity_root["strategy"]["selected_grid_enabled"]:
            thrust_values = [115000.0, 130000.0, 150000.0]
            cruise_ld_values = [15.0, 18.0]
            electric_power_values = [0.0, 4000000.0, 8000000.0]
            battery_values = [250000.0, 1000000.0]
            generator_values = [2000000.0, 6000000.0]
            hybrid_mass_values = [150.0, 400.0]
            for thrust in thrust_values:
                for cruise_ld in cruise_ld_values:
                    for power in electric_power_values:
                        for battery in battery_values:
                            for generator in generator_values:
                                for mass_per_mw in hybrid_mass_values:
                                    settings.append(
                                        (
                                            "selected_grid",
                                            {
                                                "sea_level_static_thrust_N_per_engine": thrust,
                                                "cruise_ld": cruise_ld,
                                                "total_electric_power_W": power,
                                                "battery_capacity_Wh": battery,
                                                "max_generator_power_W_total": generator,
                                                "hybrid_mass_per_MW_kg": mass_per_mw,
                                            },
                                            HYBRID_CASE,
                                        )
                                    )

        max_cases = int(self.sensitivity_root["strategy"]["max_cases_for_v05"])
        estimated_rows = 0
        limited: list[tuple[str, dict[str, float], str | None]] = []
        for family, case_settings, propulsion_filter in settings:
            row_count = 1 if propulsion_filter else len(self.mission_solver_config["mission_solver"]["cases"])
            if estimated_rows + row_count > max_cases:
                break
            limited.append((family, case_settings, propulsion_filter))
            estimated_rows += row_count
        return limited

    def _parameters(self) -> list[SensitivityParameter]:
        variables = self.sensitivity_root["design_variables"]
        baseline_values = {
            "sea_level_static_thrust_N_per_engine": 115000.0,
            "cruise_tsfc_multiplier": 1.0,
            "cruise_ld": None,
            "mtow_upper_kg": 95000.0,
            "total_electric_power_W": 4000000.0,
            "battery_capacity_Wh": 500000.0,
            "max_generator_power_W_total": 6000000.0,
            "hybrid_mass_per_MW_kg": 250.0,
            "blown_flap_clmax_increment_fraction": 0.0,
            "approach_descent_angle_deg": -3.0,
        }
        return [
            SensitivityParameter(
                name=name,
                values=[float(value) for value in data["values"]],
                baseline_value=baseline_values[name],
            )
            for name, data in variables.items()
        ]

    def _run_settings(
        self,
        settings: dict[str, float],
    ) -> tuple[list[MissionResult], dict[str, dict[str, Any]]]:
        configs = {
            "mission_solver": deepcopy(self.mission_solver_config),
            "aero": deepcopy(self.aero_config),
            "propulsion": deepcopy(self.propulsion_config),
            "engine": deepcopy(self.engine_config),
            "hybrid": deepcopy(self.hybrid_config),
        }
        self._apply_settings(configs, settings)
        solver = SegmentedMissionSolver(
            project_config=self.project_config,
            mission_solver_config=configs["mission_solver"],
            aero_config=configs["aero"],
            propulsion_config=configs["propulsion"],
            engine_config=configs["engine"],
            hybrid_config=configs["hybrid"],
            fuel=self.fuel,
        )
        return solver.run_all_cases(), configs

    def _apply_settings(self, configs: dict[str, dict[str, Any]], settings: dict[str, float]) -> None:
        engine_root = configs["engine"]["engine_surrogate"]
        mission_root = configs["mission_solver"]["mission_solver"]
        hybrid_root = configs["hybrid"]["hybrid_electric"]
        aero_root = configs["aero"]["aero"]

        if "sea_level_static_thrust_N_per_engine" in settings:
            thrust = settings["sea_level_static_thrust_N_per_engine"]
            engine_root["baseline_fixed_cycle"]["sea_level_static_thrust_N_per_engine"] = thrust
            engine_root["adaptive_cycle"]["sea_level_static_thrust_N_per_engine"] = thrust

        if "cruise_tsfc_multiplier" in settings:
            multiplier = settings["cruise_tsfc_multiplier"]
            engine_root["baseline_fixed_cycle"]["reference_tsfc_kg_per_N_s"]["cruise"] *= multiplier
            engine_root["adaptive_cycle"]["reference_tsfc_kg_per_N_s"]["cruise"] *= multiplier

        if "cruise_ld" in settings:
            mission_root["aero"]["cruise_ld_override"] = settings["cruise_ld"]

        if "mtow_upper_kg" in settings:
            mission_root["weights"]["mtow_range_upper_kg"] = settings["mtow_upper_kg"]

        if "total_electric_power_W" in settings:
            fan_count = float(hybrid_root["electric_fan"]["count"])
            nominal_per_fan = settings["total_electric_power_W"] / fan_count
            hybrid_root["electric_fan"]["nominal_power_W_per_fan"] = nominal_per_fan
            hybrid_root["electric_fan"]["max_power_W_per_fan_for_v02"] = max(
                nominal_per_fan,
                hybrid_root["electric_fan"]["max_power_W_per_fan_for_v02"],
            )

        if "battery_capacity_Wh" in settings:
            hybrid_root["battery_buffer"]["capacity_Wh"] = settings["battery_capacity_Wh"]

        if "max_generator_power_W_total" in settings:
            hybrid_root["electrical_bus"]["max_generator_power_W_total_for_v02"] = settings[
                "max_generator_power_W_total"
            ]

        if "hybrid_mass_per_MW_kg" in settings:
            mission_root["weights"]["hybrid_mass_per_MW_kg"] = settings[
                "hybrid_mass_per_MW_kg"
            ]

        if "blown_flap_clmax_increment_fraction" in settings:
            base = self.aero_config["aero"]["blowing"]["clmax_increment_per_cmu"]
            aero_root["blowing"]["clmax_increment_per_cmu"] = base * (
                1.0 + settings["blown_flap_clmax_increment_fraction"]
            )

        if "approach_descent_angle_deg" in settings:
            configs["mission_solver"]["approach_landing_model"][
                "default_descent_angle_deg"
            ] = settings["approach_descent_angle_deg"]

        if (
            "total_electric_power_W" in settings
            or "max_generator_power_W_total" in settings
        ):
            self._reschedule_generator_power(configs)

    def _reschedule_generator_power(self, configs: dict[str, dict[str, Any]]) -> None:
        hybrid_root = configs["hybrid"]["hybrid_electric"]
        fan = hybrid_root["electric_fan"]
        bus = hybrid_root["electrical_bus"]
        extraction_limit_total_W = (
            configs["engine"]["engine_surrogate"]["shaft_power_extraction"][
                "max_extraction_W_per_engine_for_v02"
            ]
            * hybrid_root["generator"]["efficiency"]
            * hybrid_root["generator"]["engine_count"]
        )
        max_generator_W = min(
            bus["max_generator_power_W_total_for_v02"],
            extraction_limit_total_W,
        )
        for phase in hybrid_root["operation_schedule"]:
            mode = phase["fan_mode"]
            mode_fraction = fan["modes"][mode]["power_fraction"]
            requested_load_W = fan["nominal_power_W_per_fan"] * fan["count"] * mode_fraction
            phase["generator_power_W_total"] = min(max_generator_W, requested_load_W)

    def _result_rows(
        self,
        case_id_base: str,
        case_family: str,
        settings: dict[str, float],
        results: list[MissionResult],
        configs: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        baseline_fixed = next(
            result for result in results if result.case_name == BASELINE_FIXED_CASE
        )
        if self._baseline_fixed_fuel_kg is None and case_family == "baseline":
            self._baseline_fixed_fuel_kg = baseline_fixed.mission_fuel_kg
        baseline_fuel = self._baseline_fixed_fuel_kg or baseline_fixed.mission_fuel_kg

        bundles = []
        for result in results:
            case_id = f"{case_id_base}_{_case_slug(result.case_name)}"
            takeoff_proxy, landing_proxy = self._proxy_indices(result, configs["aero"])
            margin_rows = [
                self._sensitivity_margin_row(segment, configs)
                for segment in result.segment_results
                if segment.average_required_thrust_N > 0.0
            ]
            min_margin_row = min(
                margin_rows,
                key=lambda item: item["thrust_margin_N"],
            )
            unmet_electric_load_Wh = sum(
                segment.unmet_electric_load_Wh for segment in result.segment_results
            )
            constraints = self._constraint_rows(case_id, result)
            constraint_count = len(constraints)
            conclusion_status = self._conclusion_status(
                result,
                unmet_electric_load_Wh,
                result.weight_breakdown.mtow_margin_to_upper_kg,
            )
            changed_parameter, changed_value = _changed_parameter_text(settings)
            summary = SensitivityCaseResult(
                case_id=case_id,
                case_family=case_family,
                changed_parameter=changed_parameter,
                changed_value=changed_value,
                propulsion_case=result.case_name,
                mission_fuel_kg=result.mission_fuel_kg,
                fuel_delta_vs_baseline_pct=(
                    (result.mission_fuel_kg - baseline_fuel) / baseline_fuel * 100.0
                ),
                estimated_mtow_kg=result.weight_breakdown.estimated_mtow_kg,
                mtow_margin_to_upper_kg=result.weight_breakdown.mtow_margin_to_upper_kg,
                min_thrust_margin_N=min_margin_row["thrust_margin_N"],
                min_thrust_margin_ratio=(
                    min_margin_row["thrust_margin_N"]
                    / min_margin_row["required_thrust_N"]
                ),
                unmet_electric_load_Wh=unmet_electric_load_Wh,
                takeoff_proxy_index=takeoff_proxy,
                landing_proxy_index=landing_proxy,
                constraint_count=constraint_count,
                conclusion_status=conclusion_status,
            )
            details = self._details_row(
                case_id,
                case_family,
                settings,
                result,
                configs,
                str(min_margin_row["segment_name"]),
            )
            bundles.append(
                {
                    "propulsion_case": result.case_name,
                    "summary": summary.__dict__,
                    "details": details,
                    "constraints": constraints,
                }
            )
        return bundles

    def _sensitivity_margin_row(
        self,
        segment: MissionSegmentResult,
        configs: dict[str, dict[str, Any]],
    ) -> dict[str, float | str]:
        if segment.segment_type != "approach":
            return {
                "segment_name": segment.segment_name,
                "required_thrust_N": segment.average_required_thrust_N,
                "thrust_margin_N": segment.thrust_margin_N,
            }

        approach_config = configs["mission_solver"].get("approach_landing_model", {})
        if not bool(approach_config.get("allow_descent_force_balance", False)):
            return {
                "segment_name": segment.segment_name,
                "required_thrust_N": segment.average_required_thrust_N,
                "thrust_margin_N": segment.thrust_margin_N,
            }

        drag_N = self._approach_drag_N(segment, configs["aero"])
        result = evaluate_approach_force_balance(
            ApproachForceBalanceInput(
                case_name=segment.case_name,
                segment_name=segment.segment_name,
                weight_N=kg_to_N(segment.start_mass_kg),
                speed_mps=float(segment.speed_mps or 0.0),
                altitude_m=0.5
                * (segment.altitude_start_m + segment.altitude_end_m),
                gamma_deg=float(approach_config["default_descent_angle_deg"]),
                drag_N=drag_N,
                available_thrust_N=segment.available_thrust_N,
                electric_thrust_proxy_N=segment.electric_thrust_proxy_N,
                include_weight_component_along_path=bool(
                    approach_config.get("include_weight_component_along_path", True)
                ),
            )
        )
        return {
            "segment_name": segment.segment_name,
            "required_thrust_N": result.required_thrust_descent_N,
            "thrust_margin_N": result.thrust_margin_descent_N,
        }

    def _approach_drag_N(
        self,
        segment: MissionSegmentResult,
        aero_config: dict[str, Any],
    ) -> float:
        altitude_m = 0.5 * (segment.altitude_start_m + segment.altitude_end_m)
        atmosphere = isa_atmosphere(altitude_m)
        speed_mps = float(segment.speed_mps or 0.0)
        mach = speed_mps / atmosphere.speed_of_sound_mps
        wing_area_m2 = float(aero_config["aero"]["default"]["wing_area_m2"])
        model = AeroModel.from_config(aero_config)
        blowing = aero_config["aero"]["blowing"]
        c_mu = min(
            max(segment.blowing_momentum_coefficient, 0.0),
            float(blowing["cmu_max_for_v02"]),
        )
        performance = model.evaluate(
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
        return dynamic_pressure_Pa * wing_area_m2 * performance.cd

    def _constraint_rows(self, case_id: str, result: MissionResult) -> list[dict[str, Any]]:
        rows = []
        for flag in result.constraint_violations:
            rows.append(
                {
                    "case_id": case_id,
                    "propulsion_case": result.case_name,
                    "scope": "mission",
                    "segment_name": "",
                    "constraint_flag": flag,
                    "value": 1.0,
                    "threshold": 0.0,
                }
            )
        for segment in result.segment_results:
            for flag in segment.constraint_flags:
                value = (
                    segment.thrust_margin_N
                    if flag == "low_thrust_margin"
                    else segment.unmet_electric_load_Wh
                )
                rows.append(
                    {
                        "case_id": case_id,
                        "propulsion_case": result.case_name,
                        "scope": "segment",
                        "segment_name": segment.segment_name,
                        "constraint_flag": flag,
                        "value": value,
                        "threshold": 0.0,
                    }
                )
        return rows

    def _conclusion_status(
        self,
        result: MissionResult,
        unmet_electric_load_Wh: float,
        mtow_margin_to_upper_kg: float,
    ) -> str:
        scoring = self.sensitivity_root["scoring"]
        if scoring["reject_if_low_thrust_margin"] and "low_thrust_margin" in result.constraint_violations:
            return "rejected_low_thrust_margin"
        if scoring["reject_if_unmet_electric_load"] and unmet_electric_load_Wh > 0.0:
            return "rejected_unmet_electric_load"
        if scoring["reject_if_above_mtow_upper"] and mtow_margin_to_upper_kg < 0.0:
            return "rejected_above_mtow_upper"
        return "candidate_for_sensitivity_study"

    def _details_row(
        self,
        case_id: str,
        case_family: str,
        settings: dict[str, float],
        result: MissionResult,
        configs: dict[str, dict[str, Any]],
        min_margin_segment_name: str,
    ) -> dict[str, Any]:
        variables = self._current_design_variables(configs)
        return {
            "case_id": case_id,
            "case_family": case_family,
            "propulsion_case": result.case_name,
            "design_variable_summary": _settings_summary(settings),
            "min_margin_segment_name": min_margin_segment_name,
            **variables,
        }

    def _current_design_variables(self, configs: dict[str, dict[str, Any]]) -> dict[str, float]:
        hybrid = configs["hybrid"]["hybrid_electric"]
        mission = configs["mission_solver"]["mission_solver"]
        engine = configs["engine"]["engine_surrogate"]
        aero = configs["aero"]["aero"]
        base_blowing = self.aero_config["aero"]["blowing"]["clmax_increment_per_cmu"]
        return {
            "sea_level_static_thrust_N_per_engine": engine["adaptive_cycle"][
                "sea_level_static_thrust_N_per_engine"
            ],
            "cruise_tsfc_multiplier": (
                engine["adaptive_cycle"]["reference_tsfc_kg_per_N_s"]["cruise"]
                / self.engine_config["engine_surrogate"]["adaptive_cycle"][
                    "reference_tsfc_kg_per_N_s"
                ]["cruise"]
            ),
            "cruise_ld": mission["aero"]["cruise_ld_override"] or 0.0,
            "mtow_upper_kg": mission["weights"]["mtow_range_upper_kg"],
            "total_electric_power_W": hybrid["electric_fan"]["nominal_power_W_per_fan"]
            * hybrid["electric_fan"]["count"],
            "battery_capacity_Wh": hybrid["battery_buffer"]["capacity_Wh"],
            "max_generator_power_W_total": hybrid["electrical_bus"][
                "max_generator_power_W_total_for_v02"
            ],
            "hybrid_mass_per_MW_kg": mission["weights"]["hybrid_mass_per_MW_kg"],
            "blown_flap_clmax_increment_fraction": (
                aero["blowing"]["clmax_increment_per_cmu"] / base_blowing - 1.0
            ),
            "approach_descent_angle_deg": configs["mission_solver"][
                "approach_landing_model"
            ]["default_descent_angle_deg"],
        }

    def _proxy_indices(
        self,
        result: MissionResult,
        aero_config: dict[str, Any],
    ) -> tuple[float, float]:
        atmosphere = isa_atmosphere(0.0)
        wing_area_m2 = aero_config["aero"]["default"]["wing_area_m2"]
        takeoff_segment = next(
            segment for segment in result.segment_results if segment.segment_type == "takeoff"
        )
        approach_segment = next(
            segment for segment in result.segment_results if segment.segment_type == "approach"
        )
        takeoff_clmax = _effective_clmax(
            aero_config["aero"]["clmax"]["takeoff_flap"],
            takeoff_segment.blowing_momentum_coefficient,
            aero_config["aero"]["blowing"],
        )
        landing_clmax = _effective_clmax(
            aero_config["aero"]["clmax"]["landing_flap"],
            approach_segment.blowing_momentum_coefficient,
            aero_config["aero"]["blowing"],
        )
        takeoff = takeoff_performance_proxy(
            weight_N=kg_to_N(takeoff_segment.start_mass_kg),
            density_kg_m3=atmosphere.density_kg_m3,
            wing_area_m2=wing_area_m2,
            clmax=takeoff_clmax,
            effective_thrust_N=takeoff_segment.available_thrust_N,
        )
        landing = landing_performance_proxy(
            weight_N=kg_to_N(approach_segment.end_mass_kg),
            density_kg_m3=atmosphere.density_kg_m3,
            wing_area_m2=wing_area_m2,
            clmax=landing_clmax,
            effective_thrust_N=approach_segment.available_thrust_N,
        )
        return takeoff.field_length_index, landing.field_length_index

    def _tornado_data(self, summary: pd.DataFrame) -> pd.DataFrame:
        rows = []
        baseline = summary[summary["case_family"] == "baseline"]
        baseline_by_case = baseline.set_index("propulsion_case")
        for parameter, group in summary[summary["case_family"] == "one_at_a_time"].groupby(
            "changed_parameter"
        ):
            for propulsion_case, subset in group.groupby("propulsion_case"):
                if propulsion_case not in baseline_by_case.index:
                    continue
                base = baseline_by_case.loc[propulsion_case]
                rows.append(
                    {
                        "changed_parameter": parameter,
                        "propulsion_case": propulsion_case,
                        "min_mission_fuel_delta_kg": (
                            subset["mission_fuel_kg"].min() - base["mission_fuel_kg"]
                        ),
                        "max_mission_fuel_delta_kg": (
                            subset["mission_fuel_kg"].max() - base["mission_fuel_kg"]
                        ),
                        "min_thrust_margin_delta_N": (
                            subset["min_thrust_margin_N"].min()
                            - base["min_thrust_margin_N"]
                        ),
                        "max_thrust_margin_delta_N": (
                            subset["min_thrust_margin_N"].max()
                            - base["min_thrust_margin_N"]
                        ),
                        "max_abs_fuel_delta_pct": max(
                            abs(subset["fuel_delta_vs_baseline_pct"].min()),
                            abs(subset["fuel_delta_vs_baseline_pct"].max()),
                        ),
                    }
                )
        return pd.DataFrame(rows)

    def _best_candidates(self, summary: pd.DataFrame, details: pd.DataFrame) -> pd.DataFrame:
        merged = summary.merge(
            details[["case_id", "design_variable_summary"]],
            on="case_id",
            how="left",
        )
        ordered = merged.sort_values(
            by=[
                "constraint_count",
                "unmet_electric_load_Wh",
                "min_thrust_margin_N",
                "mission_fuel_kg",
                "takeoff_proxy_index",
            ],
            ascending=[True, True, False, True, True],
        ).head(10)
        rows = []
        for _, row in ordered.iterrows():
            if row["constraint_count"] == 0:
                reason = "complete model output without major constraint flags; screening candidate only"
            else:
                reason = "lowest remaining constraint burden in V0.2-05 screening; not validated"
            rows.append(
                {
                    "case_id": row["case_id"],
                    "propulsion_case": row["propulsion_case"],
                    "design_variable_summary": row["design_variable_summary"],
                    "mission_fuel_kg": row["mission_fuel_kg"],
                    "fuel_delta_vs_baseline_pct": row["fuel_delta_vs_baseline_pct"],
                    "estimated_mtow_kg": row["estimated_mtow_kg"],
                    "mtow_margin_to_upper_kg": row["mtow_margin_to_upper_kg"],
                    "min_thrust_margin_N": row["min_thrust_margin_N"],
                    "unmet_electric_load_Wh": row["unmet_electric_load_Wh"],
                    "takeoff_proxy_index": row["takeoff_proxy_index"],
                    "conclusion_status": row["conclusion_status"],
                    "reason_selected": reason,
                }
            )
        return pd.DataFrame(rows)


def _case_slug(case_name: str) -> str:
    return {
        BASELINE_FIXED_CASE: "baseline",
        "adaptive_cycle_turbofan": "adaptive",
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


def _effective_clmax(base_clmax: float, c_mu_proxy: float, blowing: dict[str, Any]) -> float:
    cmu = min(max(c_mu_proxy, 0.0), blowing["cmu_max_for_v02"])
    return base_clmax + blowing["clmax_increment_per_cmu"] * cmu
