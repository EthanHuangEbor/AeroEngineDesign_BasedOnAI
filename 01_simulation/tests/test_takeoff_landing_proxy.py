from mta_vhep.mission.takeoff_landing import (
    landing_performance_proxy,
    takeoff_performance_proxy,
)


def test_takeoff_proxy_improves_with_higher_clmax() -> None:
    base = takeoff_performance_proxy(
        weight_N=850000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.2,
        effective_thrust_N=220000.0,
    )
    higher_clmax = takeoff_performance_proxy(
        weight_N=850000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.8,
        effective_thrust_N=220000.0,
    )

    assert higher_clmax.field_length_index < base.field_length_index


def test_takeoff_proxy_improves_with_higher_effective_thrust() -> None:
    base = takeoff_performance_proxy(
        weight_N=850000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.2,
        effective_thrust_N=180000.0,
    )
    higher_thrust = takeoff_performance_proxy(
        weight_N=850000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.2,
        effective_thrust_N=240000.0,
    )

    assert higher_thrust.field_length_index < base.field_length_index


def test_landing_proxy_improves_with_higher_clmax_or_effective_thrust() -> None:
    base = landing_performance_proxy(
        weight_N=760000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.4,
        effective_thrust_N=20000.0,
    )
    higher_clmax = landing_performance_proxy(
        weight_N=760000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.9,
        effective_thrust_N=20000.0,
    )
    higher_thrust = landing_performance_proxy(
        weight_N=760000.0,
        density_kg_m3=1.225,
        wing_area_m2=160.0,
        clmax=2.4,
        effective_thrust_N=60000.0,
    )

    assert higher_clmax.field_length_index < base.field_length_index
    assert higher_thrust.field_length_index < base.field_length_index
