"""Approach/landing force-balance audit helpers for MTA-VHEP."""

from dataclasses import dataclass
from math import radians, sin


@dataclass(frozen=True)
class ApproachForceBalanceInput:
    """Approach force-balance input using SI units."""

    case_name: str
    segment_name: str
    weight_N: float
    speed_mps: float
    altitude_m: float
    gamma_deg: float
    drag_N: float
    available_thrust_N: float
    electric_thrust_proxy_N: float
    include_weight_component_along_path: bool = True


@dataclass(frozen=True)
class ApproachForceBalanceResult:
    """Approach force-balance audit result using SI units."""

    case_name: str
    segment_name: str
    weight_N: float
    speed_mps: float
    altitude_m: float
    gamma_deg: float
    drag_N: float
    weight_component_along_path_N: float
    required_thrust_level_flight_N: float
    required_thrust_descent_N: float
    available_thrust_N: float
    electric_thrust_proxy_N: float
    net_required_thrust_after_electric_N: float
    thrust_margin_level_flight_N: float
    thrust_margin_descent_N: float
    thrust_margin_change_due_to_descent_N: float
    conclusion_flag: str


def evaluate_approach_force_balance(
    data: ApproachForceBalanceInput,
) -> ApproachForceBalanceResult:
    """Evaluate quasi-steady approach thrust balance.

    Drag, thrust, and weight are in N; speed is in m/s; altitude is in m; gamma
    is in degrees and is negative for descent. This is a concept-level force
    balance audit, not a flight-dynamics or certification model.
    """
    _validate_input(data)

    required_level_N = data.drag_N
    weight_component_N = 0.0
    if data.include_weight_component_along_path:
        weight_component_N = data.weight_N * sin(radians(data.gamma_deg))
    required_descent_N = max(data.drag_N + weight_component_N, 0.0)
    net_required_after_electric_N = max(
        required_descent_N - data.electric_thrust_proxy_N,
        0.0,
    )
    level_margin_N = data.available_thrust_N - required_level_N
    descent_margin_N = data.available_thrust_N - required_descent_N
    margin_change_N = descent_margin_N - level_margin_N

    if level_margin_N < 0.0 <= descent_margin_N:
        conclusion = "constraint_sensitive_to_approach_model"
    elif descent_margin_N < 0.0:
        conclusion = "sizing_or_schedule_issue"
    else:
        conclusion = "no_low_margin_in_force_balance"

    return ApproachForceBalanceResult(
        case_name=data.case_name,
        segment_name=data.segment_name,
        weight_N=data.weight_N,
        speed_mps=data.speed_mps,
        altitude_m=data.altitude_m,
        gamma_deg=data.gamma_deg,
        drag_N=data.drag_N,
        weight_component_along_path_N=weight_component_N,
        required_thrust_level_flight_N=required_level_N,
        required_thrust_descent_N=required_descent_N,
        available_thrust_N=data.available_thrust_N,
        electric_thrust_proxy_N=data.electric_thrust_proxy_N,
        net_required_thrust_after_electric_N=net_required_after_electric_N,
        thrust_margin_level_flight_N=level_margin_N,
        thrust_margin_descent_N=descent_margin_N,
        thrust_margin_change_due_to_descent_N=margin_change_N,
        conclusion_flag=conclusion,
    )


def _validate_input(data: ApproachForceBalanceInput) -> None:
    if data.weight_N <= 0.0:
        raise ValueError("weight_N must be positive")
    if data.speed_mps <= 0.0:
        raise ValueError("speed_mps must be positive")
    if data.altitude_m < 0.0:
        raise ValueError("altitude_m must be non-negative")
    if data.drag_N < 0.0:
        raise ValueError("drag_N must be non-negative")
    if data.available_thrust_N < 0.0:
        raise ValueError("available_thrust_N must be non-negative")
    if data.electric_thrust_proxy_N < 0.0:
        raise ValueError("electric_thrust_proxy_N must be non-negative")
