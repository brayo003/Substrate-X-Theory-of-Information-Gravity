from __future__ import annotations

import numpy as np
from typing import Tuple, List, Dict, Any
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


def create_physical_grid(
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    nx: int,
    ny: int,
    dz: float = 1.0,
    nz: int = 1,
) -> Tuple[np.ndarray, np.ndarray, float, float, float]:
    """Create physical coordinate grid.
    
    Args:
        x_range: (x_min, x_max) in meters
        y_range: (y_min, y_max) in meters
        nx: Number of grid points in x
        ny: Number of grid points in y
        dz: Physical spacing in z (meters)
        nz: Number of grid points in z
    
    Returns:
        coordinates: (nx*ny*nz, 3) array of physical coordinates
        dx, dy, dz: Physical spacing
    """
    x = np.linspace(x_range[0], x_range[1], nx)
    y = np.linspace(y_range[0], y_range[1], ny)
    z = np.linspace(0.0, dz * (nz - 1), nz)
    
    dx = (x_range[1] - x_range[0]) / (nx - 1) if nx > 1 else 1.0
    dy = (y_range[1] - y_range[0]) / (ny - 1) if ny > 1 else 1.0
    
    # Create meshgrid and flatten
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    coordinates = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    
    return coordinates, dx, dy, dz


def initialize_field_state(
    x_range: Tuple[float, float] = (0.0, 100.0),
    y_range: Tuple[float, float] = (0.0, 100.0),
    nx: int = 50,
    ny: int = 50,
    initial_value: float = 1.0,
    dt: float = 0.1,
) -> FieldState:
    """Initialize field state with physical coordinates."""
    coordinates, dx, dy, dz = create_physical_grid(x_range, y_range, nx, ny)
    
    nz = 1  # Default 2D
    grid_shape = (nx, ny, nz)
    
    # Initialize field with constant value
    field_values = np.full(nx * ny * nz, initial_value)
    field_velocity = np.zeros(nx * ny * nz)
    
    metric = PhysicalMetric()
    
    return FieldState(
        field_values=field_values,
        coordinates=coordinates,
        field_velocity=field_velocity,
        dx=dx,
        dy=dy,
        dz=dz,
        dt=dt,
        physical_time=0.0,
        grid_shape=grid_shape,
        metric=metric,
    )


def evolve_field(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    relaxation_params: RelaxationParameters,
    source_term: np.ndarray | None = None,
) -> InformationDensityField:
    """Evolve field using damped wave equation (telegraph equation).
    
    Governing equation:
    τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S(x,t)
    
    This is a second-order hyperbolic equation that exhibits both
    wave propagation (coherent regime) and diffusion (overdamped regime).
    
    Args:
        field: Current information density field
        propagation_params: Propagation parameters (c)
        relaxation_params: Relaxation parameters (τ)
        source_term: Optional source term S(x,t)
    
    Returns:
        Evolved field at next time step
    """
    state = field.state
    c = propagation_params.c_nominal
    tau = relaxation_params.tau_nominal
    dt = state.dt
    dx, dy, dz = state.dx, state.dy, state.dz
    
    # Reshape field for finite difference operations
    s = state.field_values.reshape(state.grid_shape)
    v = state.field_velocity.reshape(state.grid_shape)
    
    # Compute Laplacian using finite differences
    laplacian = compute_laplacian(s, dx, dy, dz)
    
    # Add source term if provided
    if source_term is not None:
        source = source_term.reshape(state.grid_shape)
    else:
        source = np.zeros_like(s)
    
    # Time integration using explicit scheme
    # From telegraph equation: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + S
    # Discretized: τ (v_new - v)/dt + (s_new - s)/dt = c²τ ∇²s + S
    # Where v = ∂s/∂t, so s_new = s + v_new * dt
    
    # Update velocity: v_new = v + dt * (c² ∇²s - v/τ + S/τ)
    acceleration = (c**2) * laplacian - v / tau + source / tau
    v_new = v + dt * acceleration
    
    # Update field: s_new = s + v_new * dt
    s_new = s + dt * v_new
    
    # Flatten back to 1D
    field_values_new = s_new.ravel()
    field_velocity_new = v_new.ravel()
    
    # Update physical time
    physical_time_new = state.physical_time + dt
    
    # Create new state
    new_state = FieldState(
        field_values=field_values_new,
        coordinates=state.coordinates,
        field_velocity=field_velocity_new,
        dx=dx,
        dy=dy,
        dz=dz,
        dt=dt,
        physical_time=physical_time_new,
        grid_shape=state.grid_shape,
        metric=state.metric,
    )
    
    return InformationDensityField(
        state=new_state,
        information_quantity=field.information_quantity,
        physical_volume=field.physical_volume,
        information_units=field.information_units,
        spatial_units=field.spatial_units,
        density_units=field.density_units,
    )


