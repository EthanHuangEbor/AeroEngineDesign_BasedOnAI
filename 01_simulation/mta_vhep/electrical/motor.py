"""Concept-level electric motor model for MTA-VHEP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MotorResult:
    """Motor conversion result using SI units."""

    input_power_W: float
    shaft_power_W: float
    output_power_W: float
    losses_W: float
    efficiency: float
    estimated_mass_kg: float


@dataclass(frozen=True)
class MotorModel:
    """Simple motor model using efficiency and specific power in kW/kg."""

    efficiency: float
    specific_power_kW_per_kg: float

    def __post_init__(self) -> None:
        if self.efficiency <= 0.0 or self.efficiency > 1.0:
            raise ValueError("motor efficiency must be in the range (0, 1]")
        if self.specific_power_kW_per_kg <= 0.0:
            raise ValueError("motor specific_power_kW_per_kg must be positive")

    def evaluate_electric_to_shaft(self, input_power_W: float) -> MotorResult:
        """Convert electric input power in W to shaft output power in W."""
        if input_power_W < 0.0:
            raise ValueError("input_power_W must be non-negative")
        shaft_power_W = input_power_W * self.efficiency
        return MotorResult(
            input_power_W=input_power_W,
            shaft_power_W=shaft_power_W,
            output_power_W=shaft_power_W,
            losses_W=input_power_W - shaft_power_W,
            efficiency=self.efficiency,
            estimated_mass_kg=_estimate_mass_kg(input_power_W, self.specific_power_kW_per_kg),
        )

    def evaluate_shaft_to_electric(self, shaft_power_W: float) -> MotorResult:
        """Convert shaft input power in W to electric output power in W."""
        if shaft_power_W < 0.0:
            raise ValueError("shaft_power_W must be non-negative")
        output_power_W = shaft_power_W * self.efficiency
        return MotorResult(
            input_power_W=shaft_power_W,
            shaft_power_W=shaft_power_W,
            output_power_W=output_power_W,
            losses_W=shaft_power_W - output_power_W,
            efficiency=self.efficiency,
            estimated_mass_kg=_estimate_mass_kg(shaft_power_W, self.specific_power_kW_per_kg),
        )


def _estimate_mass_kg(power_W: float, specific_power_kW_per_kg: float) -> float:
    return (power_W / 1000.0) / specific_power_kW_per_kg
