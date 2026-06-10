"""Concept-level shaft power extraction penalties for MTA-VHEP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PowerExtractionResult:
    """Power extraction penalty outputs using SI units."""

    shaft_power_extracted_W: float
    effective_shaft_power_extracted_W: float
    equivalent_thrust_penalty_N: float
    additional_fuel_flow_kg_s: float
    heat_load_note: str | None


def compute_power_extraction_penalty(
    shaft_power_extraction_W: float,
    mechanical_efficiency: float,
    propulsive_power_equivalent_efficiency: float,
    fuel_flow_increment_per_MW_kg_s: float,
    max_extraction_W_per_engine_for_v02: float,
    flight_speed_mps: float | None = None,
    min_equivalent_speed_mps: float = 75.0,
) -> PowerExtractionResult:
    """Compute concept-level per-engine shaft power extraction penalties.

    Inputs are per engine. Shaft power is in W, flight speed is in m/s, the
    equivalent thrust penalty is returned in N, and additional fuel flow is
    returned in kg/s. The equivalent thrust penalty is a power-equivalent proxy,
    not a spool matching calculation.
    """
    if shaft_power_extraction_W < 0.0:
        raise ValueError("shaft_power_extraction_W must be non-negative")
    if shaft_power_extraction_W > max_extraction_W_per_engine_for_v02:
        raise ValueError("shaft_power_extraction_W exceeds the configured V0.2 limit")
    if mechanical_efficiency <= 0.0 or mechanical_efficiency > 1.0:
        raise ValueError("mechanical_efficiency must be in the range (0, 1]")
    if propulsive_power_equivalent_efficiency <= 0.0:
        raise ValueError("propulsive_power_equivalent_efficiency must be positive")
    if fuel_flow_increment_per_MW_kg_s < 0.0:
        raise ValueError("fuel_flow_increment_per_MW_kg_s must be non-negative")

    if shaft_power_extraction_W == 0.0:
        return PowerExtractionResult(
            shaft_power_extracted_W=0.0,
            effective_shaft_power_extracted_W=0.0,
            equivalent_thrust_penalty_N=0.0,
            additional_fuel_flow_kg_s=0.0,
            heat_load_note=None,
        )

    speed_for_equivalent_power = max(flight_speed_mps or 0.0, min_equivalent_speed_mps)
    effective_shaft_power_extracted_W = shaft_power_extraction_W / mechanical_efficiency
    equivalent_thrust_penalty_N = effective_shaft_power_extracted_W / (
        propulsive_power_equivalent_efficiency * speed_for_equivalent_power
    )
    additional_fuel_flow_kg_s = (
        shaft_power_extraction_W / 1_000_000.0
    ) * fuel_flow_increment_per_MW_kg_s

    heat_load_note = None
    if shaft_power_extraction_W >= 0.8 * max_extraction_W_per_engine_for_v02:
        heat_load_note = "high V0.2 shaft extraction load placeholder"

    return PowerExtractionResult(
        shaft_power_extracted_W=shaft_power_extraction_W,
        effective_shaft_power_extracted_W=effective_shaft_power_extracted_W,
        equivalent_thrust_penalty_N=equivalent_thrust_penalty_N,
        additional_fuel_flow_kg_s=additional_fuel_flow_kg_s,
        heat_load_note=heat_load_note,
    )
