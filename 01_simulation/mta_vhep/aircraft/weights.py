"""Concept-level aircraft weight buildup helpers for MTA-VHEP."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WeightBreakdown:
    """Mission start mass estimate using kg units.

    The estimated MTOW is OEW + payload + fuel + optional hybrid masses. The
    main engine mass is reported as a traceable assumption and is treated as
    already included in OEW for this V0.2 concept buildup.
    """

    payload_kg: float
    oew_kg: float
    fuel_kg: float
    main_engines_kg: float
    hybrid_fixed_mass_kg: float
    hybrid_power_mass_kg: float
    battery_mass_kg: float
    hybrid_total_mass_kg: float
    estimated_mtow_kg: float
    mtow_margin_kg: float


class WeightBuildUp:
    """Build concept-level mission start mass estimates from YAML assumptions."""

    def __init__(
        self,
        weights_config: dict[str, Any],
        hybrid_config: dict[str, Any] | None = None,
        engine_count: int = 2,
    ) -> None:
        self.weights_config = weights_config
        self.hybrid_config = hybrid_config
        self.engine_count = engine_count

    def estimate(
        self,
        fuel_kg: float,
        hybrid_mass_penalty_enabled: bool,
        total_electric_power_W: float = 0.0,
    ) -> WeightBreakdown:
        """Return a weight breakdown for fuel mass in kg and electric power in W."""
        if fuel_kg < 0.0:
            raise ValueError("fuel_kg must be non-negative")
        if total_electric_power_W < 0.0:
            raise ValueError("total_electric_power_W must be non-negative")

        payload_kg = _number(self.weights_config, "payload_kg")
        oew_kg = _number(self.weights_config, "oew_kg")
        mtow_initial_kg = _number(self.weights_config, "mtow_initial_kg")
        main_engines_kg = (
            _number(self.weights_config, "main_engine_mass_kg_each_assumption")
            * self.engine_count
        )

        hybrid_fixed_mass_kg = 0.0
        hybrid_power_mass_kg = 0.0
        battery_mass_kg = 0.0
        if hybrid_mass_penalty_enabled:
            hybrid_fixed_mass_kg = _number(self.weights_config, "hybrid_fixed_mass_kg")
            hybrid_power_mass_kg = (
                _number(self.weights_config, "hybrid_mass_per_MW_kg")
                * total_electric_power_W
                / 1_000_000.0
            )
            battery_mass_kg = self._battery_mass_kg()

        hybrid_total_mass_kg = (
            hybrid_fixed_mass_kg + hybrid_power_mass_kg + battery_mass_kg
        )
        estimated_mtow_kg = oew_kg + payload_kg + fuel_kg + hybrid_total_mass_kg

        return WeightBreakdown(
            payload_kg=payload_kg,
            oew_kg=oew_kg,
            fuel_kg=fuel_kg,
            main_engines_kg=main_engines_kg,
            hybrid_fixed_mass_kg=hybrid_fixed_mass_kg,
            hybrid_power_mass_kg=hybrid_power_mass_kg,
            battery_mass_kg=battery_mass_kg,
            hybrid_total_mass_kg=hybrid_total_mass_kg,
            estimated_mtow_kg=estimated_mtow_kg,
            mtow_margin_kg=mtow_initial_kg - estimated_mtow_kg,
        )

    def _battery_mass_kg(self) -> float:
        override = self.weights_config.get("battery_mass_override_kg")
        if override is not None:
            if isinstance(override, bool) or not isinstance(override, (int, float)):
                raise ValueError("battery_mass_override_kg must be numeric or null")
            if override < 0.0:
                raise ValueError("battery_mass_override_kg must be non-negative")
            return float(override)

        if self.hybrid_config is None:
            return 0.0
        battery = _mapping(self.hybrid_config, "battery_buffer")
        capacity_Wh = _number(battery, "capacity_Wh")
        specific_energy_Wh_per_kg = _number(battery, "specific_energy_Wh_per_kg")
        if specific_energy_Wh_per_kg <= 0.0:
            raise ValueError("battery specific energy must be positive")
        return capacity_Wh / specific_energy_Wh_per_kg


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
