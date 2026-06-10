"""Dataclass schemas for MTA-VHEP configuration data."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AircraftBaseline:
    """Baseline aircraft configuration using SI units."""

    name: str
    aircraft_type: str
    payload_design_kg: float
    range_design_km: float
    engine_count: int
    electric_fan_count: int
    cruise_mach: float
    cruise_altitude_m: float
    mtow_initial_kg: float
    oew_initial_kg: float


@dataclass(frozen=True)
class GeometryBaseline:
    """Baseline aircraft geometry using SI units."""

    wing_area_m2_initial: float
    aspect_ratio_initial: float
    oswald_efficiency_initial: float
    cd0_cruise_initial: float
    ld_cruise_range: tuple[float, float]


@dataclass(frozen=True)
class PerformanceTargets:
    """Concept-level performance targets using SI units."""

    takeoff_field_length_target_m: float
    landing_field_length_target_m: float
    max_mach: float
    max_altitude_m: float


@dataclass(frozen=True)
class MainEngineConfig:
    """Main engine configuration using SI units."""

    engine_type: str
    count: int
    sea_level_static_thrust_N_per_engine_initial: float
    supports_shaft_power_extraction: bool
    third_stream_model: str
    future_hydrogen_enabled: bool
    future_detonation_enabled: bool


@dataclass(frozen=True)
class ElectricFanConfig:
    """Electric blown-flap fan configuration using SI units."""

    count: int
    role: str
    power_W_per_fan_initial: float
    cruise_operation: str
    motor_efficiency: float
    inverter_efficiency: float
    failure_modes: list[str]


@dataclass(frozen=True)
class ElectricalConfig:
    """Electrical system configuration using SI units."""

    bus_voltage_V_initial: float
    generator_efficiency: float
    cable_distribution_efficiency: float
    battery_buffer_capacity_Wh_initial: float
    battery_soc_min: float
    battery_soc_initial: float


@dataclass(frozen=True)
class FuelProperties:
    """Fuel properties using SI units."""

    name: str
    lower_heating_value_J_per_kg: float
    density_kg_per_m3: float
    carbon_emission_factor_kgCO2_per_kg: float
    lifecycle_factor_kgCO2e_per_kg: float | None
    blend_ratio_saf: float | None


@dataclass(frozen=True)
class MissionSegment:
    """Mission segment definition using SI units for altitude and speed."""

    name: str
    segment_type: str
    duration_s: float | None
    distance_km: float | None
    altitude_start_m: float
    altitude_end_m: float
    mach: float | None
    speed_mps: float | None
    electric_fan_mode: str
    engine_rating: str


@dataclass(frozen=True)
class MissionProfile:
    """Mission profile configuration using SI units where applicable."""

    name: str
    design_payload_kg: float
    design_range_km: float
    reserve_policy: dict[str, Any]
    segments: list[MissionSegment]


@dataclass(frozen=True)
class ProjectConfig:
    """Complete V0.2 project configuration."""

    aircraft: AircraftBaseline
    geometry: GeometryBaseline
    performance_targets: PerformanceTargets
    main_engine: MainEngineConfig
    electric_fan: ElectricFanConfig
    electrical: ElectricalConfig
    fuels: dict[str, FuelProperties]
    mission: MissionProfile
