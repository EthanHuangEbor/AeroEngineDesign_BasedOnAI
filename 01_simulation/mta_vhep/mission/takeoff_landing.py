"""First-order takeoff and landing proxy indicators for MTA-VHEP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldLengthProxy:
    """Non-certified field-length proxy using SI inputs.

    Lower field_length_index values are directionally better. This is a
    normalized concept indicator, not a certified takeoff or landing distance.
    """

    field_length_index: float
    wing_loading_N_m2: float
    thrust_to_weight: float
    clmax: float


def takeoff_performance_proxy(
    weight_N: float,
    density_kg_m3: float,
    wing_area_m2: float,
    clmax: float,
    effective_thrust_N: float,
) -> FieldLengthProxy:
    """Return a takeoff proxy index from weight N, density kg/m^3, area m^2.

    The index decreases when CLmax, density, wing area, or effective thrust
    improves. It is a concept-level trend metric only.
    """
    _validate_inputs(weight_N, density_kg_m3, wing_area_m2, clmax, effective_thrust_N)
    wing_loading_N_m2 = weight_N / wing_area_m2
    thrust_to_weight = effective_thrust_N / weight_N
    field_length_index = wing_loading_N_m2 / (
        density_kg_m3 * clmax * max(thrust_to_weight, 1.0e-6)
    )
    return FieldLengthProxy(
        field_length_index=field_length_index,
        wing_loading_N_m2=wing_loading_N_m2,
        thrust_to_weight=thrust_to_weight,
        clmax=clmax,
    )


def landing_performance_proxy(
    weight_N: float,
    density_kg_m3: float,
    wing_area_m2: float,
    clmax: float,
    effective_thrust_N: float,
) -> FieldLengthProxy:
    """Return a landing proxy index from weight N, density kg/m^3, area m^2.

    Effective thrust is treated as a small deceleration or reverse-thrust proxy
    credit. This is not a certified landing field length prediction.
    """
    _validate_inputs(weight_N, density_kg_m3, wing_area_m2, clmax, effective_thrust_N)
    wing_loading_N_m2 = weight_N / wing_area_m2
    thrust_to_weight = effective_thrust_N / weight_N
    field_length_index = wing_loading_N_m2 / (
        density_kg_m3 * clmax * (1.0 + max(thrust_to_weight, 0.0))
    )
    return FieldLengthProxy(
        field_length_index=field_length_index,
        wing_loading_N_m2=wing_loading_N_m2,
        thrust_to_weight=thrust_to_weight,
        clmax=clmax,
    )


def _validate_inputs(
    weight_N: float,
    density_kg_m3: float,
    wing_area_m2: float,
    clmax: float,
    effective_thrust_N: float,
) -> None:
    if weight_N <= 0.0:
        raise ValueError("weight_N must be positive")
    if density_kg_m3 <= 0.0:
        raise ValueError("density_kg_m3 must be positive")
    if wing_area_m2 <= 0.0:
        raise ValueError("wing_area_m2 must be positive")
    if clmax <= 0.0:
        raise ValueError("clmax must be positive")
    if effective_thrust_N < 0.0:
        raise ValueError("effective_thrust_N must be non-negative")
