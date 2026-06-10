"""Concept-level inverter model for MTA-VHEP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InverterResult:
    """Inverter conversion result using SI units."""

    input_power_W: float
    output_power_W: float
    losses_W: float
    efficiency: float
    estimated_mass_kg: float


@dataclass(frozen=True)
class InverterModel:
    """Simple inverter model using efficiency and specific power in kW/kg."""

    efficiency: float
    specific_power_kW_per_kg: float

    def __post_init__(self) -> None:
        if self.efficiency <= 0.0 or self.efficiency > 1.0:
            raise ValueError("inverter efficiency must be in the range (0, 1]")
        if self.specific_power_kW_per_kg <= 0.0:
            raise ValueError("inverter specific_power_kW_per_kg must be positive")

    def evaluate(self, input_power_W: float) -> InverterResult:
        """Convert DC bus input power in W to motor-side output power in W."""
        if input_power_W < 0.0:
            raise ValueError("input_power_W must be non-negative")
        output_power_W = input_power_W * self.efficiency
        return InverterResult(
            input_power_W=input_power_W,
            output_power_W=output_power_W,
            losses_W=input_power_W - output_power_W,
            efficiency=self.efficiency,
            estimated_mass_kg=(input_power_W / 1000.0) / self.specific_power_kW_per_kg,
        )