def compute_laplacian(
    field: np.ndarray,
    dx: float,
    dy: float,
    dz: float,
) -> np.ndarray:
    """Compute Laplacian using finite differences."""
    laplacian = np.zeros_like(field)
    
    # Second derivatives
    if field.shape[0] > 2:
        d2s_dx2 = (field[2:, :, :] - 2*field[1:-1, :, :] + field[:-2, :, :]) / (dx**2)
        laplacian[1:-1, :, :] += d2s_dx2
    
    if field.shape[1] > 2:
        d2s_dy2 = (field[:, 2:, :] - 2*field[:, 1:-1, :] + field[:, :-2, :]) / (dy**2)
        laplacian[:, 1:-1, :] += d2s_dy2
    
    if field.shape[2] > 2:
        d2s_dz2 = (field[:, :, 2:] - 2*field[:, :, 1:-1] + field[:, :, :-2]) / (dz**2)
        laplacian[:, :, 1:-1] += d2s_dz2
    
    return laplacian


def evolve_field_nonlinear(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    relaxation_params: RelaxationParameters,
    reaction_params: NonlinearReactionParameters | None = None,
    source_term: np.ndarray | None = None,
) -> InformationDensityField:
    """Evolve field using the nonlinear reaction-telegraph equation.

    Governing equation:
        τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + r·s + a·s² − b·s³ + S(x,t)

    Equivalent first-order system (state variables s and v = ∂s/∂t):
        ∂s/∂t = v
        ∂v/∂t = [c²∇²s + r·s + a·s² − b·s³ + S − v] / τ

    LINEAR LIMIT: When r = a = b = 0, this function falls through to the same
    numerical result as evolve_field().  Test A in the nonlinear test suite
    verifies this to numerical precision.

    NUMERICAL SCHEME:
    Two-stage explicit Euler (same asymmetric scheme as evolve_field):
        acceleration = (c²·∇²s + r·s + a·s² − b·s³ − v + S) / τ
        v_new = v + dt·acceleration
        s_new = s + dt·v_new

    STABILITY NOTES:
    The nonlinear cubic term b·s³ provides a restoring force for large |s|,
    but it also introduces stiffness.  For large deviations from equilibrium the
    effective linearized damping rate is |3b·s²|, which may require a smaller dt
    than the linear scheme.  The function checks for non-finite values after each
    step and raises ValueError with diagnostics rather than silently returning NaN.

    Parameters for verified bistability (use with default EXP3 grid parameters):
        r = −0.5, a = 2.0, b = 1.0, dt ≤ 0.05
    Equilibria: s=0 (stable), s≈0.293 (unstable separatrix), s≈1.707 (stable).

    Args:
        field:              Current information density field.
        propagation_params: Propagation parameters (c).
        relaxation_params:  Relaxation parameters (τ).
        reaction_params:    Nonlinear reaction parameters (r, a, b).
                            None or all-zero recovers the linear telegraph equation.
        source_term:        Optional external source S(x,t), same shape as field.

    Returns:
        Evolved field at next time step.

    Raises:
        ValueError: If the field produces non-finite values, indicating numerical
                    instability.  Caller should reduce dt or the reaction coefficients.
    """
    if reaction_params is None or reaction_params.is_linear:
        # Exact fall-through to the original linear solver — no recomputation.
        return evolve_field(field, propagation_params, relaxation_params, source_term)

    state = field.state
    c   = propagation_params.c_measured if propagation_params.c_measured > 0 else propagation_params.c_nominal
    tau = relaxation_params.tau_measured if relaxation_params.tau_measured > 0 else relaxation_params.tau_nominal
    r_coef = reaction_params.r
    a_coef = reaction_params.a
    b_coef = reaction_params.b
    dt = state.dt
    dx, dy, dz = state.dx, state.dy, state.dz

    # Reshape field for spatial operations
    s = state.field_values.reshape(state.grid_shape)
    v = state.field_velocity.reshape(state.grid_shape)

    # Spatial term: c²∇²s
    laplacian = compute_laplacian(s, dx, dy, dz)

    # Nonlinear reaction term: r·s + a·s² − b·s³
    reaction = r_coef * s + a_coef * (s ** 2) - b_coef * (s ** 3)

    # Optional source term
    if source_term is not None:
        source = source_term.reshape(state.grid_shape)
    else:
        source = np.zeros_like(s)

    # Update: same asymmetric two-stage Euler as evolve_field
    # ∂v/∂t = (c²∇²s + reaction + S − v) / τ
    acceleration = ((c ** 2) * laplacian + reaction + source - v) / tau
    v_new = v + dt * acceleration
    s_new = s + dt * v_new

    # --- Finite-value protection (explicit, not silent clamping) ---
    if not np.all(np.isfinite(s_new)) or not np.all(np.isfinite(v_new)):
        s_max = float(np.nanmax(np.abs(s_new)))
        v_max = float(np.nanmax(np.abs(v_new)))
        raise ValueError(
            f"evolve_field_nonlinear: non-finite values detected after update. "
            f"|s|_max={s_max:.3e}, |v|_max={v_max:.3e}. "
            f"Parameters: c={c}, tau={tau}, r={r_coef}, a={a_coef}, b={b_coef}, dt={dt}. "
            f"Consider reducing dt or b (the cubic coefficient must dominate a**2/(4*|r|) "
            f"for the equilibria to remain bounded)."
        )

    # Flatten and package new state
    new_state = FieldState(
        field_values=s_new.ravel(),
        coordinates=state.coordinates,
        field_velocity=v_new.ravel(),
        dx=dx, dy=dy, dz=dz,
        dt=dt,
        physical_time=state.physical_time + dt,
        grid_shape=state.grid_shape,
        metric=state.metric,
    )
    return InformationDensityField(
        state=new_state,
        information_quantity=field.information_quantity,
        physical_volume=field.physical_volume,
        information_units=field.information_units,
        spatial_units=field.spatial_units,
        density_units=field.density_units,
    )


