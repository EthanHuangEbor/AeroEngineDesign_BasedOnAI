from mta_vhep.mission.approach_analysis import (
    ApproachForceBalanceInput,
    evaluate_approach_force_balance,
)


def _input(
    gamma_deg: float,
    drag_N: float = 100000.0,
    available_thrust_N: float = 80000.0,
    electric_thrust_proxy_N: float = 0.0,
) -> ApproachForceBalanceInput:
    return ApproachForceBalanceInput(
        case_name="test_case",
        segment_name="approach_landing",
        weight_N=800000.0,
        speed_mps=70.0,
        altitude_m=250.0,
        gamma_deg=gamma_deg,
        drag_N=drag_N,
        available_thrust_N=available_thrust_N,
        electric_thrust_proxy_N=electric_thrust_proxy_N,
    )


def test_negative_descent_angle_reduces_required_thrust() -> None:
    level = evaluate_approach_force_balance(_input(gamma_deg=0.0))
    descent = evaluate_approach_force_balance(_input(gamma_deg=-3.0))

    assert descent.required_thrust_descent_N < level.required_thrust_descent_N


def test_zero_descent_angle_returns_level_flight_requirement() -> None:
    result = evaluate_approach_force_balance(_input(gamma_deg=0.0))

    assert result.required_thrust_descent_N == result.required_thrust_level_flight_N


def test_larger_drag_factor_increases_required_thrust() -> None:
    low_drag = evaluate_approach_force_balance(_input(gamma_deg=-3.0, drag_N=90000.0))
    high_drag = evaluate_approach_force_balance(_input(gamma_deg=-3.0, drag_N=120000.0))

    assert high_drag.required_thrust_descent_N > low_drag.required_thrust_descent_N


def test_higher_available_thrust_improves_margin() -> None:
    low_thrust = evaluate_approach_force_balance(
        _input(gamma_deg=-3.0, available_thrust_N=70000.0)
    )
    high_thrust = evaluate_approach_force_balance(
        _input(gamma_deg=-3.0, available_thrust_N=120000.0)
    )

    assert high_thrust.thrust_margin_descent_N > low_thrust.thrust_margin_descent_N


def test_electric_thrust_proxy_reduces_net_required_thrust() -> None:
    no_electric = evaluate_approach_force_balance(_input(gamma_deg=-3.0))
    with_electric = evaluate_approach_force_balance(
        _input(gamma_deg=-3.0, electric_thrust_proxy_N=15000.0)
    )

    assert (
        with_electric.net_required_thrust_after_electric_N
        < no_electric.net_required_thrust_after_electric_N
    )
