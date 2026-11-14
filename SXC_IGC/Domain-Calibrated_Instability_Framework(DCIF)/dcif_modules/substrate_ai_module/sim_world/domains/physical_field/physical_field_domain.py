from __future__ import annotations

from typing import Any
from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine
from .physical_field_models import (
    InformationDensityField,
    FieldState,
    PropagationParameters,
    RelaxationParameters,
    NonlinearReactionParameters,
    PhysicalCoordinate,
)
from .physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    evolve_field_nonlinear,
    compute_theoretical_q,
    compute_independent_observables,
    compute_spectral_transport_observable,
)


# Global field state (in production, this would be in kernel state)
_physical_field: InformationDensityField | None = None
_propagation_params: PropagationParameters = PropagationParameters(c_nominal=1.0)
_relaxation_params: RelaxationParameters = RelaxationParameters(tau_nominal=1.0)
_reaction_params: NonlinearReactionParameters = NonlinearReactionParameters()


def set_field_parameters(c_nominal: float | None = None, tau_nominal: float | None = None) -> None:
    """
    Set field parameters for controlled experimentation.
    
    This allows experiments to create worlds with different field conditions
    by setting parameters before field initialization.
    
    Args:
        c_nominal: Nominal propagation speed (m/s). If None, current value is preserved.
        tau_nominal: Nominal relaxation time (s). If None, current value is preserved.
    
    This is an experimental control mechanism - the field parameters
    influence the spectral observable which is exposed to agents.
    """
    global _propagation_params, _relaxation_params
    
    if c_nominal is not None:
        _propagation_params = PropagationParameters(c_nominal=float(c_nominal))
    
    if tau_nominal is not None:
        _relaxation_params = RelaxationParameters(tau_nominal=float(tau_nominal))


def set_nonlinear_reaction_parameters(
    r: float = 0.0,
    a: float = 0.0,
    b: float = 0.0,
) -> None:
    """Set nonlinear reaction coefficients for the global field.

    The active solver will use:
        τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + r·s + a·s² − b·s³

    Setting r=a=b=0 (the defaults) restores the linear telegraph equation.

    Args:
        r: Linear reaction coefficient (s⁻¹).
        a: Quadratic coefficient (1/(density·s)). Must be ≥ 0.
        b: Cubic saturation coefficient (1/(density²·s)). Must be ≥ 0.
    """
    global _reaction_params
    _reaction_params = NonlinearReactionParameters(r=r, a=a, b=b)


def reset_field_state() -> None:
    """
    Reset global field state to allow creation of independent worlds.
    """
    global _physical_field, _propagation_params, _relaxation_params, _reaction_params
    _physical_field = None
    _propagation_params = PropagationParameters(c_nominal=1.0)
    _relaxation_params = RelaxationParameters(tau_nominal=1.0)
    _reaction_params = NonlinearReactionParameters()


def register(engine: SimulationEngine) -> None:
    """Register physical field domain with simulation engine."""
    engine.register_domain("physical_field", lambda engine, context: (apply(context),))


def initialize_physical_field(kernel: Any) -> InformationDensityField:
    """Initialize the physical information density field.
    
    This creates the physical spatial domain and initial field state.
    Physical assumptions:
    - Domain size: 100m x 100m (physical meters)
    - Grid resolution: 50 x 50 points
    - Initial field value: 1.0 (normalized information density)
    - Time step: 0.1s (physical seconds)
    - Information units: bits
    - Spatial units: meters
    - Density units: bits/m³
    
    Note: Field parameters can be set via set_field_parameters() before
    calling this function to create worlds with different field conditions.
    """
    global _physical_field, _propagation_params, _relaxation_params
    
    # Initialize field state with physical coordinates
    state = initialize_field_state(
        x_range=(0.0, 100.0),  # 100 meters in x
        y_range=(0.0, 100.0),  # 100 meters in y
        nx=50,  # 50 grid points in x
        ny=50,  # 50 grid points in y
        initial_value=1.0,  # Initial information density
        dt=0.1,  # 0.1 second time step
    )
    
    # Calculate physical volume
    physical_volume = 100.0 * 100.0 * 1.0  # 100m x 100m x 1m
    
    # Create information density field
    _physical_field = InformationDensityField(
        state=state,
        information_quantity=1.0,  # Normalized information quantity
        physical_volume=physical_volume,
        information_units="bits",
        spatial_units="m",
        density_units="bits/m³",
    )
    
    # Ensure parameters are initialized (use defaults if not set via set_field_parameters)
    if _propagation_params.c_nominal == 1.0 and _propagation_params.c_measured == 0.0:
        # Still at default, ensure it's properly initialized
        _propagation_params = PropagationParameters(c_nominal=1.0)
    if _relaxation_params.tau_nominal == 1.0 and _relaxation_params.tau_measured == 0.0:
        # Still at default, ensure it's properly initialized
        _relaxation_params = RelaxationParameters(tau_nominal=1.0)
    
    return _physical_field


