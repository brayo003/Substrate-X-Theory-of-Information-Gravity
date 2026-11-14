from __future__ import annotations

from .physical_field_domain import (
    register,
    initialize_physical_field,
    set_field_parameters,
    reset_field_state,
    set_nonlinear_reaction_parameters,
    get_reaction_parameters,
    set_reaction_parameters,
)
from .physical_field_models import (
    PhysicalCoordinate,
    PhysicalMetric,
    InformationDensityField,
    FieldState,
    PropagationParameters,
    RelaxationParameters,
    NonlinearReactionParameters,
    QObservation,
    SpectralTransportObservable,
)
from .physical_field_dynamics import (
    evolve_field,
    evolve_field_nonlinear,
    apply_perturbation,
    measure_propagation_speed,
    measure_relaxation_time,
    compute_gradient,
    compute_theoretical_q,
    compute_spectral_transport_observable,
    compute_independent_observables,
)
from .substrate_state import SubstrateState
from .legacy_q_isolation import LegacyQIsolation
from .substrate_coupling import SubstrateCoupling
from .controlled_experiments import ControlledExperiments

__all__ = [
    "register",
    "initialize_physical_field",
    "set_field_parameters",
    "reset_field_state",
    "set_nonlinear_reaction_parameters",
    "get_reaction_parameters",
    "set_reaction_parameters",
    "PhysicalCoordinate",
    "PhysicalMetric",
    "InformationDensityField",
    "FieldState",
    "PropagationParameters",
    "RelaxationParameters",
    "NonlinearReactionParameters",
    "QObservation",
    "SpectralTransportObservable",
    "evolve_field",
    "evolve_field_nonlinear",
    "apply_perturbation",
    "measure_propagation_speed",
    "measure_relaxation_time",
    "compute_gradient",
    "compute_theoretical_q",
    "compute_spectral_transport_observable",
    "compute_independent_observables",
    "SubstrateState",
    "LegacyQIsolation",
    "SubstrateCoupling",
    "ControlledExperiments",
]