def apply_perturbation(
    field: InformationDensityField,
    center: PhysicalCoordinate,
    perturbation_amplitude: float,
    perturbation_width: float,
) -> InformationDensityField:
    """Apply Gaussian perturbation at specified location.
    
    Args:
        field: Current field
        center: Center of perturbation
        amplitude: Perturbation amplitude
        width: Gaussian width (meters)
    
    Returns:
        Field with perturbation applied
    """
    state = field.state
    coordinates = state.coordinates
    
    # Compute Gaussian perturbation
    perturbation = np.zeros_like(state.field_values)
    for i, coord_array in enumerate(coordinates):
        coord = PhysicalCoordinate(coord_array[0], coord_array[1], coord_array[2])
        distance = coord.distance_to(center)
        perturbation[i] = perturbation_amplitude * np.exp(-(distance**2) / (2 * perturbation_width**2))
    
    # Add perturbation to field
    new_field_values = state.field_values + perturbation
    
    new_state = FieldState(
        field_values=new_field_values,
        coordinates=state.coordinates,
        field_velocity=state.field_velocity,
        dx=state.dx,
        dy=state.dy,
        dz=state.dz,
        dt=state.dt,
        physical_time=state.physical_time,
        grid_shape=state.grid_shape,
        metric=state.metric,
    )
    
    return InformationDensityField(
        state=new_state,
        information_quantity=field.information_quantity,
        physical_volume=field.physical_volume,
        information_units=field.information_units,
        spatial_units=field.spatial_units,
        density_units=field.density_units,
    )


