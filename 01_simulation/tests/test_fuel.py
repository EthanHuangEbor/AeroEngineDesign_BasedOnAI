from pathlib import Path

import pytest

from mta_vhep.interfaces.io import load_fuel_database
from mta_vhep.propulsion.fuel import blend_fuel, fuel_co2_from_burn, get_fuel


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def test_fuel_database_contains_baseline_fuels() -> None:
    fuels = load_fuel_database(CONFIG_DIR)

    assert "Jet-A" in fuels
    assert "SAF_generic" in fuels
    assert get_fuel(fuels, "Jet-A").lower_heating_value_J_per_kg > 0.0


def test_saf_blend_endpoints_match_inputs() -> None:
    fuels = load_fuel_database(CONFIG_DIR)
    jet_a = get_fuel(fuels, "Jet-A")
    saf = get_fuel(fuels, "SAF_generic")

    blend_0 = blend_fuel(jet_a, saf, 0.0)
    blend_1 = blend_fuel(jet_a, saf, 1.0)

    assert blend_0.lower_heating_value_J_per_kg == pytest.approx(
        jet_a.lower_heating_value_J_per_kg
    )
    assert blend_0.density_kg_per_m3 == pytest.approx(jet_a.density_kg_per_m3)
    assert blend_1.lower_heating_value_J_per_kg == pytest.approx(
        saf.lower_heating_value_J_per_kg
    )
    assert blend_1.density_kg_per_m3 == pytest.approx(saf.density_kg_per_m3)


def test_saf_blend_ratio_bounds() -> None:
    fuels = load_fuel_database(CONFIG_DIR)
    jet_a = get_fuel(fuels, "Jet-A")
    saf = get_fuel(fuels, "SAF_generic")

    with pytest.raises(ValueError):
        blend_fuel(jet_a, saf, -0.01)

    with pytest.raises(ValueError):
        blend_fuel(jet_a, saf, 1.01)


def test_jet_a_co2_from_burn_is_positive() -> None:
    fuels = load_fuel_database(CONFIG_DIR)
    jet_a = get_fuel(fuels, "Jet-A")

    assert fuel_co2_from_burn(1000.0, jet_a) > 0.0
