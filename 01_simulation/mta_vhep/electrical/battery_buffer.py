"""Short-duration battery buffer model for MTA-VHEP."""

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class BatteryBufferState:
    """Battery buffer state using SOC fraction and stored energy in Wh."""

    soc: float
    stored_energy_Wh: float


@dataclass(frozen=True)
class BatteryBufferStepResult:
    """Battery update result using SI power units and Wh energy units."""

    requested_power_W: float
    battery_power_W: float
    unmet_power_W: float
    rejected_charge_power_W: float
    soc_initial: float
    soc_final: float
    energy_delta_Wh: float


class BatteryBuffer:
    """Battery buffer for short-duration peak-power support."""

    def __init__(
        self,
        capacity_Wh: float,
        initial_soc: float,
        min_soc: float,
        max_soc: float,
        max_discharge_power_W: float,
        max_charge_power_W: float,
        roundtrip_efficiency: float,
    ) -> None:
        if capacity_Wh <= 0.0:
            raise ValueError("capacity_Wh must be positive")
        if not 0.0 <= min_soc <= max_soc <= 1.0:
            raise ValueError("SOC bounds must satisfy 0 <= min_soc <= max_soc <= 1")
        if not 0.0 <= initial_soc <= 1.0:
            raise ValueError("initial_soc must be between 0 and 1")
        if max_discharge_power_W < 0.0 or max_charge_power_W < 0.0:
            raise ValueError("battery power limits must be non-negative")
        if roundtrip_efficiency <= 0.0 or roundtrip_efficiency > 1.0:
            raise ValueError("roundtrip_efficiency must be in the range (0, 1]")

        self.capacity_Wh = capacity_Wh
        self.min_soc = min_soc
        self.max_soc = max_soc
        self.max_discharge_power_W = max_discharge_power_W
        self.max_charge_power_W = max_charge_power_W
        self.charge_efficiency = sqrt(roundtrip_efficiency)
        self.discharge_efficiency = sqrt(roundtrip_efficiency)
        self._soc = min(max(initial_soc, 0.0), 1.0)

    @property
    def state(self) -> BatteryBufferState:
        """Return current state of charge and stored energy in Wh."""
        return BatteryBufferState(
            soc=self._soc,
            stored_energy_Wh=self._soc * self.capacity_Wh,
        )

    def update(self, requested_power_W: float, duration_s: float) -> BatteryBufferStepResult:
        """Update battery state for requested power in W over duration in seconds.

        Positive requested power discharges the battery to supply the bus.
        Negative requested power charges the battery. SOC bounds are enforced.
        """
        if duration_s <= 0.0:
            raise ValueError("duration_s must be positive")

        soc_initial = self._soc
        if requested_power_W >= 0.0:
            result = self._discharge(requested_power_W, duration_s, soc_initial)
        else:
            result = self._charge(-requested_power_W, duration_s, soc_initial)

        self._soc = min(max(result.soc_final, 0.0), 1.0)
        return result

    def _discharge(
        self,
        requested_power_W: float,
        duration_s: float,
        soc_initial: float,
    ) -> BatteryBufferStepResult:
        available_Wh = max((soc_initial - self.min_soc) * self.capacity_Wh, 0.0)
        energy_limited_power_W = (
            available_Wh * self.discharge_efficiency * 3600.0 / duration_s
        )
        supplied_power_W = min(
            requested_power_W,
            self.max_discharge_power_W,
            energy_limited_power_W,
        )
        stored_energy_removed_Wh = (
            supplied_power_W * duration_s / 3600.0 / self.discharge_efficiency
            if supplied_power_W > 0.0
            else 0.0
        )
        soc_final = soc_initial - stored_energy_removed_Wh / self.capacity_Wh
        return BatteryBufferStepResult(
            requested_power_W=requested_power_W,
            battery_power_W=supplied_power_W,
            unmet_power_W=max(requested_power_W - supplied_power_W, 0.0),
            rejected_charge_power_W=0.0,
            soc_initial=soc_initial,
            soc_final=max(soc_final, self.min_soc),
            energy_delta_Wh=-stored_energy_removed_Wh,
        )

    def _charge(
        self,
        requested_charge_power_W: float,
        duration_s: float,
        soc_initial: float,
    ) -> BatteryBufferStepResult:
        remaining_Wh = max((self.max_soc - soc_initial) * self.capacity_Wh, 0.0)
        capacity_limited_input_power_W = (
            remaining_Wh * 3600.0 / duration_s / self.charge_efficiency
        )
        accepted_power_W = min(
            requested_charge_power_W,
            self.max_charge_power_W,
            capacity_limited_input_power_W,
        )
        stored_energy_added_Wh = accepted_power_W * duration_s / 3600.0 * self.charge_efficiency
        soc_final = soc_initial + stored_energy_added_Wh / self.capacity_Wh
        return BatteryBufferStepResult(
            requested_power_W=-requested_charge_power_W,
            battery_power_W=-accepted_power_W,
            unmet_power_W=0.0,
            rejected_charge_power_W=max(requested_charge_power_W - accepted_power_W, 0.0),
            soc_initial=soc_initial,
            soc_final=min(soc_final, self.max_soc),
            energy_delta_Wh=stored_energy_added_Wh,
        )
