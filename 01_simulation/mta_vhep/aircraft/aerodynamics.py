"""Concept-level drag polar and stall-speed model for MTA-VHEP."""

from dataclasses import dataclass
from math import pi, sqrt
from typing import Any

from mta_vhep.core.atmosphere import AtmosphereState

FLAP_MODES = ("clean", "takeoff_flap", "landing_flap")
GEAR_DRAG_INCREMENT_CD = 0.020


@dataclass(frozen=True)
class AeroState:
    """Aerodynamic evaluation state using SI units."""

    mach: float
    altitude_m: float
    weight_N: float
    wing_area_m2: float
    flap_mode: str
    gear_down: bool
    blowing_momentum_coefficient: float


@dataclass(frozen=True)
class AeroPerformance:
    """Aerodynamic performance outputs using SI units."""

    cl: float
    cd: float
    ld_ratio: float
    cl_max: float
    stall_speed_mps: float


def induced_drag_factor(aspect_ratio: float, oswald_efficiency: float) -> float:
    """Return induced drag factor k for aspect ratio and Oswald efficiency."""
    if aspect_ratio <= 0.0:
        raise ValueError("aspect_ratio must be positive")
    if oswald_efficiency <= 0.0:
        raise ValueError("oswald_efficiency must be positive")
    return 1.0 / (pi * oswald_efficiency * aspect_ratio)


def drag_polar_cd(
    cl: float,
    cd0: float,
    aspect_ratio: float,
    oswald_efficiency: float,
) -> float:
    """Return drag coefficient CD using CD0 + k CL^2."""
    if cd0 < 0.0:
        raise ValueError("cd0 must be non-negative")
    return cd0 + induced_drag_factor(aspect_ratio, oswald_efficiency) * cl**2


def stall_speed_mps(
    weight_N: float,
    rho_kg_m3: float,
    wing_area_m2: float,
    clmax: float,
) -> float:
    """Return stall speed in m/s for weight N, density kg/m^3, area m^2, and CLmax."""
    if weight_N <= 0.0:
        raise ValueError("weight_N must be positive")
    if rho_kg_m3 <= 0.0:
        raise ValueError("rho_kg_m3 must be positive")
    if wing_area_m2 <= 0.0:
        raise ValueError("wing_area_m2 must be positive")
    if clmax <= 0.0:
        raise ValueError("clmax must be positive")
    return sqrt(2.0 * weight_N / (rho_kg_m3 * wing_area_m2 * clmax))


class AeroModel:
    """Concept-level parabolic drag polar model.

    Gear-down drag increment is a documented placeholder constant:
    GEAR_DRAG_INCREMENT_CD = 0.020. It is not a high-fidelity landing-gear
    drag prediction.
    """

    def __init__(
        self,
        cd0_by_flap_mode: dict[str, float],
        clmax_by_flap_mode: dict[str, float],
        aspect_ratio: float,
        oswald_efficiency: float,
        blowing_clmax_increment_per_cmu: float,
        blowing_cd_increment_per_cmu: float,
        cmu_max_for_v02: float,
        gear_drag_increment_cd: float = GEAR_DRAG_INCREMENT_CD,
    ) -> None:
        self.cd0_by_flap_mode = cd0_by_flap_mode
        self.clmax_by_flap_mode = clmax_by_flap_mode
        self.aspect_ratio = aspect_ratio
        self.oswald_efficiency = oswald_efficiency
        self.blowing_clmax_increment_per_cmu = blowing_clmax_increment_per_cmu
        self.blowing_cd_increment_per_cmu = blowing_cd_increment_per_cmu
        self.cmu_max_for_v02 = cmu_max_for_v02
        self.gear_drag_increment_cd = gear_drag_increment_cd

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "AeroModel":
        """Build an AeroModel from the aero_model.yaml mapping."""
        aero = _require_mapping(config.get("aero"), "aero")
        default = _require_mapping(aero.get("default"), "aero.default")
        clmax = _require_mapping(aero.get("clmax"), "aero.clmax")
        blowing = _require_mapping(aero.get("blowing"), "aero.blowing")

        cd0_by_flap_mode = {
            "clean": _require_number(default, "cd0_clean", "aero.default"),
            "takeoff_flap": _require_number(default, "cd0_takeoff_flap", "aero.default"),
            "landing_flap": _require_number(default, "cd0_landing_flap", "aero.default"),
        }
        clmax_by_flap_mode = {
            mode: _require_number(clmax, mode, "aero.clmax") for mode in FLAP_MODES
        }

        return cls(
            cd0_by_flap_mode=cd0_by_flap_mode,
            clmax_by_flap_mode=clmax_by_flap_mode,
            aspect_ratio=_require_number(default, "aspect_ratio", "aero.default"),
            oswald_efficiency=_require_number(
                default, "oswald_efficiency", "aero.default"
            ),
            blowing_clmax_increment_per_cmu=_require_number(
                blowing, "clmax_increment_per_cmu", "aero.blowing"
            ),
            blowing_cd_increment_per_cmu=_require_number(
                blowing, "cd_increment_per_cmu", "aero.blowing"
            ),
            cmu_max_for_v02=_require_number(blowing, "cmu_max_for_v02", "aero.blowing"),
        )

    def evaluate(self, state: AeroState, atmosphere: AtmosphereState) -> AeroPerformance:
        """Evaluate level-flight CL, CD, L/D, CLmax, and stall speed in SI units."""
        if state.flap_mode not in FLAP_MODES:
            raise ValueError(f"flap_mode must be one of: {', '.join(FLAP_MODES)}")
        if state.mach <= 0.0:
            raise ValueError("mach must be positive")
        if state.wing_area_m2 <= 0.0:
            raise ValueError("wing_area_m2 must be positive")
        if state.weight_N <= 0.0:
            raise ValueError("weight_N must be positive")
        cmu = state.blowing_momentum_coefficient
        if cmu < 0.0 or cmu > self.cmu_max_for_v02:
            raise ValueError(
                f"blowing_momentum_coefficient must be between 0 and {self.cmu_max_for_v02}"
            )

        speed_mps = state.mach * atmosphere.speed_of_sound_mps
        dynamic_pressure_Pa = 0.5 * atmosphere.density_kg_m3 * speed_mps**2
        cl = state.weight_N / (dynamic_pressure_Pa * state.wing_area_m2)

        cd0 = self.cd0_by_flap_mode[state.flap_mode]
        if state.gear_down:
            cd0 += self.gear_drag_increment_cd

        cl_max = self.clmax_by_flap_mode[state.flap_mode]
        if cmu > 0.0:
            cl_max += self.blowing_clmax_increment_per_cmu * cmu

        cd = drag_polar_cd(cl, cd0, self.aspect_ratio, self.oswald_efficiency)
        if cmu > 0.0:
            cd += self.blowing_cd_increment_per_cmu * cmu

        ld_ratio = cl / cd

        return AeroPerformance(
            cl=cl,
            cd=cd,
            ld_ratio=ld_ratio,
            cl_max=cl_max,
            stall_speed_mps=stall_speed_mps(
                state.weight_N,
                atmosphere.density_kg_m3,
                state.wing_area_m2,
                cl_max,
            ),
        )


def _require_mapping(value: Any, section: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{section} must be a mapping")
    return value


def _require_number(data: dict[str, Any], key: str, section: str) -> float:
    if key not in data:
        raise ValueError(f"Missing required key in {section}: {key}")
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{section}.{key} must be a number")
    return float(value)
