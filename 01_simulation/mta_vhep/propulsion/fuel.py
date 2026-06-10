"""Fuel property helpers for MTA-VHEP concept-level studies."""

from mta_vhep.interfaces.schemas import FuelProperties


def get_fuel(fuels: dict[str, FuelProperties], name: str) -> FuelProperties:
    """Return named fuel properties from a fuel database mapping."""
    try:
        return fuels[name]
    except KeyError as exc:
        available = ", ".join(sorted(fuels))
        raise KeyError(f"Fuel {name!r} is not available. Known fuels: {available}") from exc


def blend_fuel(
    jet_a: FuelProperties,
    saf: FuelProperties,
    saf_blend_ratio: float,
) -> FuelProperties:
    """Blend Jet-A and SAF properties by SAF mass fraction from 0 to 1.

    Lower heating value, density, and direct carbon emission factor use simple
    mass-fraction blending for this concept-level property helper. Lifecycle
    factor remains None unless both input fuels define lifecycle factors.
    """
    if saf_blend_ratio < 0.0 or saf_blend_ratio > 1.0:
        raise ValueError("saf_blend_ratio must be between 0 and 1")

    jet_a_fraction = 1.0 - saf_blend_ratio
    lifecycle_factor = None
    if (
        jet_a.lifecycle_factor_kgCO2e_per_kg is not None
        and saf.lifecycle_factor_kgCO2e_per_kg is not None
    ):
        lifecycle_factor = (
            jet_a_fraction * jet_a.lifecycle_factor_kgCO2e_per_kg
            + saf_blend_ratio * saf.lifecycle_factor_kgCO2e_per_kg
        )

    return FuelProperties(
        name=f"Jet-A_SAF_blend_{saf_blend_ratio:.2f}",
        lower_heating_value_J_per_kg=(
            jet_a_fraction * jet_a.lower_heating_value_J_per_kg
            + saf_blend_ratio * saf.lower_heating_value_J_per_kg
        ),
        density_kg_per_m3=(
            jet_a_fraction * jet_a.density_kg_per_m3
            + saf_blend_ratio * saf.density_kg_per_m3
        ),
        carbon_emission_factor_kgCO2_per_kg=(
            jet_a_fraction * jet_a.carbon_emission_factor_kgCO2_per_kg
            + saf_blend_ratio * saf.carbon_emission_factor_kgCO2_per_kg
        ),
        lifecycle_factor_kgCO2e_per_kg=lifecycle_factor,
        blend_ratio_saf=saf_blend_ratio,
    )


def fuel_co2_from_burn(fuel_burn_kg: float, fuel: FuelProperties) -> float:
    """Return direct CO2 mass in kg from fuel burn mass in kg."""
    if fuel_burn_kg < 0.0:
        raise ValueError("fuel_burn_kg must be non-negative")
    return fuel_burn_kg * fuel.carbon_emission_factor_kgCO2_per_kg
