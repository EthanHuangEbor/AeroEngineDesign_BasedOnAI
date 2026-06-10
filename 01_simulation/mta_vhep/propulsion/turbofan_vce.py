"""Concept-level variable-cycle turbofan surrogate for MTA-VHEP."""

from dataclasses import dataclass
from typing import Any

from mta_vhep.core.atmosphere import isa_atmosphere
from mta_vhep.core.constants import ISA_SEA_LEVEL_DENSITY_KG_PER_M3
from mta_vhep.interfaces.schemas import FuelProperties
from mta_vhep.propulsion.power_extraction import compute_power_extraction_penalty

VALID_RATINGS = ("idle", "approach", "cruise", "climb", "takeoff")
REFERENCE_LHV_J_PER_KG = 43_000_000.0


@dataclass(frozen=True)
class EngineOperatingPoint:
    """Single engine operating point using SI units."""

    mach: float
    altitude_m: float
    throttle: float
    rating: str
    shaft_power_extraction_W: float
    third_stream_schedule: float
    variable_nozzle_schedule: float
    fuel: FuelProperties


@dataclass(frozen=True)
class EnginePerformance:
    """Single engine surrogate performance using SI units."""

    engine_name: str
    net_thrust_N: float
    gross_thrust_N: float
    fuel_flow_kg_s: float
    tsfc_kg_per_N_s: float
    core_mass_flow_kg_s: float | None
    bypass_mass_flow_kg_s: float | None
    third_stream_mass_flow_kg_s: float | None
    turbine_temperature_margin_K: float | None
    surge_margin: float | None
    shaft_power_extracted_W: float
    thrust_penalty_from_extraction_N: float
    fuel_flow_increment_from_extraction_kg_s: float
    constraint_flags: list[str]