def apply(context: Any) -> TransitionProposal:
    """Apply physical field domain update.
    
    This evolves the field using the (possibly nonlinear) reaction-telegraph
    equation and computes spectral transport observables.
    """
    # Extract field state from context (per-world isolation)
    field_state_dict = getattr(context, 'physical_field_state', None)
    
    if field_state_dict is None:
        # Fallback to module-level globals for backward compatibility
        global _physical_field, _propagation_params, _relaxation_params, _reaction_params
        physical_field = _physical_field
        propagation_params = _propagation_params
        relaxation_params = _relaxation_params
        reaction_params = _reaction_params
    else:
        # Use per-world field state from context
        physical_field = field_state_dict.get("physical_field")
        propagation_params = field_state_dict.get("propagation_params")
        relaxation_params = field_state_dict.get("relaxation_params")
        reaction_params = field_state_dict.get(
            "reaction_params", NonlinearReactionParameters()
        )
    
    # Initialize field if not exists
    if physical_field is None:
        from .physical_field_dynamics import initialize_field_state
        physical_field = initialize_field_state()
        if propagation_params is None:
            propagation_params = PropagationParameters(c_nominal=1.0)
        if relaxation_params is None:
            relaxation_params = RelaxationParameters(tau_nominal=1.0)
        if reaction_params is None:
            reaction_params = NonlinearReactionParameters()
    
    # Evolve field — nonlinear solver falls through to linear when r=a=b=0
    physical_field = evolve_field_nonlinear(
        physical_field,
        propagation_params,
        relaxation_params,
        reaction_params,
    )
    
    # Compute spectral transport observable (validated field-level transport)
    spectral_observable = compute_spectral_transport_observable(
        physical_field,
        propagation_params,
        relaxation_params,
    )
    
    # Compute Q at representative points (DEPRECATED - kept for backward compatibility)
    q_observations = []
    grid_shape = physical_field.state.grid_shape
    
    # Sample Q at grid points (every 10th point for efficiency)
    for i in range(0, grid_shape[0], 10):
        for j in range(0, grid_shape[1], 10):
            coord = physical_field.state.coordinates[i * grid_shape[1] + j]
            physical_coord = PhysicalCoordinate(coord[0], coord[1], coord[2])
            
            q_obs = compute_theoretical_q(
                physical_field,
                propagation_params,
                relaxation_params,
                physical_coord,
            )
            
            q_observations.append({
                "x": float(physical_coord.x),
                "y": float(physical_coord.y),
                "z": float(physical_coord.z),
                "q_value": float(q_obs.q_value),
                "regime": str(q_obs.regime),
                "s_value": float(q_obs.s_value),
                "gradient_magnitude": float(q_obs.gradient_magnitude),
                "c_value": float(q_obs.c_value),
                "tau_value": float(q_obs.tau_value),
            })
    
    # Compute independent observables at center
    center_coord = PhysicalCoordinate(50.0, 50.0, 0.0)
    independent_obs = compute_independent_observables(physical_field, center_coord)
    
    # Create transition proposal
    patch = {
        "physical_field": {
            "field_values": physical_field.state.field_values.tolist(),
            "physical_time": float(physical_field.state.physical_time),
            "grid_shape": list(physical_field.state.grid_shape),
            "dx": float(physical_field.state.dx),
            "dy": float(physical_field.state.dy),
            "dz": float(physical_field.state.dz),
            "dt": float(physical_field.state.dt),
            "information_units": str(physical_field.information_units),
            "spatial_units": str(physical_field.spatial_units),
            "density_units": str(physical_field.density_units),
        },
        "propagation_parameters": {
            "c_nominal": float(propagation_params.c_nominal),
            "c_measured": float(propagation_params.c_measured),
            "c_uncertainty": float(propagation_params.c_uncertainty),
        },
        "relaxation_parameters": {
            "tau_nominal": float(relaxation_params.tau_nominal),
            "tau_measured": float(relaxation_params.tau_measured),
            "tau_uncertainty": float(relaxation_params.tau_uncertainty),
            "relaxation_law": str(relaxation_params.relaxation_law),
        },
        "reaction_parameters": {
            "r": float(reaction_params.r),
            "a": float(reaction_params.a),
            "b": float(reaction_params.b),
            "is_linear": bool(reaction_params.is_linear),
        },
        "spectral_transport_observable": {
            "physical_time": float(spectral_observable.physical_time),
            "dominant_k": float(spectral_observable.dominant_k),
            "dominant_D": float(spectral_observable.dominant_D),
            "dominant_regime": str(spectral_observable.dominant_regime),
            "propagating_power_fraction": float(spectral_observable.propagating_power_fraction),
            "overdamped_power_fraction": float(spectral_observable.overdamped_power_fraction),
            "critical_power_fraction": float(spectral_observable.critical_power_fraction),
            "weighted_D": float(spectral_observable.weighted_D),
            "spectral_entropy": float(spectral_observable.spectral_entropy),
            "c_spectral": float(spectral_observable.c_spectral),
            "c_nominal": float(spectral_observable.c_nominal),
            "tau_nominal": float(spectral_observable.tau_nominal),
            "k_critical": float(spectral_observable.k_critical),
            "spectral_resolution": float(spectral_observable.spectral_resolution),
            "domain_size": float(spectral_observable.domain_size),
            "num_modes": int(spectral_observable.num_modes),
            "metadata": dict(spectral_observable.metadata),
        },
        "q_observations": q_observations,  # DEPRECATED - kept for backward compatibility
        "independent_observables": independent_obs,
    }
    
    # Extract context for transition proposal
    try:
        world_id = getattr(context, 'world_id', None)
        tick_context = getattr(context, 'tick_context', None)
        tick_id = getattr(tick_context, 'tick_id', None) if tick_context else None
        committed_revision = getattr(context, 'committed_revision', None)
        correlation_id = getattr(tick_context, 'correlation_id', None) if tick_context else None
    except Exception:
        world_id = None
        tick_id = None
        committed_revision = None
        correlation_id = None
    
    return TransitionProposal(
        world_id=world_id,
        tick_id=tick_id,
        state_revision=committed_revision,
        correlation_id=correlation_id,
        subject="domain.physical_field",
        patch=patch,
        description="physical field evolution and Q computation",
        metadata={
            "domain": "physical_field",
            "physical_time": float(physical_field.state.physical_time),
            "q_observations_count": len(q_observations),
            "regime_distribution": {
                "coherent": sum(1 for obs in q_observations if obs["regime"] == "coherent"),
                "critical": sum(1 for obs in q_observations if obs["regime"] == "critical"),
                "overdamped": sum(1 for obs in q_observations if obs["regime"] == "overdamped"),
            },
        },
    )


def get_physical_field() -> InformationDensityField | None:
    """Get current physical field state."""
    return _physical_field


def get_propagation_parameters() -> PropagationParameters:
    """Get current propagation parameters."""
    return _propagation_params


def get_relaxation_parameters() -> RelaxationParameters:
    """Get current relaxation parameters."""
    return _relaxation_params


def set_propagation_parameters(params: PropagationParameters) -> None:
    """Set propagation parameters."""
    global _propagation_params
    _propagation_params = params


def set_relaxation_parameters(params: RelaxationParameters) -> None:
    """Set relaxation parameters."""
    global _relaxation_params
    _relaxation_params = params


def get_reaction_parameters() -> NonlinearReactionParameters:
    """Get current nonlinear reaction parameters."""
    return _reaction_params


def set_reaction_parameters(params: NonlinearReactionParameters) -> None:
    """Set nonlinear reaction parameters (replaces set_nonlinear_reaction_parameters)."""
    global _reaction_params
    _reaction_params = params