def measure_propagation_speed(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    perturbation_center: PhysicalCoordinate,
    perturbation_amplitude: float,
    perturbation_width: float,
    observer_distances: List[float],
    max_time: float = 10.0,
) -> PropagationParameters:
    """Measure propagation speed by tracking perturbation arrival.
    
    Args:
        field: Initial field
        propagation_params: Current propagation parameters
        perturbation_center: Center of perturbation
        perturbation_amplitude: Amplitude of perturbation
        perturbation_width: Width of perturbation
        observer_distances: List of distances to measure (meters)
        max_time: Maximum simulation time (seconds)
    
    Returns:
        Updated propagation parameters with measured c
    """
    # Apply initial perturbation
    field = apply_perturbation(field, perturbation_center, perturbation_amplitude, perturbation_width)
    
    # Track field at observer locations
    observer_positions = [
        PhysicalCoordinate(
            perturbation_center.x + distance,
            perturbation_center.y,
            perturbation_center.z
        )
        for distance in observer_distances
    ]
    
    arrival_times = []
    field_snapshots = []
    
    # Simulate propagation
    current_field = field
    relaxation_params = RelaxationParameters(tau_nominal=1.0)  # Use nominal tau for measurement
    
    for step in range(int(max_time / current_field.state.dt)):
        current_field = evolve_field(current_field, propagation_params, relaxation_params)
        
        # Check for arrival at each observer
        for i, observer_pos in enumerate(observer_positions):
            if i >= len(arrival_times):  # Haven't detected arrival yet
                value = current_field.get_density_at(observer_pos)
                if value > perturbation_amplitude * 0.1:  # 10% threshold
                    arrival_time = current_field.state.physical_time
                    arrival_times.append(arrival_time)
                    field_snapshots.append(value)
    
    # Estimate propagation speed
    if len(arrival_times) >= 2:
        # Linear fit: distance = c * time
        distances = np.array(observer_distances[:len(arrival_times)])
        times = np.array(arrival_times)
        
        # Fit c using least squares
        c_measured = np.sum(distances * times) / np.sum(times**2)
        
        # Estimate uncertainty
        residuals = distances - c_measured * times
        c_uncertainty = np.std(residuals) / np.sqrt(len(times))
    else:
        # Fallback: use nominal value with high uncertainty
        c_measured = propagation_params.c_nominal
        c_uncertainty = c_measured * 0.5  # 50% uncertainty
    
    return PropagationParameters(
        c_nominal=propagation_params.c_nominal,
        c_measured=c_measured,
        c_uncertainty=c_uncertainty,
        c_direction_dependent=propagation_params.c_direction_dependent,
        c_spatially_varying=propagation_params.c_spatially_varying,
    )


def measure_relaxation_time(
    field: InformationDensityField,
    relaxation_params: RelaxationParameters,
    perturbation_center: PhysicalCoordinate,
    perturbation_amplitude: float,
    perturbation_width: float,
    max_time: float = 20.0,
) -> RelaxationParameters:
    """Measure relaxation time by tracking field decay.
    
    Args:
        field: Initial field
        relaxation_params: Current relaxation parameters
        perturbation_center: Center of perturbation
        perturbation_amplitude: Amplitude of perturbation
        perturbation_width: Width of perturbation
        max_time: Maximum simulation time (seconds)
    
    Returns:
        Updated relaxation parameters with measured τ
    """
    # Apply initial perturbation
    field = apply_perturbation(field, perturbation_center, perturbation_amplitude, perturbation_width)
    
    # Track field at perturbation center
    field_values_over_time = []
    times = []
    
    # Simulate relaxation
    current_field = field
    propagation_params = PropagationParameters(c_nominal=1.0)  # Use nominal c for measurement
    
    for step in range(int(max_time / current_field.state.dt)):
        current_field = evolve_field(current_field, propagation_params, relaxation_params)
        
        value = current_field.get_density_at(perturbation_center)
        field_values_over_time.append(value)
        times.append(current_field.state.physical_time)
    
    # Fit exponential decay: A(t) = A0 * exp(-t/τ)
    # Linearize: ln(A) = ln(A0) - t/τ
    # Fit: ln(A) = a + b*t, where b = -1/τ
    
    log_values = np.log(np.array(field_values_over_time) + 1e-10)  # Avoid log(0)
    times_array = np.array(times)
    
    # Linear fit
    coeffs = np.polyfit(times_array, log_values, 1)
    slope = coeffs[0]
    
    if slope < 0:
        tau_measured = -1.0 / slope
    else:
        # Fallback: growth instead of decay
        tau_measured = relaxation_params.tau_nominal
    
    # Estimate uncertainty
    predicted = np.exp(coeffs[1] + slope * times_array)
    residuals = np.array(field_values_over_time) - predicted
    tau_uncertainty = np.std(residuals) / np.sqrt(len(times))
    
    return RelaxationParameters(
        tau_nominal=relaxation_params.tau_nominal,
        tau_measured=tau_measured,
        tau_uncertainty=tau_uncertainty,
        relaxation_law="exponential",
    )


