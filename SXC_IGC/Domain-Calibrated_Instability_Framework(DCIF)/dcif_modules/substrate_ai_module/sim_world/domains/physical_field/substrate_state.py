"""
Authoritative Substrate State Interface
========================================

SubstrateState is the single canonical object through which the physical
field substrate communicates its condition to the simulation kernel,
autonomous agents, and planning systems.

It is derived from SpectralTransportObservable but deliberately exposes
only the quantities that are:
  (a) mathematically well-defined,
  (b) bounded and interpretable at agent level,
  (c) relevant to agent capability modulation.

FIELD SEMANTICS
---------------
c_spectral        : C_spectral = f_prop − f_over ∈ [−1, +1]
                    Primary aggregate coherence score.
                    −1 → fully overdamped, +1 → fully propagating.

f_prop            : Fraction of fluctuation power in propagating modes.
f_over            : Fraction of fluctuation power in overdamped modes.
f_crit            : Fraction of fluctuation power near critical boundary.

dominant_D        : Modal discriminant of the highest-power mode.
dominant_k        : Wavenumber of the highest-power mode (rad/m).
dominant_regime   : "coherent" | "overdamped" | "critical"

spectral_entropy  : Shannon entropy of the AC power distribution (nats).
                    Low → power concentrated in few modes (structured).
                    High → power spread across many modes (noisy).

decay_timescale   : T_decay = 2τ   (seconds).
                    How long modal amplitudes persist.

tau               : Relaxation time parameter (seconds).
propagation_speed : c (m/s).

physical_time     : Simulation time at which this state was computed.

AGENT CAPABILITY MODULATION
-----------------------------
The recommended pattern is:

    coordination_capacity  = 0.5 * (1 + state.c_spectral)   ∈ [0, 1]
    memory_persistence     = min(1.0, state.decay_timescale / T_ref)
    planning_horizon       = base_horizon * (1 + 0.5 * state.c_spectral)

Agents should still decide based on their goals.  The substrate modifies
the *quality* of information available to them (how well coordinated
signals can propagate) not the *content* of their goals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

try:
    from .physical_field_models import SpectralTransportObservable
except ImportError:
    SpectralTransportObservable = None  # type: ignore


@dataclass(frozen=True, slots=True)
class SubstrateState:
    """Authoritative substrate state exposed to kernel and agents.

    Derived from SpectralTransportObservable.  All fields are bounded and
    interpretable.  No raw FFT output or unbounded discriminant averages
    are exposed at this level.
    """

    # -----------------------------------------------------------------
    # Primary aggregate coherence score
    # -----------------------------------------------------------------
    c_spectral: float        # C_spectral = f_prop − f_over  ∈ [−1, +1]

    # -----------------------------------------------------------------
    # Spectral power fractions (sum to 1.0)
    # -----------------------------------------------------------------
    f_prop: float            # Propagating power fraction   ∈ [0, 1]
    f_over: float            # Overdamped power fraction    ∈ [0, 1]
    f_crit: float            # Critical power fraction      ∈ [0, 1]

    # -----------------------------------------------------------------
    # Dominant mode
    # -----------------------------------------------------------------
    dominant_D: float        # Modal discriminant of dominant mode
    dominant_k: float        # Wavenumber of dominant mode (rad/m)
    dominant_regime: str     # "coherent" | "overdamped" | "critical"

    # -----------------------------------------------------------------
    # Spectral structure
    # -----------------------------------------------------------------
    spectral_entropy: float  # H = −Σ p log p  (nats)
    weighted_D: float        # Power-weighted discriminant (unbounded; diagnostic only)

    # -----------------------------------------------------------------
    # Temporal characteristics
    # -----------------------------------------------------------------
    tau: float               # Relaxation time (s)
    decay_timescale: float   # T_decay = 2τ  (s)
    propagation_speed: float # c (m/s)
    k_critical: float        # k_c = 1/(2cτ)  (rad/m)

    # -----------------------------------------------------------------
    # Context
    # -----------------------------------------------------------------
    physical_time: float     # Simulation time (s)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def coordination_capacity(self) -> float:
        """Normalised coordination capacity ∈ [0, 1].

        Derived from c_spectral.  Near 1 when substrate is fully propagating,
        near 0 when fully overdamped.  Can be used to scale the probability
        or effectiveness of coordinated multi-agent actions.
        """
        return 0.5 * (1.0 + self.c_spectral)

    @property
    def memory_persistence_factor(self, t_reference: float = 6.0) -> float:
        """Relative memory persistence compared to a reference timescale.

        Capped at 1.0.  t_reference is the 'baseline' decay time (default 6 s).
        """
        return min(1.0, self.decay_timescale / t_reference)

    @property
    def is_coherent(self) -> bool:
        return self.dominant_regime == "coherent"

    @property
    def is_overdamped(self) -> bool:
        return self.dominant_regime == "overdamped"

    @property
    def is_critical(self) -> bool:
        return self.dominant_regime == "critical"

    @property
    def has_mixed_regime(self) -> bool:
        """True if both propagating and overdamped power are significant (>10%)."""
        return self.f_prop > 0.1 and self.f_over > 0.1

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_spectral_observable(
        cls,
        obs: "SpectralTransportObservable",
    ) -> "SubstrateState":
        """Construct SubstrateState from a SpectralTransportObservable."""
        tau = obs.tau_nominal
        return cls(
            c_spectral=obs.c_spectral,
            f_prop=obs.propagating_power_fraction,
            f_over=obs.overdamped_power_fraction,
            f_crit=obs.critical_power_fraction,
            dominant_D=obs.dominant_D,
            dominant_k=obs.dominant_k,
            dominant_regime=obs.dominant_regime,
            spectral_entropy=obs.spectral_entropy,
            weighted_D=obs.weighted_D,
            tau=tau,
            decay_timescale=2.0 * tau,
            propagation_speed=obs.c_nominal,
            k_critical=obs.k_critical,
            physical_time=obs.physical_time,
            metadata=dict(obs.metadata),
        )

    @classmethod
    def overdamped_default(cls) -> "SubstrateState":
        """Return a neutral overdamped state used when no field is initialised."""
        return cls(
            c_spectral=-1.0,
            f_prop=0.0, f_over=1.0, f_crit=0.0,
            dominant_D=-1.0, dominant_k=0.0, dominant_regime="overdamped",
            spectral_entropy=0.0, weighted_D=-1.0,
            tau=1.0, decay_timescale=2.0,
            propagation_speed=1.0, k_critical=0.5,
            physical_time=0.0,
        )

    def to_agent_context(self) -> dict[str, Any]:
        """Return a flat dict suitable for injection into an agent prompt or context."""
        return {
            "substrate_c_spectral":       round(self.c_spectral, 4),
            "substrate_f_prop":           round(self.f_prop, 4),
            "substrate_f_over":           round(self.f_over, 4),
            "substrate_f_crit":           round(self.f_crit, 4),
            "substrate_dominant_regime":  self.dominant_regime,
            "substrate_dominant_D":       round(self.dominant_D, 4),
            "substrate_spectral_entropy": round(self.spectral_entropy, 4),
            "substrate_decay_timescale":  round(self.decay_timescale, 4),
            "substrate_coordination":     round(self.coordination_capacity, 4),
            "substrate_has_mixed":        self.has_mixed_regime,
        }

    def __repr__(self) -> str:
        return (
            f"SubstrateState(C={self.c_spectral:+.3f}, "
            f"f_prop={self.f_prop:.3f}, f_over={self.f_over:.3f}, "
            f"regime={self.dominant_regime}, τ={self.tau:.2f}, "
            f"T_decay={self.decay_timescale:.2f})"
        )