class VariableCycleTurbofan:
    """Transparent surrogate for baseline and adaptive turbofan variants."""

    def __init__(
        self,
        engine_config: dict[str, Any],
        lapse_model: dict[str, Any],
        third_stream_effects: dict[str, Any],
        nozzle_effects: dict[str, Any],
        shaft_power_extraction: dict[str, Any],
        adaptive_effects_enabled: bool,
    ) -> None:
        self.engine_name = _require_str(engine_config, "name", "engine_config")
        self.sea_level_static_thrust_N_per_engine = _require_number(
            engine_config,
            "sea_level_static_thrust_N_per_engine",
            "engine_config",
        )
        self.reference_tsfc_kg_per_N_s = _require_number_mapping(
            engine_config,
            "reference_tsfc_kg_per_N_s",
            "engine_config",
        )
        self.rating_throttle_floor = _require_number_mapping(
            engine_config,
            "rating_throttle_floor",
            "engine_config",
        )
        self.lapse_model = lapse_model
        self.third_stream_effects = third_stream_effects
        self.nozzle_effects = nozzle_effects
        self.shaft_power_extraction = shaft_power_extraction
        self.adaptive_effects_enabled = adaptive_effects_enabled

    @classmethod
    def from_config(cls, config: dict[str, Any], variant_key: str) -> "VariableCycleTurbofan":
        """Build a turbofan surrogate variant from engine_surrogate.yaml data."""
        root = _require_mapping(config.get("engine_surrogate"), "engine_surrogate")
        if bool(root.get("certification_grade", True)):
            raise ValueError("engine_surrogate.certification_grade must be false")
        if variant_key not in ("baseline_fixed_cycle", "adaptive_cycle"):
            raise ValueError("variant_key must be baseline_fixed_cycle or adaptive_cycle")

        return cls(
            engine_config=_require_mapping(root.get(variant_key), f"engine_surrogate.{variant_key}"),
            lapse_model=_require_mapping(root.get("lapse_model"), "engine_surrogate.lapse_model"),
            third_stream_effects=_require_mapping(
                root.get("third_stream_effects"), "engine_surrogate.third_stream_effects"
            ),
            nozzle_effects=_require_mapping(
                root.get("nozzle_effects"), "engine_surrogate.nozzle_effects"
            ),
            shaft_power_extraction=_require_mapping(
                root.get("shaft_power_extraction"), "engine_surrogate.shaft_power_extraction"
            ),
            adaptive_effects_enabled=variant_key == "adaptive_cycle",
        )

    def evaluate(self, op: EngineOperatingPoint) -> EnginePerformance:
        """Evaluate concept-level engine output for one operating point."""
        if op.rating not in VALID_RATINGS:
            raise ValueError(f"invalid_rating: {op.rating}")
        if op.mach < 0.0:
            raise ValueError("mach must be non-negative")
        if op.altitude_m < 0.0:
            raise ValueError("altitude_m must be non-negative")

        flags: list[str] = []
        throttle = _clamp(op.throttle, 0.0, 1.0)
        throttle_floor = self.rating_throttle_floor[op.rating]
        if throttle != op.throttle or throttle < throttle_floor:
            flags.append("throttle_clamped")
        throttle = max(throttle, throttle_floor)

        third_stream_schedule = _clamp(op.third_stream_schedule, 0.0, 1.0)
        variable_nozzle_schedule = _clamp(op.variable_nozzle_schedule, 0.0, 1.0)
        if (
            third_stream_schedule != op.third_stream_schedule
            or variable_nozzle_schedule != op.variable_nozzle_schedule
        ):
            flags.append("schedule_clamped")

        atmosphere = isa_atmosphere(op.altitude_m)
        density_ratio = atmosphere.density_kg_m3 / ISA_SEA_LEVEL_DENSITY_KG_PER_M3
        density_lapse = density_ratio ** _require_number(
            self.lapse_model, "density_exponent", "lapse_model"
        )
        mach_lapse = max(
            _require_number(self.lapse_model, "min_lapse_factor", "lapse_model"),
            1.0
            - _require_number(
                self.lapse_model, "mach_thrust_lapse_per_mach", "lapse_model"
            )
            * op.mach,
        )

        gross_thrust_N = (
            self.sea_level_static_thrust_N_per_engine
            * density_lapse
            * mach_lapse
            * throttle
        )

        tsfc_kg_per_N_s = self.reference_tsfc_kg_per_N_s[op.rating]
        tsfc_kg_per_N_s *= REFERENCE_LHV_J_PER_KG / op.fuel.lower_heating_value_J_per_kg

        if self.adaptive_effects_enabled:
            gross_thrust_N *= self._adaptive_thrust_multiplier(
                op.rating,
                third_stream_schedule,
                variable_nozzle_schedule,
            )
            tsfc_kg_per_N_s *= self._adaptive_tsfc_multiplier(
                op.rating,
                third_stream_schedule,
                variable_nozzle_schedule,
            )

        flight_speed_mps = op.mach * atmosphere.speed_of_sound_mps
        try:
            extraction = compute_power_extraction_penalty(
                shaft_power_extraction_W=op.shaft_power_extraction_W,
                mechanical_efficiency=_require_number(
                    self.shaft_power_extraction,
                    "mechanical_efficiency",
                    "shaft_power_extraction",
                ),
                propulsive_power_equivalent_efficiency=_require_number(
                    self.shaft_power_extraction,
                    "propulsive_power_equivalent_efficiency",
                    "shaft_power_extraction",
                ),
                fuel_flow_increment_per_MW_kg_s=_require_number(
                    self.shaft_power_extraction,
                    "fuel_flow_increment_per_MW_kg_s",
                    "shaft_power_extraction",
                ),
                max_extraction_W_per_engine_for_v02=_require_number(
                    self.shaft_power_extraction,
                    "max_extraction_W_per_engine_for_v02",
                    "shaft_power_extraction",
                ),
                flight_speed_mps=flight_speed_mps,
            )
        except ValueError as exc:
            if "exceeds" in str(exc):
                raise ValueError(f"extraction_limit_exceeded: {exc}") from exc
            raise

        net_thrust_N = gross_thrust_N - extraction.equivalent_thrust_penalty_N
        if net_thrust_N <= 0.0:
            flags.append("low_net_thrust")
            net_thrust_N = 0.0

        fuel_flow_kg_s = gross_thrust_N * tsfc_kg_per_N_s
        fuel_flow_kg_s += extraction.additional_fuel_flow_kg_s
        effective_tsfc = fuel_flow_kg_s / net_thrust_N if net_thrust_N > 0.0 else float("inf")

        return EnginePerformance(
            engine_name=self.engine_name,
            net_thrust_N=net_thrust_N,
            gross_thrust_N=gross_thrust_N,
            fuel_flow_kg_s=fuel_flow_kg_s,
            tsfc_kg_per_N_s=effective_tsfc,
            core_mass_flow_kg_s=None,
            bypass_mass_flow_kg_s=None,
            third_stream_mass_flow_kg_s=None,
            turbine_temperature_margin_K=None,
            surge_margin=None,
            shaft_power_extracted_W=extraction.shaft_power_extracted_W,
            thrust_penalty_from_extraction_N=extraction.equivalent_thrust_penalty_N,
            fuel_flow_increment_from_extraction_kg_s=extraction.additional_fuel_flow_kg_s,
            constraint_flags=flags,
        )

    def _adaptive_thrust_multiplier(
        self,
        rating: str,
        third_stream_schedule: float,
        variable_nozzle_schedule: float,
    ) -> float:
        multiplier = 1.0
        if rating in ("takeoff", "climb", "approach"):
            multiplier += _require_number(
                self.nozzle_effects, "high_thrust_nozzle_bonus", "nozzle_effects"
            ) * variable_nozzle_schedule
        if rating == "takeoff":
            multiplier -= _require_number(
                self.third_stream_effects,
                "takeoff_thrust_penalty_at_full_schedule",
                "third_stream_effects",
            ) * third_stream_schedule
            multiplier += _require_number(
                self.third_stream_effects,
                "thrust_bonus_takeoff_low_third_stream",
                "third_stream_effects",
            ) * (1.0 - third_stream_schedule) * variable_nozzle_schedule
        return max(multiplier, 0.0)

    def _adaptive_tsfc_multiplier(
        self,
        rating: str,
        third_stream_schedule: float,
        variable_nozzle_schedule: float,
    ) -> float:
        reduction_by_rating = {
            "cruise": "cruise_tsfc_reduction_at_full_schedule",
            "climb": "climb_tsfc_reduction_at_full_schedule",
            "approach": "approach_tsfc_reduction_at_full_schedule",
        }
        multiplier = 1.0
        if rating in reduction_by_rating:
            multiplier -= _require_number(
                self.third_stream_effects,
                reduction_by_rating[rating],
                "third_stream_effects",
            ) * third_stream_schedule
        high_efficiency_nozzle_factor = 1.0 - variable_nozzle_schedule
        multiplier -= _require_number(
            self.nozzle_effects,
            "high_efficiency_nozzle_tsfc_reduction",
            "nozzle_effects",
        ) * high_efficiency_nozzle_factor
        return max(multiplier, 0.5)


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _require_mapping(value: Any, section: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{section} must be a mapping")
    return value


def _require_str(data: dict[str, Any], key: str, section: str) -> str:
    if key not in data or not isinstance(data[key], str):
        raise ValueError(f"{section}.{key} must be a string")
    return data[key]


def _require_number(data: dict[str, Any], key: str, section: str) -> float:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{section}.{key} must be a number")
    return float(value)


def _require_number_mapping(data: dict[str, Any], key: str, section: str) -> dict[str, float]:
    mapping = _require_mapping(data.get(key), f"{section}.{key}")
    result = {rating: _require_number(mapping, rating, f"{section}.{key}") for rating in VALID_RATINGS}
    return result
