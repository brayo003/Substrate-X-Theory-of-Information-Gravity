from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple
import numpy as np

try:
    from ...core.contracts import freeze_value
except ImportError:
    # For standalone use, we'll implement freeze_value locally
    def freeze_value(obj):
        """Freeze a value to make it hashable."""
        if isinstance(obj, dict):
            return tuple(sorted((k, freeze_value(v)) for k, v in obj.items()))
        elif isinstance(obj, (list, tuple)):
            return tuple(freeze_value(item) for item in obj)
        elif isinstance(obj, (set, frozenset)):
            return frozenset(freeze_value(item) for item in obj)
        else:
            return obj


@dataclass(frozen=False)
class PhysicalCoordinate:
    """Physical spatial coordinate with metric structure."""
    x: float  # Physical x coordinate (meters)
    y: float  # Physical y coordinate (meters)
    z: float = 0.0  # Physical z coordinate (meters, default 2D)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def distance_to(self, other: 'PhysicalCoordinate') -> float:
        """Euclidean distance to another coordinate."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)


@dataclass(frozen=True, slots=True)
class PhysicalMetric:
    """Metric structure for physical space."""
    # Euclidean metric (identity matrix)
    g_ij: np.ndarray = field(default_factory=lambda: np.eye(3))
    g_inv: np.ndarray = field(default_factory=lambda: np.eye(3))
    
    def __post_init__(self):
        # Ensure metric is properly frozen
        object.__setattr__(self, 'g_ij', self.g_ij.copy())
        object.__setattr__(self, 'g_inv', self.g_inv.copy())
    
    def contract(self, gradient: np.ndarray) -> float:
        """Contract gradient with inverse metric: |∇f|² = g^{ij} ∂_i f ∂_j f"""
        return float(gradient.T @ self.g_inv @ gradient)


@dataclass(frozen=True, slots=True)
class PropagationParameters:
    """Parameters governing field propagation."""
    c_nominal: float = 1.0  # Nominal propagation speed (m/s)
    c_measured: float = 0.0  # Measured propagation speed (m/s)
    c_uncertainty: float = 0.0  # Measurement uncertainty
    c_direction_dependent: bool = False  # Whether c varies with direction
    c_spatially_varying: bool = False  # Whether c varies spatially
    
    def __post_init__(self):
        object.__setattr__(self, 'c_nominal', float(self.c_nominal))
        object.__setattr__(self, 'c_measured', float(self.c_measured))
        object.__setattr__(self, 'c_uncertainty', float(self.c_uncertainty))


@dataclass(frozen=True, slots=True)
class RelaxationParameters:
    """Parameters governing field relaxation."""
    tau_nominal: float = 1.0  # Nominal relaxation time (s)
    tau_measured: float = 0.0  # Measured relaxation time (s)
    tau_uncertainty: float = 0.0  # Measurement uncertainty
    relaxation_law: str = "exponential"  # exponential, power_law, etc.
    
    def __post_init__(self):
        object.__setattr__(self, 'tau_nominal', float(self.tau_nominal))
        object.__setattr__(self, 'tau_measured', float(self.tau_measured))
        object.__setattr__(self, 'tau_uncertainty', float(self.tau_uncertainty))
        object.__setattr__(self, 'relaxation_law', str(self.relaxation_law))


@dataclass(frozen=True, slots=True)
class NonlinearReactionParameters:
    """Parameters for the nonlinear reaction terms in the reaction-telegraph equation.

    The full equation is:
        τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + r·s + a·s² − b·s³

    where the three reaction coefficients govern:
        r  — linear growth/decay rate (s⁻¹).  Positive → growth, negative → decay.
        a  — quadratic (autocatalytic) coefficient (1/(density·s)).  Must be ≥ 0.
        b  — cubic saturation coefficient (1/(density²·s)).  Must be > 0 to ensure
               global boundedness.

    Units:
        If s has units [ρ] (e.g. bits/m³) and t has units [s], then for each
        term in ∂s/∂t = …:
            r·s          → [ρ/s]   requires r in [s⁻¹]
            a·s²         → [ρ/s]   requires a in [1/(ρ·s)]
            b·s³         → [ρ/s]   requires b in [1/(ρ²·s)]

    Setting r = a = b = 0 recovers the original linear telegraph equation exactly.

    Stationary homogeneous equilibria (∇²s = 0, ṡ = 0) satisfy:
        r·s + a·s² − b·s³ = 0
        s = 0  (always)
        s± = (a ± √(a² + 4·b·r)) / (2·b)   when discriminant ≥ 0

    Bistability (two nonzero stable equilibria) requires a² + 4·b·r > 0 and r > 0
    so that s+ and s− are real and positive.  A sufficient bistable parameter set:
        r > 0, a > 0, b > 0  with  a² + 4·b·r > 0  (always true when r,a > 0)
    giving s+ = (a + √(a²+4br))/(2b) > 0 and s− = (a − √(a²+4br))/(2b).
    s− > 0 requires a > √(a²+4br), i.e. a² > a²+4br, i.e. r < 0 — so for r > 0
    s− < 0 and only one positive nonzero equilibrium s+ exists.

    For genuine bistability between s=0 and s+:
        Use r < 0 (the zero state is locally stable) with a large enough to create
        a fold (subcritical bifurcation).  Specifically:
        a² + 4·b·r > 0  with  r < 0  →  a > 2√(−b·r)
        Then s+ > 0 and s− ∈ (0, s+) exist; the zero state and s+ are stable,
        s− is unstable (the separatrix).

    Example bistable parameters documented and tested:
        r = −0.5, a = 2.0, b = 1.0
        Discriminant = 4 + 4×1×(−0.5) = 2 > 0  ✓
        s+ = (2 + √2) / 2 ≈ 1.707
        s− = (2 − √2) / 2 ≈ 0.293  (unstable separatrix)
    """
    r: float = 0.0   # linear reaction coefficient  (s⁻¹)
    a: float = 0.0   # quadratic coefficient  (1/(density·s))
    b: float = 0.0   # cubic saturation coefficient  (1/(density²·s))

    def __post_init__(self) -> None:
        object.__setattr__(self, 'r', float(self.r))
        object.__setattr__(self, 'a', float(self.a))
        object.__setattr__(self, 'b', float(self.b))
        if self.b < 0.0:
            raise ValueError(
                f"NonlinearReactionParameters: b must be ≥ 0 (got {self.b}). "
                "Negative b removes the cubic saturation and allows unbounded growth."
            )

    @property
    def is_linear(self) -> bool:
        """True when all reaction coefficients are zero (linear limit)."""
        return self.r == 0.0 and self.a == 0.0 and self.b == 0.0

    def homogeneous_equilibria(self) -> list[float]:
        """Compute real homogeneous equilibria: roots of r·s + a·s² − b·s³ = 0.

        Returns a sorted list of real equilibrium values (always includes 0.0).
        """
        roots = [0.0]
        if self.b > 0.0:
            # Factor out s: remaining equation is  −b·s² + a·s + r = 0
            #   or equivalently b·s² − a·s − r = 0
            disc = self.a ** 2 + 4.0 * self.b * self.r
            if disc >= 0.0:
                sqrt_disc = float(disc ** 0.5)
                s_plus  = (self.a + sqrt_disc) / (2.0 * self.b)
                s_minus = (self.a - sqrt_disc) / (2.0 * self.b)
                for s in (s_plus, s_minus):
                    if abs(s) > 1e-12:
                        roots.append(float(s))
        return sorted(set(round(x, 12) for x in roots))

    def linearized_growth_rate(self, s_star: float) -> float:
        """Compute the linearized reaction rate f'(s*) = r + 2a·s* − 3b·s*² .

        A linearized rate < 0 indicates local stability of the equilibrium s*.
        """
        return self.r + 2.0 * self.a * s_star - 3.0 * self.b * (s_star ** 2)


@dataclass(frozen=True, slots=True)
class FieldState:
    """Complete state of the information density field."""
    # Field values on physical grid
    field_values: np.ndarray  # s(x,t) values
    # Physical coordinates for each grid point
    coordinates: np.ndarray  # Shape (N, 3) array of PhysicalCoordinates
    # Field velocity (for second-order dynamics)
    field_velocity: np.ndarray  # ∂s/∂t values
    # Physical parameters
    dx: float  # Physical spacing in x (meters)
    dy: float  # Physical spacing in y (meters)
    dz: float  # Physical spacing in z (meters)
    dt: float  # Physical time step (seconds)
    # Metadata
    physical_time: float  # Physical time (seconds)
    grid_shape: Tuple[int, int, int]  # Grid dimensions
    metric: PhysicalMetric = field(default_factory=PhysicalMetric)
    
    def __post_init__(self):
        # Ensure arrays are properly frozen
        object.__setattr__(self, 'field_values', self.field_values.copy())
        object.__setattr__(self, 'coordinates', self.coordinates.copy())
        object.__setattr__(self, 'field_velocity', self.field_velocity.copy())
        object.__setattr__(self, 'dx', float(self.dx))
        object.__setattr__(self, 'dy', float(self.dy))
        object.__setattr__(self, 'dz', float(self.dz))
        object.__setattr__(self, 'dt', float(self.dt))
        object.__setattr__(self, 'physical_time', float(self.physical_time))
        object.__setattr__(self, 'grid_shape', tuple(self.grid_shape))


@dataclass(frozen=True, slots=True)
class InformationDensityField:
    """Information density field s(x,t) over physical space."""
    state: FieldState
    # Information content (numerator for density calculation)
    information_quantity: float  # Total information (bits or info units)
    # Physical volume (denominator for density calculation)
    physical_volume: float  # Cubic meters
    # Units
    information_units: str = "bits"  # Units of information
    spatial_units: str = "m"  # Units of spatial coordinates
    density_units: str = "bits/m³"  # Units of information density
    
    def __post_init__(self):
        object.__setattr__(self, 'information_quantity', float(self.information_quantity))
        object.__setattr__(self, 'physical_volume', float(self.physical_volume))
        object.__setattr__(self, 'information_units', str(self.information_units))
        object.__setattr__(self, 'spatial_units', str(self.spatial_units))
        object.__setattr__(self, 'density_units', str(self.density_units))
    
    def get_density_at(self, coordinate: PhysicalCoordinate) -> float:
        """Get information density at a physical coordinate."""
        # Find nearest grid point using direct coordinate calculation
        coords = self.state.coordinates
        distances = np.sqrt(
            (coords[:, 0] - coordinate.x)**2 + 
            (coords[:, 1] - coordinate.y)**2 + 
            (coords[:, 2] - coordinate.z)**2
        )
        nearest_idx = np.argmin(distances)
        return float(self.state.field_values[nearest_idx])
    
    def ensure_positivity(self, epsilon: float = 1e-10) -> 'InformationDensityField':
        """Ensure field values are positive for ln(s) calculation."""
        positive_values = np.maximum(self.state.field_values, epsilon)
        new_state = FieldState(
            field_values=positive_values,
            coordinates=self.state.coordinates,
            field_velocity=self.state.field_velocity,
            dx=self.state.dx,
            dy=self.state.dy,
            dz=self.state.dz,
            dt=self.state.dt,
            physical_time=self.state.physical_time,
            grid_shape=self.state.grid_shape,
            metric=self.state.metric,
        )
        return InformationDensityField(
            state=new_state,
            information_quantity=self.information_quantity,
            physical_volume=self.physical_volume,
            information_units=self.information_units,
            spatial_units=self.spatial_units,
            density_units=self.density_units,
        )


@dataclass(frozen=True, slots=True)
class QObservation:
    """Single observation of theoretical Q at a physical location.
    
    DEPRECATED: This quantity has been experimentally falsified as a general
    transport regime classifier. Use SpectralTransportObservable instead.
    """
    coordinate: PhysicalCoordinate
    physical_time: float
    s_value: float  # Information density
    gradient_magnitude: float  # |∇ln s|
    c_value: float  # Propagation speed
    tau_value: float  # Relaxation time
    q_value: float  # Theoretical Q
    regime: str  # "coherent", "critical", "overdamped"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        object.__setattr__(self, 'physical_time', float(self.physical_time))
        object.__setattr__(self, 's_value', float(self.s_value))
        object.__setattr__(self, 'gradient_magnitude', float(self.gradient_magnitude))
        object.__setattr__(self, 'c_value', float(self.c_value))
        object.__setattr__(self, 'tau_value', float(self.tau_value))
        object.__setattr__(self, 'q_value', float(self.q_value))
        object.__setattr__(self, 'regime', str(self.regime))
        object.__setattr__(self, 'metadata', freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class SpectralTransportObservable:
    """Structured spectral transport observable for field-level transport classification.
    
    This observable provides a mathematically defensible representation of transport
    regime based on the telegraph equation's spectral analysis. Unlike the falsified
    local scalar Q, this structured observable correctly handles multimode fields.
    
    FUNDAMENTAL QUANTITY:
        D(k) = 4c²τ²|k|² - 1  (modal telegraph discriminant)
    
    DERIVED QUANTITIES:
        All spectral quantities are derived from the modal discriminant and field spectrum.
    """
    physical_time: float  # Time of observation (seconds)
    
    # Dominant mode information
    dominant_k: float  # Dominant wavenumber magnitude (rad/m)
    dominant_D: float  # Dominant discriminant D = 4c²τ²k² - 1 (dimensionless)
    dominant_regime: str  # Regime of dominant mode: "coherent" | "overdamped" | "critical"
    
    # Spectral power distribution
    propagating_power_fraction: float  # Fraction of energy in propagating modes (0-1)
    overdamped_power_fraction: float  # Fraction of energy in overdamped modes (0-1)
    critical_power_fraction: float  # Fraction of energy at critical boundary (0-1)
    
    # Aggregate metrics
    weighted_D: float  # Power-weighted discriminant (dimensionless)
    spectral_entropy: float  # Spectral entropy H = -Σ p(k) log p(k) (nats)
    # Bounded aggregate coherence score: C_spectral = f_prop - f_over ∈ [-1, +1]
    # Near -1: predominantly overdamped; near 0: mixed; near +1: predominantly propagating.
    c_spectral: float = 0.0

    # Physical parameters
    c_nominal: float = 1.0  # Nominal propagation speed (m/s)
    tau_nominal: float = 1.0  # Nominal relaxation time (s)
    k_critical: float = 0.5  # Critical wavenumber k_c = 1/(2cτ) (rad/m)
    
    # Analysis metadata
    spectral_resolution: float = 1.0  # Spatial resolution of analysis (m)
    domain_size: float = 100.0  # Physical domain size (m)
    num_modes: int = 0  # Number of spectral modes analyzed
    metadata: Mapping[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and freeze all fields."""
        object.__setattr__(self, 'physical_time', float(self.physical_time))
        object.__setattr__(self, 'dominant_k', float(self.dominant_k))
        object.__setattr__(self, 'dominant_D', float(self.dominant_D))
        object.__setattr__(self, 'dominant_regime', str(self.dominant_regime))
        object.__setattr__(self, 'propagating_power_fraction', float(self.propagating_power_fraction))
        object.__setattr__(self, 'overdamped_power_fraction', float(self.overdamped_power_fraction))
        object.__setattr__(self, 'critical_power_fraction', float(self.critical_power_fraction))
        object.__setattr__(self, 'weighted_D', float(self.weighted_D))
        object.__setattr__(self, 'spectral_entropy', float(self.spectral_entropy))
        object.__setattr__(self, 'c_spectral', float(self.c_spectral))
        object.__setattr__(self, 'c_nominal', float(self.c_nominal))
        object.__setattr__(self, 'tau_nominal', float(self.tau_nominal))
        object.__setattr__(self, 'k_critical', float(self.k_critical))
        object.__setattr__(self, 'spectral_resolution', float(self.spectral_resolution))
        object.__setattr__(self, 'domain_size', float(self.domain_size))
        object.__setattr__(self, 'num_modes', int(self.num_modes))
        object.__setattr__(self, 'metadata', freeze_value(dict(self.metadata)))
        
        # Validate power fractions sum to 1.0 (within numerical tolerance)
        total_power = (self.propagating_power_fraction + 
                      self.overdamped_power_fraction + 
                      self.critical_power_fraction)
        if abs(total_power - 1.0) > 1e-6:
            raise ValueError(f"Power fractions must sum to 1.0, got {total_power}")
        
        # Validate fractions are in [0, 1]
        for name, value in [
            ("propagating_power_fraction", self.propagating_power_fraction),
            ("overdamped_power_fraction", self.overdamped_power_fraction),
            ("critical_power_fraction", self.critical_power_fraction),
        ]:
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {value}")
        
        # Validate regime string
        if self.dominant_regime not in ["coherent", "overdamped", "critical"]:
            raise ValueError(f"dominant_regime must be 'coherent', 'overdamped', or 'critical', got {self.dominant_regime}")
    
    def is_single_mode(self, entropy_threshold: float = 0.5) -> bool:
        """Determine if field is effectively single-mode based on spectral entropy.
        
        Args:
            entropy_threshold: Entropy threshold below which field is considered single-mode
        
        Returns:
            True if field is single-mode, False if multimode
        """
        return self.spectral_entropy < entropy_threshold
    
    def is_regime_coherent(self) -> bool:
        """Determine if dominant mode is in coherent regime."""
        return self.dominant_regime == "coherent"
    
    def is_regime_overdamped(self) -> bool:
        """Determine if dominant mode is in overdamped regime."""
        return self.dominant_regime == "overdamped"
    
    def is_regime_critical(self) -> bool:
        """Determine if dominant mode is at critical boundary."""
        return self.dominant_regime == "critical"
    
    def has_regime_coexistence(self, threshold: float = 0.3) -> bool:
        """Determine if field has significant coexistence of multiple regimes.
        
        Args:
            threshold: Minimum power fraction for regime to be considered significant
        
        Returns:
            True if multiple regimes have significant power, False otherwise
        """
        significant_regimes = sum([
            self.propagating_power_fraction > threshold,
            self.overdamped_power_fraction > threshold,
            self.critical_power_fraction > threshold,
        ])
        return significant_regimes >= 2