def compute_gradient(
    field: InformationDensityField,
    coordinate: PhysicalCoordinate,
) -> np.ndarray:
    """Compute spatial gradient ∇s at a physical coordinate.
    
    Args:
        field: Information density field
        coordinate: Physical coordinate
    
    Returns:
        Gradient vector [∂s/∂x, ∂s/∂y, ∂s/∂z]
    """
    state = field.state
    s = state.field_values.reshape(state.grid_shape)
    dx, dy, dz = state.dx, state.dy, state.dz
    
    # Find nearest grid indices
    x_idx = int((coordinate.x - state.coordinates[0, 0]) / dx)
    y_idx = int((coordinate.y - state.coordinates[0, 1]) / dy)
    z_idx = int((coordinate.z - state.coordinates[0, 2]) / dz)
    
    # Clamp to valid range (ensure we have neighbors for central difference)
    x_idx = max(1, min(x_idx, state.grid_shape[0] - 2))
    y_idx = max(1, min(y_idx, state.grid_shape[1] - 2))
    z_idx = max(0, min(z_idx, state.grid_shape[2] - 1))
    
    # Compute gradient using central differences
    ds_dx = (s[x_idx + 1, y_idx, z_idx] - s[x_idx - 1, y_idx, z_idx]) / (2 * dx)
    ds_dy = (s[x_idx, y_idx + 1, z_idx] - s[x_idx, y_idx - 1, z_idx]) / (2 * dy)
    
    # Handle z dimension (if 2D, gradient is zero)
    if state.grid_shape[2] > 1:
        if z_idx > 0 and z_idx < state.grid_shape[2] - 1:
            ds_dz = (s[x_idx, y_idx, z_idx + 1] - s[x_idx, y_idx, z_idx - 1]) / (2 * dz)
        else:
            ds_dz = 0.0
    else:
        ds_dz = 0.0
    
    return np.array([ds_dx, ds_dy, ds_dz])


def compute_gradient_magnitude(
    field: InformationDensityField,
    coordinate: PhysicalCoordinate,
) -> float:
    """Compute |∇ln s| at a physical coordinate.
    
    Args:
        field: Information density field
        coordinate: Physical coordinate
    
    Returns:
        Magnitude of logarithmic gradient
    """
    # Ensure field is positive for ln(s)
    field = field.ensure_positivity()
    
    # Get field value at coordinate
    s_value = field.get_density_at(coordinate)
    
    # Compute gradient of s
    gradient_s = compute_gradient(field, coordinate)
    
    # Compute gradient of ln(s): ∇ln(s) = (1/s) ∇s
    gradient_ln_s = gradient_s / s_value
    
    # Contract with metric to get magnitude
    magnitude = field.state.metric.contract(gradient_ln_s)
    
    return float(np.sqrt(magnitude))


