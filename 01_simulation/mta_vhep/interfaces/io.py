"""YAML configuration loading for MTA-VHEP V0.2."""

from pathlib import Path
import re
from typing import Any

import yaml

from mta_vhep.interfaces.schemas import (
    AircraftBaseline,
    ElectricFanConfig,
    ElectricalConfig,
    FuelProperties,
    GeometryBaseline,
    MainEngineConfig,
    MissionProfile,
    MissionSegment,
    PerformanceTargets,
    ProjectConfig,
)


FROZEN_AIRCRAFT_VALUES = {
    "payload_design_kg": 25000,
    "range_design_km": 3200,
    "engine_count": 2,
    "electric_fan_count": 4,
    "cruise_mach": 0.75,
    "cruise_altitude_m": 10668,
    "mtow_initial_kg": 87500,
    "oew_initial_kg": 52000,
}

FROZEN_MAIN_ENGINE_VALUES = {
    "count": 2,
    "sea_level_static_thrust_N_per_engine_initial": 115000,
}

FROZEN_ELECTRIC_FAN_VALUES = {
    "count": 4,
    "power_W_per_fan_initial": 1000000,
}


class _MtaVhepYamlLoader(yaml.SafeLoader):
    """YAML loader that keeps on/off mode labels as strings."""


_MtaVhepYamlLoader.yaml_implicit_resolvers = {
    key: list(value) for key, value in yaml.SafeLoader.yaml_implicit_resolvers.items()
}

