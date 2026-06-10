"""Quasi-steady electrical bus power balance for MTA-VHEP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ElectricalLoad:
    """Electrical load request in W."""

    name: str
    power_W: float


@dataclass(frozen=True)
class ElectricalBusState:
    """Electrical bus balance state using SI power units."""

    generated_power_W: float
    battery_power_W: float
    requested_load_power_W: float
    supplied_load_power_W: float
    distribution_losses_W: float
    unmet_load_W: float
    residual_power_W: float
    thermal_load_W: float


class ElectricalBus:
    """Quasi-steady electrical bus with cable distribution efficiency."""

    def __init__(
        self,
        voltage_V: float,
        cable_distribution_efficiency: float,
        load_shedding_enabled: bool,
    ) -> None:
        if voltage_V <= 0.0:
            raise ValueError("voltage_V must be positive")
        if cable_distribution_efficiency <= 0.0 or cable_distribution_efficiency > 1.0:
            raise ValueError("cable_distribution_efficiency must be in the range (0, 1]")
        self.voltage_V = voltage_V
        self.cable_distribution_efficiency = cable_distribution_efficiency
        self.load_shedding_enabled = load_shedding_enabled

    def solve(
        self,
        loads: list[ElectricalLoad],
        generated_power_W: float,
        battery_power_W: float,
    ) -> ElectricalBusState:
        """Solve bus balance with generated and battery power in W."""
        if generated_power_W < 0.0 or battery_power_W < 0.0:
            raise ValueError("generated_power_W and battery_power_W must be non-negative")
        requested_load_power_W = 0.0
        for load in loads:
            if load.power_W < 0.0:
                raise ValueError(f"load {load.name} power_W must be non-negative")
            requested_load_power_W += load.power_W

        source_power_W = generated_power_W + battery_power_W
        load_capacity_W = source_power_W * self.cable_distribution_efficiency

        if load_capacity_W >= requested_load_power_W:
            supplied_load_power_W = requested_load_power_W
            source_used_W = (
                supplied_load_power_W / self.cable_distribution_efficiency
                if supplied_load_power_W > 0.0
                else 0.0
            )
            unmet_load_W = 0.0
        else:
            supplied_load_power_W = load_capacity_W if self.load_shedding_enabled else load_capacity_W
            source_used_W = source_power_W
            unmet_load_W = max(requested_load_power_W - supplied_load_power_W, 0.0)

        distribution_losses_W = max(source_used_W - supplied_load_power_W, 0.0)
        residual_power_W = source_power_W - supplied_load_power_W - distribution_losses_W

        return ElectricalBusState(
            generated_power_W=generated_power_W,
            battery_power_W=battery_power_W,
            requested_load_power_W=requested_load_power_W,
            supplied_load_power_W=supplied_load_power_W,
            distribution_losses_W=distribution_losses_W,
            unmet_load_W=unmet_load_W,
            residual_power_W=residual_power_W,
            thermal_load_W=distribution_losses_W,
        )