def compute_theoretical_q(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    relaxation_params: RelaxationParameters,
    coordinate: PhysicalCoordinate,
) -> QObservation:
    """Compute theoretical Q at a physical coordinate.
    
    DEPRECATED: This quantity has been experimentally falsified as a general
    transport regime classifier. Use compute_spectral_transport_observable() instead.
    
    Q = 4c²τ²|∇ln s|² - 1
    
    This function is retained for backward compatibility and validation comparisons only.
    It should not be used for production transport classification.
    
    Args:
        field: Information density field
        propagation_params: Propagation parameters (c)
        relaxation_params: Relaxation parameters (τ)
        coordinate: Physical coordinate
    
    Returns:
        Q observation with regime classification
    """
    # Use measured values if available, otherwise nominal
    c = propagation_params.c_measured if propagation_params.c_measured > 0 else propagation_params.c_nominal
    tau = relaxation_params.tau_measured if relaxation_params.tau_measured > 0 else relaxation_params.tau_nominal
    
    # Compute gradient magnitude
    gradient_magnitude = compute_gradient_magnitude(field, coordinate)
    
    # Compute Q
    q_value = 4.0 * (c**2) * (tau**2) * (gradient_magnitude**2) - 1.0
    
    # Classify regime
    if q_value > 0:
        regime = "coherent"
    elif q_value < 0:
        regime = "overdamped"
    else:
        regime = "critical"
    
    # Get field value
    s_value = field.get_density_at(coordinate)
    
    return QObservation(
        coordinate=coordinate,
        physical_time=field.state.physical_time,
        s_value=s_value,
        gradient_magnitude=gradient_magnitude,
        c_value=c,
        tau_value=tau,
        q_value=q_value,
        regime=regime,
        metadata={
            "c_measured": propagation_params.c_measured,
            "c_uncertainty": propagation_params.c_uncertainty,
            "tau_measured": relaxation_params.tau_measured,
            "tau_uncertainty": relaxation_params.tau_uncertainty,
        },
    )


