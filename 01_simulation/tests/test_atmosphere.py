import pytest

from mta_vhep.core.atmosphere import isa_atmosphere


def test_sea_level_isa_values() -> None:
    state = isa_atmosphere(0.0)

    assert state.temperature_K == pytest.approx(288.15, abs=0.01)
    assert state.pressure_Pa == pytest.approx(101325.0, rel=0.001)
    assert state.density_kg_m3 == pytest.approx(1.225, rel=0.005)


def test_density_decreases_with_altitude() -> None:
    sea_level = isa_atmosphere(0.0)
    high_altitude = isa_atmosphere(10000.0)

    assert high_altitude.density_kg_m3 < sea_level.density_kg_m3


def test_speed_of_sound_decreases_in_troposphere() -> None:
    sea_level = isa_atmosphere(0.0)
    high_altitude = isa_atmosphere(10000.0)

    assert high_altitude.speed_of_sound_mps < sea_level.speed_of_sound_mps


def test_altitude_bounds_raise_value_error() -> None:
    with pytest.raises(ValueError):
        isa_atmosphere(-1.0)

    with pytest.raises(ValueError):
        isa_atmosphere(12000.1)
