"""Electric blown-flap fan proxy model for MTA-VHEP."""

from dataclasses import dataclass

from mta_vhep.electrical.inverter import InverterModel
from mta_vhep.electrical.motor import MotorModel

FAN_MODES = ("off", "assist", "degraded", "failed")


@dataclass(frozen=True)
class ElectricFanCommand:
    """Electric fan command using SI units."""

    mode: str
    airspeed_mps: float
    density_kg_m3: float
    wing_area_m2: float
    input_power_W: float | None = None


@dataclass(frozen=True)
class ElectricFanPerformance:
    """Electric fan proxy outputs using SI units."""

    mode: str
    input_power_W: float
    inverter_output_power_W: float
    shaft_power_W: float
    thrust_N: float
    blowing_momentum_coefficient: float
    motor_losses_W: float
    inverter_losses_W: float
    heat_loss_W: float


class ElectricBlownFlapFan:
    """Power-over-velocity proxy for a single electric blown-flap fan."""

    def __init__(
        self,
        nominal_power_W: float,
        max_power_W_for_v02: float,
        propulsive_efficiency: float,
        min_effective_airspeed_mps: float,
        mode_power_fractions: dict[str, float],
        motor: MotorModel,
        inverter: InverterModel,
    ) -> None:
        if nominal_power_W < 0.0 or max_power_W_for_v02 < 0.0:
            raise ValueError("fan power levels must be non-negative")
        if propulsive_efficiency <= 0.0 or propulsive_efficiency > 1.0:
            raise ValueError("propulsive_efficiency must be in the range (0, 1]")
        if min_effective_airspeed_mps <= 0.0:
            raise ValueError("min_effective_airspeed_mps must be positive")
        missing = [mode for mode in FAN_MODES if mode not in mode_power_fractions]
        if missing:
            raise ValueError(f"missing fan mode power fractions: {', '.join(missing)}")

        self.nominal_power_W = nominal_power_W
        self.max_power_W_for_v02 = max_power_W_for_v02
        self.propulsive_efficiency = propulsive_efficiency
        self.min_effective_airspeed_mps = min_effective_airspeed_mps
        self.mode_power_fractions = dict(mode_power_fractions)
        self.motor = motor
        self.inverter = inverter

    def requested_input_power_W(self, mode: str) -> float:
        """Return requested DC input power in W for a fan mode."""
        if mode not in FAN_MODES:
            raise ValueError(f"fan mode must be one of: {', '.join(FAN_MODES)}")
        if mode in ("off", "failed"):
            return 0.0
        requested = self.nominal_power_W * self.mode_power_fractions[mode]
        return min(requested, self.max_power_W_for_v02)

    def evaluate(self, command: ElectricFanCommand) -> ElectricFanPerformance:
        """Evaluate single-fan proxy thrust and blowing coefficient in SI units."""
        if command.mode not in FAN_MODES:
            raise ValueError(f"fan mode must be one of: {', '.join(FAN_MODES)}")
        if command.airspeed_mps < 0.0:
            raise ValueError("airspeed_mps must be non-negative")
        if command.density_kg_m3 <= 0.0:
            raise ValueError("density_kg_m3 must be positive")
        if command.wing_area_m2 <= 0.0:
            raise ValueError("wing_area_m2 must be positive")

        if command.mode in ("off", "failed"):
            return ElectricFanPerformance(
                mode=command.mode,
                input_power_W=0.0,
                inverter_output_power_W=0.0,
                shaft_power_W=0.0,
                thrust_N=0.0,
                blowing_momentum_coefficient=0.0,
                motor_losses_W=0.0,
                inverter_losses_W=0.0,
                heat_loss_W=0.0,
            )

        input_power_W = (
            command.input_power_W
            if command.input_power_W is not None
            else self.requested_input_power_W(command.mode)
        )
        if input_power_W < 0.0:
            raise ValueError("input_power_W must be non-negative")
        input_power_W = min(input_power_W, self.max_power_W_for_v02)

        inverter_result = self.inverter.evaluate(input_power_W)
        motor_result = self.motor.evaluate_electric_to_shaft(inverter_result.output_power_W)
        effective_speed_mps = max(command.airspeed_mps, self.min_effective_airspeed_mps)
        thrust_N = self.propulsive_efficiency * motor_result.shaft_power_W / effective_speed_mps
        dynamic_pressure_Pa = 0.5 * command.density_kg_m3 * command.airspeed_mps**2
        if dynamic_pressure_Pa > 0.0:
            c_mu = thrust_N / (dynamic_pressure_Pa * command.wing_area_m2)
        else:
            c_mu = 0.0

        return ElectricFanPerformance(
            mode=command.mode,
            input_power_W=input_power_W,
            inverter_output_power_W=inverter_result.output_power_W,
            shaft_power_W=motor_result.shaft_power_W,
            thrust_N=thrust_N,
            blowing_momentum_coefficient=c_mu,
            motor_losses_W=motor_result.losses_W,
            inverter_losses_W=inverter_result.losses_W,
            heat_loss_W=motor_result.losses_W + inverter_result.losses_W,
        )