def compute_spectral_transport_observable(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    relaxation_params: RelaxationParameters,
    epsilon: float = 0.05,
) -> SpectralTransportObservable:
    """Compute structured spectral transport observable for field-level transport classification.

    MATHEMATICAL BASIS
    ------------------
    For the telegraph equation  τ∂²s/∂t² + ∂s/∂t = c²τ∇²s,
    the modal discriminant for a Fourier mode k is:

        D(k) = 4c²τ²|k|² − 1

    Regimes:
        D(k) > +ε   → propagating (damped oscillation)
        D(k) < −ε   → overdamped  (two real negative roots)
        |D(k)| ≤ ε  → critical boundary (near-repeated root)

    BACKGROUND SUBTRACTION
    ----------------------
    We analyse FLUCTUATIONS δs = s − <s>, not the raw field.
    The uniform mean contributes only to k=0 (DC). Including it in power
    fractions would make an almost-flat field look 100% overdamped because
    the DC component has D(0) = −1 and carries virtually all the raw power.
    We therefore subtract the spatial mean before the FFT and exclude k=0
    from all power calculations.

    AGGREGATE COHERENCE SCORE
    --------------------------
        C_spectral = f_prop − f_over  ∈ [−1, +1]

    Near −1: predominantly overdamped.
    Near  0: mixed / near-critical.
    Near +1: predominantly propagating.

    Args:
        field: Information density field
        propagation_params: Propagation parameters (c)
        relaxation_params:  Relaxation parameters (τ)
        epsilon: Critical-boundary half-width (dimensionless). Modes with
                 |D(k)| ≤ epsilon are classified as critical.  Default 0.05.

    Returns:
        SpectralTransportObservable with complete spectral transport information.
    """
    import numpy as np

    # Use measured values if available, otherwise nominal
    c   = propagation_params.c_measured   if propagation_params.c_measured   > 0 else propagation_params.c_nominal
    tau = relaxation_params.tau_measured  if relaxation_params.tau_measured  > 0 else relaxation_params.tau_nominal

    state      = field.state
    s_values   = state.field_values
    grid_shape = state.grid_shape

    # ------------------------------------------------------------------ #
    # 1. Background subtraction — analyse fluctuation field δs = s − <s> #
    # ------------------------------------------------------------------ #
    s_mean      = float(np.mean(s_values))
    delta_s     = s_values - s_mean          # zero-mean fluctuation field

    # Guard: degenerate (all-uniform) field
    fluctuation_power = float(np.sum(delta_s**2))
    degenerate = fluctuation_power < 1e-30

    # ------------------------------------------------------------------ #
    # 2. FFT of the fluctuation field & physical wavenumbers              #
    # ------------------------------------------------------------------ #
    if len(grid_shape) == 3 and grid_shape[2] == 1:
        # 2-D field stored as (nx, ny, 1)
        ds_2d = delta_s.reshape(grid_shape[0], grid_shape[1])
        ds_k  = np.fft.fft2(ds_2d)
        power_spectrum_2d = np.abs(ds_k)**2

        kx = 2 * np.pi * np.fft.fftfreq(grid_shape[0], d=state.dx)
        ky = 2 * np.pi * np.fft.fftfreq(grid_shape[1], d=state.dy)
        KX, KY = np.meshgrid(kx, ky, indexing='ij')
        k_magnitude_2d = np.sqrt(KX**2 + KY**2)

        # Flatten
        power_spectrum = power_spectrum_2d.ravel()
        k_magnitude    = k_magnitude_2d.ravel()

        domain_size         = max(grid_shape[0] * state.dx, grid_shape[1] * state.dy)
        spectral_resolution = min(state.dx, state.dy)
        num_modes           = grid_shape[0] * grid_shape[1]

    else:
        # 1-D field
        ds_k          = np.fft.fft(delta_s)
        power_spectrum = np.abs(ds_k)**2
        k_values      = 2 * np.pi * np.fft.fftfreq(len(delta_s), d=state.dx)
        k_magnitude   = np.abs(k_values)

        domain_size         = len(delta_s) * state.dx
        spectral_resolution = state.dx
        num_modes           = len(delta_s)

    # ------------------------------------------------------------------ #
    # 3. Exclude DC bin (k=0) from all power calculations                 #
    # ------------------------------------------------------------------ #
    # DC bin is always index 0 in the flattened spectrum after fft/fft2.
    # For 2-D: (kx=0, ky=0) is the [0,0] element, which is ravel index 0.
    ac_mask = np.ones(len(power_spectrum), dtype=bool)
    ac_mask[0] = False                       # exclude DC

    power_ac   = power_spectrum[ac_mask]     # AC (non-DC) power values
    k_ac       = k_magnitude[ac_mask]        # corresponding |k| values

    total_power_ac = float(np.sum(power_ac))

    # ------------------------------------------------------------------ #
    # 4. Modal discriminant D(k) = 4c²τ²|k|² − 1                        #
    # ------------------------------------------------------------------ #
    D_ac = 4.0 * (c**2) * (tau**2) * (k_ac**2) - 1.0

    # ------------------------------------------------------------------ #
    # 5. Find dominant (highest-power AC) mode                            #
    # ------------------------------------------------------------------ #
    if not degenerate and total_power_ac > 0:
        dom_idx    = int(np.argmax(power_ac))
        dominant_k = float(k_ac[dom_idx])
        dominant_D = float(D_ac[dom_idx])
    else:
        dominant_k = 0.0
        dominant_D = -1.0

    if   dominant_D >  epsilon: dominant_regime = "coherent"
    elif dominant_D < -epsilon: dominant_regime = "overdamped"
    else:                       dominant_regime = "critical"

    # ------------------------------------------------------------------ #
    # 6. Power fractions using epsilon-tolerance critical band            #
    # ------------------------------------------------------------------ #
    if not degenerate and total_power_ac > 0:
        prop_mask  = D_ac >  epsilon
        over_mask  = D_ac < -epsilon
        crit_mask  = ~prop_mask & ~over_mask   # |D| ≤ epsilon

        f_prop = float(np.sum(power_ac[prop_mask])) / total_power_ac
        f_over = float(np.sum(power_ac[over_mask])) / total_power_ac
        f_crit = float(np.sum(power_ac[crit_mask])) / total_power_ac

        # Numerical guard: ensure exact sum-to-one
        total_check = f_prop + f_over + f_crit
        if total_check > 0:
            f_prop /= total_check
            f_over /= total_check
            f_crit /= total_check
        else:
            f_prop, f_over, f_crit = 0.0, 1.0, 0.0
    else:
        # Degenerate field — all power is effectively at DC/overdamped
        f_prop, f_over, f_crit = 0.0, 1.0, 0.0

    # ------------------------------------------------------------------ #
    # 7. Aggregate coherence score C_spectral = f_prop − f_over           #
    # ------------------------------------------------------------------ #
    c_spectral = f_prop - f_over   # ∈ [−1, +1]

    # ------------------------------------------------------------------ #
    # 8. Power-weighted discriminant (uses AC power only)                 #
    # ------------------------------------------------------------------ #
    if not degenerate and total_power_ac > 0:
        weighted_D = float(np.sum(power_ac * D_ac)) / total_power_ac
    else:
        weighted_D = -1.0

    # ------------------------------------------------------------------ #
    # 9. Spectral entropy over AC power distribution                      #
    # ------------------------------------------------------------------ #
    if not degenerate and total_power_ac > 0:
        p_k_ac = power_ac / total_power_ac
        p_pos  = p_k_ac[p_k_ac > 0]
        spectral_entropy = float(-np.sum(p_pos * np.log(p_pos)))
    else:
        spectral_entropy = 0.0

    # ------------------------------------------------------------------ #
    # 10. Critical wavenumber  k_c = 1 / (2cτ)                           #
    # ------------------------------------------------------------------ #
    k_critical = 1.0 / (2.0 * c * tau)

    return SpectralTransportObservable(
        physical_time=state.physical_time,
        dominant_k=dominant_k,
        dominant_D=dominant_D,
        dominant_regime=dominant_regime,
        propagating_power_fraction=f_prop,
        overdamped_power_fraction=f_over,
        critical_power_fraction=f_crit,
        weighted_D=weighted_D,
        spectral_entropy=spectral_entropy,
        c_spectral=c_spectral,
        c_nominal=c,
        tau_nominal=tau,
        k_critical=k_critical,
        spectral_resolution=spectral_resolution,
        domain_size=domain_size,
        num_modes=num_modes,
        metadata={
            "c_measured":        propagation_params.c_measured,
            "c_uncertainty":     propagation_params.c_uncertainty,
            "tau_measured":      relaxation_params.tau_measured,
            "tau_uncertainty":   relaxation_params.tau_uncertainty,
            "epsilon":           epsilon,
            "s_mean":            s_mean,
            "total_power_ac":    total_power_ac,
            "degenerate":        degenerate,
        },
    )


