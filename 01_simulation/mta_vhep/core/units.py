"""Small SI unit conversion helpers for MTA-VHEP."""

from mta_vhep.core.constants import GRAVITY_M_PER_S2, J_PER_WH, M_PER_KM


def kg_to_N(mass_kg: float) -> float:
    """Convert mass in kilograms to weight in newtons using standard gravity."""
    return mass_kg * GRAVITY_M_PER_S2


def km_to_m(distance_km: float) -> float:
    """Convert distance in kilometers to meters."""
    return distance_km * M_PER_KM


def m_to_km(distance_m: float) -> float:
    """Convert distance in meters to kilometers."""
    return distance_m / M_PER_KM


def Wh_to_J(energy_Wh: float) -> float:
    """Convert energy in watt-hours to joules."""
    return energy_Wh * J_PER_WH


def J_to_Wh(energy_J: float) -> float:
    """Convert energy in joules to watt-hours."""
    return energy_J / J_PER_WH
