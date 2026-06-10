"""Mission segment result interfaces for MTA-VHEP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MissionSegmentResult:
    """Concept mission segment result using SI units except distance in km."""

    case_name: str
    segment_name: str
    segment_type: str
    distance_km: float
    duration_s: float
    altitude_start_m: float
    altitude_end_m: float
    mach: float | None
    speed_mps: float | None
    engine_rating: str
    electric_fan_mode: str
    start_mass_kg: float
    end_mass_kg: float
    fuel_burn_kg: float
    electric_energy_Wh: float
    max_electric_power_W: float
    max_thermal_load_W: float
    electric_thrust_proxy_N: float
    blowing_momentum_coefficient: float
    average_required_thrust_N: float
    available_thrust_N: float
    thrust_margin_N: float
    soc_start: float | None
    soc_end: float | None
    unmet_electric_load_Wh: float
    constraint_flags: list[str]