def compute_independent_observables(
    field: InformationDensityField,
    coordinate: PhysicalCoordinate,
) -> Dict[str, float]:
    """Compute independent transport observables for validation.
    
    These observables are independent of Q and provide ground truth
    for transport regime classification.
    
    Args:
        field: Information density field
        coordinate: Physical coordinate
    
    Returns:
        Dictionary of independent observables
    """
    state = field.state
    s = field.get_density_at(coordinate)
    gradient = compute_gradient(field, coordinate)
    velocity = field.state.field_velocity.reshape(state.grid_shape)
    
    # Find nearest grid indices
    x_idx = int((coordinate.x - state.coordinates[0, 0]) / state.dx)
    y_idx = int((coordinate.y - state.coordinates[0, 1]) / state.dy)
    z_idx = int((coordinate.z - state.coordinates[0, 2]) / state.dz)
    
    # Clamp to valid range
    x_idx = max(0, min(x_idx, state.grid_shape[0] - 1))
    y_idx = max(0, min(y_idx, state.grid_shape[1] - 1))
    z_idx = max(0, min(z_idx, state.grid_shape[2] - 1))
    
    local_velocity = velocity[x_idx, y_idx, z_idx]
    
    # Compute local observables
    observables = {
        "field_value": float(s),
        "gradient_magnitude": float(np.linalg.norm(gradient)),
        "local_velocity": float(local_velocity),
        "kinetic_energy": 0.5 * float(local_velocity**2),
        "potential_energy": 0.5 * float(s**2),
        "total_energy": 0.5 * float(local_velocity**2 + s**2),
        "spatial_variance": float(np.var(state.field_values)),
        "temporal_derivative": float(local_velocity),  # ∂s/∂t
    }
    
    return observables