for first_char, resolvers in list(_MtaVhepYamlLoader.yaml_implicit_resolvers.items()):
    _MtaVhepYamlLoader.yaml_implicit_resolvers[first_char] = [
        (tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:bool"
    ]

_MtaVhepYamlLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file from path and return a dictionary."""
    if not path.exists():
        raise FileNotFoundError(f"Required YAML file is missing: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.load(handle, Loader=_MtaVhepYamlLoader)

    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping at top level: {path}")

    return data


def load_aircraft_baseline(
    config_dir: Path,
) -> tuple[AircraftBaseline, GeometryBaseline, PerformanceTargets]:
    """Load aircraft, geometry, and performance target config from SI YAML values."""
    data = load_yaml(config_dir / "aircraft_baseline.yaml")
    _require_keys(data, ("aircraft", "geometry", "performance_targets"), "aircraft_baseline.yaml")

    aircraft_data = _require_mapping(data["aircraft"], "aircraft")
    geometry_data = _require_mapping(data["geometry"], "geometry")
    performance_data = _require_mapping(data["performance_targets"], "performance_targets")

    _validate_frozen_values(aircraft_data, FROZEN_AIRCRAFT_VALUES, "aircraft")

    aircraft = AircraftBaseline(
        name=_require_type(aircraft_data, "name", str, "aircraft"),
        aircraft_type=_require_type(aircraft_data, "type", str, "aircraft"),
        payload_design_kg=_require_number(aircraft_data, "payload_design_kg", "aircraft"),
        range_design_km=_require_number(aircraft_data, "range_design_km", "aircraft"),
        engine_count=_require_int(aircraft_data, "engine_count", "aircraft"),
        electric_fan_count=_require_int(aircraft_data, "electric_fan_count", "aircraft"),
        cruise_mach=_require_number(aircraft_data, "cruise_mach", "aircraft"),
        cruise_altitude_m=_require_number(aircraft_data, "cruise_altitude_m", "aircraft"),
        mtow_initial_kg=_require_number(aircraft_data, "mtow_initial_kg", "aircraft"),
        oew_initial_kg=_require_number(aircraft_data, "oew_initial_kg", "aircraft"),
    )
    geometry = GeometryBaseline(
        wing_area_m2_initial=_require_number(geometry_data, "wing_area_m2_initial", "geometry"),
        aspect_ratio_initial=_require_number(geometry_data, "aspect_ratio_initial", "geometry"),
        oswald_efficiency_initial=_require_number(
            geometry_data, "oswald_efficiency_initial", "geometry"
        ),
        cd0_cruise_initial=_require_number(geometry_data, "cd0_cruise_initial", "geometry"),
        ld_cruise_range=_require_number_pair(geometry_data, "ld_cruise_range", "geometry"),
    )
    performance_targets = PerformanceTargets(
        takeoff_field_length_target_m=_require_number(
            performance_data, "takeoff_field_length_target_m", "performance_targets"
        ),
        landing_field_length_target_m=_require_number(
            performance_data, "landing_field_length_target_m", "performance_targets"
        ),
        max_mach=_require_number(performance_data, "max_mach", "performance_targets"),
        max_altitude_m=_require_number(performance_data, "max_altitude_m", "performance_targets"),
    )

    return aircraft, geometry, performance_targets


def load_propulsion_config(
    config_dir: Path,
) -> tuple[MainEngineConfig, ElectricFanConfig, ElectricalConfig]:
    """Load main engine, electric fan, and electrical config from SI YAML values."""
    data = load_yaml(config_dir / "propulsion.yaml")
    _require_keys(data, ("propulsion", "electrical", "model_boundaries"), "propulsion.yaml")

    propulsion_data = _require_mapping(data["propulsion"], "propulsion")
    _require_keys(propulsion_data, ("main_engine", "electric_blown_flap_fan"), "propulsion")
    main_engine_data = _require_mapping(propulsion_data["main_engine"], "propulsion.main_engine")
    electric_fan_data = _require_mapping(
        propulsion_data["electric_blown_flap_fan"], "propulsion.electric_blown_flap_fan"
    )
    electrical_data = _require_mapping(data["electrical"], "electrical")
    model_boundaries = _require_mapping(data["model_boundaries"], "model_boundaries")

    _validate_frozen_values(main_engine_data, FROZEN_MAIN_ENGINE_VALUES, "propulsion.main_engine")
    _validate_frozen_values(
        electric_fan_data, FROZEN_ELECTRIC_FAN_VALUES, "propulsion.electric_blown_flap_fan"
    )
    certification_grade = _require_type(model_boundaries, "certification_grade", bool, "model_boundaries")
    if certification_grade:
        raise ValueError("model_boundaries.certification_grade must be false for V0.2")

    main_engine = MainEngineConfig(
        engine_type=_require_type(main_engine_data, "type", str, "propulsion.main_engine"),
        count=_require_int(main_engine_data, "count", "propulsion.main_engine"),
        sea_level_static_thrust_N_per_engine_initial=_require_number(
            main_engine_data,
            "sea_level_static_thrust_N_per_engine_initial",
            "propulsion.main_engine",
        ),
        supports_shaft_power_extraction=_require_type(
            main_engine_data, "supports_shaft_power_extraction", bool, "propulsion.main_engine"
        ),
        third_stream_model=_require_type(
            main_engine_data, "third_stream_model", str, "propulsion.main_engine"
        ),
        future_hydrogen_enabled=_require_type(
            main_engine_data, "future_hydrogen_enabled", bool, "propulsion.main_engine"
        ),
        future_detonation_enabled=_require_type(
            main_engine_data, "future_detonation_enabled", bool, "propulsion.main_engine"
        ),
    )
    if main_engine.future_hydrogen_enabled or main_engine.future_detonation_enabled:
        raise ValueError("Hydrogen and detonation modes must remain disabled in V0.2")

    electric_fan = ElectricFanConfig(
        count=_require_int(electric_fan_data, "count", "propulsion.electric_blown_flap_fan"),
        role=_require_type(electric_fan_data, "role", str, "propulsion.electric_blown_flap_fan"),
        power_W_per_fan_initial=_require_number(
            electric_fan_data, "power_W_per_fan_initial", "propulsion.electric_blown_flap_fan"
        ),
        cruise_operation=_require_type(
            electric_fan_data, "cruise_operation", str, "propulsion.electric_blown_flap_fan"
        ),
        motor_efficiency=_require_number(
            electric_fan_data, "motor_efficiency", "propulsion.electric_blown_flap_fan"
        ),
        inverter_efficiency=_require_number(
            electric_fan_data, "inverter_efficiency", "propulsion.electric_blown_flap_fan"
        ),
        failure_modes=_require_str_list(
            electric_fan_data, "failure_modes", "propulsion.electric_blown_flap_fan"
        ),
    )
    electrical = ElectricalConfig(
        bus_voltage_V_initial=_require_number(
            electrical_data, "bus_voltage_V_initial", "electrical"
        ),
        generator_efficiency=_require_number(electrical_data, "generator_efficiency", "electrical"),
        cable_distribution_efficiency=_require_number(
            electrical_data, "cable_distribution_efficiency", "electrical"
        ),
        battery_buffer_capacity_Wh_initial=_require_number(
            electrical_data, "battery_buffer_capacity_Wh_initial", "electrical"
        ),
        battery_soc_min=_require_number(electrical_data, "battery_soc_min", "electrical"),
        battery_soc_initial=_require_number(electrical_data, "battery_soc_initial", "electrical"),
    )

    return main_engine, electric_fan, electrical


def load_fuel_database(config_dir: Path) -> dict[str, FuelProperties]:
    """Load fuel database from SI YAML values."""
    data = load_yaml(config_dir / "fuel_database.yaml")
    _require_keys(data, ("fuels", "fuel_policy"), "fuel_database.yaml")
    fuels_data = _require_mapping(data["fuels"], "fuels")

    fuels: dict[str, FuelProperties] = {}
    for name, fuel_data in fuels_data.items():
        section = f"fuels.{name}"
        fuel_mapping = _require_mapping(fuel_data, section)
        fuels[name] = FuelProperties(
            name=name,
            lower_heating_value_J_per_kg=_require_number(
                fuel_mapping, "lower_heating_value_J_per_kg", section
            ),
            density_kg_per_m3=_require_number(fuel_mapping, "density_kg_per_m3", section),
            carbon_emission_factor_kgCO2_per_kg=_require_number(
                fuel_mapping, "carbon_emission_factor_kgCO2_per_kg", section
            ),
            lifecycle_factor_kgCO2e_per_kg=_require_optional_number(
                fuel_mapping, "lifecycle_factor_kgCO2e_per_kg", section
            ),
            blend_ratio_saf=_require_optional_number(fuel_mapping, "blend_ratio_saf", section),
        )

    return fuels


def load_mission_profile(config_dir: Path) -> MissionProfile:
    """Load mission profile from SI YAML values."""
    data = load_yaml(config_dir / "mission_profile.yaml")
    _require_keys(data, ("mission", "segments"), "mission_profile.yaml")
    mission_data = _require_mapping(data["mission"], "mission")

    segments_data = data["segments"]
    if not isinstance(segments_data, list):
        raise ValueError("segments must be a list in mission_profile.yaml")

    segments = [_build_mission_segment(item, index) for index, item in enumerate(segments_data)]

    return MissionProfile(
        name=_require_type(mission_data, "name", str, "mission"),
        design_payload_kg=_require_number(mission_data, "design_payload_kg", "mission"),
        design_range_km=_require_number(mission_data, "design_range_km", "mission"),
        reserve_policy=_require_mapping(mission_data.get("reserve_policy"), "mission.reserve_policy"),
        segments=segments,
    )


def load_project_config(config_dir: Path) -> ProjectConfig:
    """Load the complete V0.2 project configuration from YAML files."""
    aircraft, geometry, performance_targets = load_aircraft_baseline(config_dir)
    main_engine, electric_fan, electrical = load_propulsion_config(config_dir)
    fuels = load_fuel_database(config_dir)
    mission = load_mission_profile(config_dir)

    return ProjectConfig(
        aircraft=aircraft,
        geometry=geometry,
        performance_targets=performance_targets,
        main_engine=main_engine,
        electric_fan=electric_fan,
        electrical=electrical,
        fuels=fuels,
        mission=mission,
    )


def _build_mission_segment(data: Any, index: int) -> MissionSegment:
    section = f"segments[{index}]"
    segment_data = _require_mapping(data, section)
    return MissionSegment(
        name=_require_type(segment_data, "name", str, section),
        segment_type=_require_type(segment_data, "segment_type", str, section),
        duration_s=_require_optional_number(segment_data, "duration_s", section),
        distance_km=_require_optional_number(segment_data, "distance_km", section),
        altitude_start_m=_require_number(segment_data, "altitude_start_m", section),
        altitude_end_m=_require_number(segment_data, "altitude_end_m", section),
        mach=_require_optional_number(segment_data, "mach", section),
        speed_mps=_require_optional_number(segment_data, "speed_mps", section),
        electric_fan_mode=_require_type(segment_data, "electric_fan_mode", str, section),
        engine_rating=_require_type(segment_data, "engine_rating", str, section),
    )


def _require_keys(data: dict[str, Any], keys: tuple[str, ...], section: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required key(s) in {section}: {missing_text}")


def _require_mapping(value: Any, section: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{section} must be a mapping")
    return value


def _require_type(data: dict[str, Any], key: str, expected_type: type, section: str) -> Any:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if not isinstance(value, expected_type):
        raise ValueError(f"{section}.{key} must be {expected_type.__name__}, got {type(value).__name__}")
    return value


def _require_number(data: dict[str, Any], key: str, section: str) -> float:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{section}.{key} must be a number, got {type(value).__name__}")
    return float(value)


def _require_optional_number(data: dict[str, Any], key: str, section: str) -> float | None:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{section}.{key} must be a number or null, got {type(value).__name__}")
    return float(value)


def _require_int(data: dict[str, Any], key: str, section: str) -> int:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{section}.{key} must be an integer, got {type(value).__name__}")
    return value


def _require_number_pair(data: dict[str, Any], key: str, section: str) -> tuple[float, float]:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{section}.{key} must be a two-item list")
    first, second = value
    if (
        isinstance(first, bool)
        or isinstance(second, bool)
        or not isinstance(first, (int, float))
        or not isinstance(second, (int, float))
    ):
        raise ValueError(f"{section}.{key} must contain only numbers")
    return float(first), float(second)


def _require_str_list(data: dict[str, Any], key: str, section: str) -> list[str]:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{section}.{key} must be a list of strings")
    return list(value)


def _validate_frozen_values(data: dict[str, Any], frozen_values: dict[str, Any], section: str) -> None:
    for key, expected in frozen_values.items():
        if key not in data:
            raise ValueError(f"Missing frozen key in {section}: {key}")
        actual = data[key]
        if actual != expected:
            raise ValueError(f"{section}.{key} is frozen at {expected!r}, got {actual!r}")
