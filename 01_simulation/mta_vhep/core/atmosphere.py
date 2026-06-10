"""ISA atmosphere helpers for MTA-VHEP concept-level models."""

from dataclasses import dataclass
from math import sqrt

from mta_vhep.core.constants import (
    GRAVITY_M_PER_S2,
    ISA_SEA_LEVEL_PRESSURE_PA,
    ISA_SEA_LEVEL_TEMPERATURE_K,
)

AIR_GAS_CONSTANT_J_PER_KG_K = 287.05287
AIR_HEAT_CAPACITY_RATIO = 1.4
ISA_TROPOSPHERE_LAPSE_RATE_K_PER_M = 0.0065
MIN_ALTITUDE_M = 0.0
MAX_ALTITUDE_M = 12000.0


@dataclass(frozen=True)
class AtmosphereState:
    """Atmospheric state at one altitude using SI units."""

    altitude_m: float
    delta_isa_K: float
    temperature_K: float
    pressure_Pa: float
    density_kg_m3: float
    speed_of_sound_mps: float


def isa_atmosphere(altitude_m: float, delta_isa_K: float = 0.0) -> AtmosphereState:
    """Return ISA troposphere properties for altitude in meters.

    The valid altitude range is 0 to 12000 m. Temperature includes the
    user-supplied delta ISA offset in kelvin. Pressure follows the baseline
    ISA lapse-rate relation, and density is computed from pressure and actual
    temperature in kg/m^3.
    """
    if altitude_m < MIN_ALTITUDE_M or altitude_m > MAX_ALTITUDE_M:
        raise ValueError("isa_atmosphere altitude_m must be between 0 and 12000 m")

    isa_temperature_K = (
        ISA_SEA_LEVEL_TEMPERATURE_K - ISA_TROPOSPHERE_LAPSE_RATE_K_PER_M * altitude_m
    )
    temperature_K = isa_temperature_K + delta_isa_K
    if temperature_K <= 0.0:
        raise ValueError("isa_atmosphere temperature must remain above 0 K")

    pressure_exponent = GRAVITY_M_PER_S2 / (
        AIR_GAS_CONSTANT_J_PER_KG_K * ISA_TROPOSPHERE_LAPSE_RATE_K_PER_M
    )
    pressure_Pa = ISA_SEA_LEVEL_PRESSURE_PA * (
        isa_temperature_K / ISA_SEA_LEVEL_TEMPERATURE_K
    ) ** pressure_exponent
    density_kg_m3 = pressure_Pa / (AIR_GAS_CONSTANT_J_PER_KG_K * temperature_K)
    speed_of_sound_mps = sqrt(AIR_HEAT_CAPACITY_RATIO * AIR_GAS_CONSTANT_J_PER_KG_K * temperature_K)

    return AtmosphereState(
        altitude_m=float(altitude_m),
        delta_isa_K=float(delta_isa_K),
        temperature_K=temperature_K,
        pressure_Pa=pressure_Pa,
        density_kg_m3=density_kg_m3,
        speed_of_sound_mps=speed_of_sound_mps,
    )
