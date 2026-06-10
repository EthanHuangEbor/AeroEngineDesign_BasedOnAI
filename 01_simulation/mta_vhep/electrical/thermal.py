"""Lumped thermal load accounting for MTA-VHEP electrical studies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThermalLoadResult:
    """Thermal load result using W and Wh."""

    heat_load_W: float
    heat_energy_Wh: float
    rejected_heat_load_W: float


class ThermalAccumulator:
    """Simple thermal load accumulator, not a heat-exchanger model."""

    def __init__(self, coolant_loop_efficiency: float) -> None:
        if coolant_loop_efficiency <= 0.0 or coolant_loop_efficiency > 1.0:
            raise ValueError("coolant_loop_efficiency must be in the range (0, 1]")
        self.coolant_loop_efficiency = coolant_loop_efficiency
        self.total_heat_energy_Wh = 0.0

    def add_heat(self, heat_load_W: float, duration_s: float) -> ThermalLoadResult:
        """Accumulate heat load in W over duration in seconds."""
        if heat_load_W < 0.0:
            raise ValueError("heat_load_W must be non-negative")
        if duration_s < 0.0:
            raise ValueError("duration_s must be non-negative")
        heat_energy_Wh = heat_load_W * duration_s / 3600.0
        self.total_heat_energy_Wh += heat_energy_Wh
        return ThermalLoadResult(
            heat_load_W=heat_load_W,
            heat_energy_Wh=heat_energy_Wh,
            rejected_heat_load_W=heat_load_W / self.coolant_loop_efficiency,
        )
