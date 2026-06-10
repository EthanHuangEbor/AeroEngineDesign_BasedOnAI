from pathlib import Path

from mta_vhep.aircraft.aerodynamics import (
    AeroModel,
    AeroState,
    drag_polar_cd,
    induced_drag_factor,
    stall_speed_mps,
)
from mta_vhep.core.atmosphere import isa_atmosphere
from mta_vhep.core.units import kg_to_N
from mta_vhep.interfaces.io import load_aircraft_baseline, load_yaml


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def test_induced_drag_factor_is_positive() -> None:
    assert induced_drag_factor(9.5, 0.78) > 0.0


def test_cd_increases_with_cl_for_fixed_cd0() -> None:
    cd_low = drag_polar_cd(0.3, 0.026, 9.5, 0.78)
    cd_high = drag_polar_cd(0.7, 0.026, 9.5, 0.78)

    assert cd_high > cd_low


def test_stall_speed_decreases_when_clmax_increases() -> None:
    weight_N = kg_to_N(87500.0)
    rho = isa_atmosphere(0.0).density_kg_m3

    clean_speed = stall_speed_mps(weight_N, rho, 160.0, 1.55)
    high_lift_speed = stall_speed_mps(weight_N, rho, 160.0, 2.75)

    assert high_lift_speed < clean_speed


def test_landing_flap_clmax_is_greater_than_clean() -> None:
    model = AeroModel.from_config(load_yaml(CONFIG_DIR / "aero_model.yaml"))

    assert model.clmax_by_flap_mode["landing_flap"] > model.clmax_by_flap_mode["clean"]


def test_blowing_momentum_coefficient_increases_clmax() -> None:
    model = AeroModel.from_config(load_yaml(CONFIG_DIR / "aero_model.yaml"))
    aircraft, geometry, _ = load_aircraft_baseline(CONFIG_DIR)
    atmosphere = isa_atmosphere(aircraft.cruise_altitude_m)
    base_state = AeroState(
        mach=aircraft.cruise_mach,
        altitude_m=aircraft.cruise_altitude_m,
        weight_N=kg_to_N(aircraft.mtow_initial_kg),
        wing_area_m2=geometry.wing_area_m2_initial,
        flap_mode="takeoff_flap",
        gear_down=False,
        blowing_momentum_coefficient=0.0,
    )
    blown_state = AeroState(
        mach=aircraft.cruise_mach,
        altitude_m=aircraft.cruise_altitude_m,
        weight_N=kg_to_N(aircraft.mtow_initial_kg),
        wing_area_m2=geometry.wing_area_m2_initial,
        flap_mode="takeoff_flap",
        gear_down=False,
        blowing_momentum_coefficient=0.08,
    )

    assert model.evaluate(blown_state, atmosphere).cl_max > model.evaluate(
        base_state, atmosphere
    ).cl_max


def test_clean_cruise_ld_is_in_validation_range() -> None:
    config = load_yaml(CONFIG_DIR / "aero_model.yaml")
    model = AeroModel.from_config(config)
    aircraft, geometry, _ = load_aircraft_baseline(CONFIG_DIR)
    atmosphere = isa_atmosphere(aircraft.cruise_altitude_m)
    performance = model.evaluate(
        AeroState(
            mach=aircraft.cruise_mach,
            altitude_m=aircraft.cruise_altitude_m,
            weight_N=kg_to_N(aircraft.mtow_initial_kg),
            wing_area_m2=geometry.wing_area_m2_initial,
            flap_mode="clean",
            gear_down=False,
            blowing_momentum_coefficient=0.0,
        ),
        atmosphere,
    )

    validation = config["aero"]["validation"]
    assert validation["min_ld_clean_cruise"] <= performance.ld_ratio
    assert performance.ld_ratio <= validation["max_ld_clean_cruise"]
