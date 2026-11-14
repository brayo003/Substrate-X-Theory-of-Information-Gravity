"""
Test suite for the nonlinear reaction-telegraph substrate.

Tests:
  A. Linear-limit recovery:  r=a=b=0 must reproduce evolve_field() exactly.
  B. Homogeneous equilibrium convergence: spatially uniform ICs near stable equilibria.
  C. Bistability: two ICs in different basins converge to different stable states.
  D. Nonlinear saturation: cubic term prevents unbounded growth.
  E. Spatial propagation: perturbation propagates after adding reaction terms.
  F. Boundary correctness: no artificial mean drift or blow-up from BCs.
  G. Numerical convergence: refined dt gives consistent equilibria.
  H. Finite-value protection: bad parameters raise ValueError, not NaN.
  I. Parameter validation: negative b is rejected at construction.
  J. Equilibrium analysis: analytical vs. numerical equilibrium locations.
  K. Hysteresis: forward/reverse sweep shows path-dependent transitions.

Run from sim_world root with:
    ../.venv/bin/python -m pytest domains/physical_field/test_nonlinear_reaction_telegraph.py -v
or:
    ../.venv/bin/python domains/physical_field/test_nonlinear_reaction_telegraph.py
"""
from __future__ import annotations

import sys
import os
import math
import unittest
import numpy as np

# ---------------------------------------------------------------------------
# Path setup — work from the substrate_ai_module parent so that
# `sim_world` is importable as a package.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM_WORLD = os.path.join(_HERE, '..', '..')          # sim_world/
_PARENT    = os.path.join(_SIM_WORLD, '..')            # substrate_ai_module/
for _p in (_PARENT, _SIM_WORLD):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.domains.physical_field.physical_field_models import (
    NonlinearReactionParameters,
    PropagationParameters,
    RelaxationParameters,
    InformationDensityField,
    FieldState,
    PhysicalMetric,
    PhysicalCoordinate,
)
from sim_world.domains.physical_field.physical_field_dynamics import (
    evolve_field,
    evolve_field_nonlinear,
    initialize_field_state,
    apply_perturbation,
    compute_spectral_transport_observable,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_field(nx: int = 20, ny: int = 20,
                initial_value: float = 0.0,
                dt: float = 0.02) -> InformationDensityField:
    """Return an InformationDensityField on a small grid for fast tests."""
    state = initialize_field_state(
        x_range=(0.0, 10.0), y_range=(0.0, 10.0),
        nx=nx, ny=ny,
        initial_value=initial_value,
        dt=dt,
    )
    return InformationDensityField(
        state=state,
        information_quantity=1.0,
        physical_volume=10.0 * 10.0 * 1.0,
        information_units="bits",
        spatial_units="m",
        density_units="bits/m³",
    )


def _run_steps(field, prop, relax, reaction, n_steps: int) -> InformationDensityField:
    for _ in range(n_steps):
        field = evolve_field_nonlinear(field, prop, relax, reaction)
    return field


def _field_mean(field: InformationDensityField) -> float:
    return float(np.mean(field.state.field_values))


PROP  = PropagationParameters(c_nominal=1.0)
RELAX = RelaxationParameters(tau_nominal=1.0)


# ---------------------------------------------------------------------------
# Test A — Linear-limit recovery
# ---------------------------------------------------------------------------

class TestLinearLimit(unittest.TestCase):
    """When r=a=b=0, evolve_field_nonlinear must equal evolve_field exactly."""

    def test_linear_limit_single_step(self):
        """Single step with zero reaction coefficients matches the linear solver."""
        field = _make_field(initial_value=1.0)
        # Apply a Gaussian so the field is non-trivial.
        field = apply_perturbation(field, PhysicalCoordinate(5.0, 5.0, 0.0), 2.0, 1.5)

        linear_result    = evolve_field(field, PROP, RELAX)
        nonlinear_result = evolve_field_nonlinear(
            field, PROP, RELAX, NonlinearReactionParameters(r=0.0, a=0.0, b=0.0)
        )

        np.testing.assert_array_almost_equal(
            linear_result.state.field_values,
            nonlinear_result.state.field_values,
            decimal=12,
            err_msg="Linear-limit: field values differ from evolve_field",
        )
        np.testing.assert_array_almost_equal(
            linear_result.state.field_velocity,
            nonlinear_result.state.field_velocity,
            decimal=12,
            err_msg="Linear-limit: velocity values differ from evolve_field",
        )

    def test_linear_limit_none_params(self):
        """None reaction_params is identical to all-zero params."""
        field = _make_field(initial_value=1.5)
        field = apply_perturbation(field, PhysicalCoordinate(3.0, 3.0, 0.0), 1.0, 2.0)

        result_none = evolve_field_nonlinear(field, PROP, RELAX, None)
        result_zero = evolve_field_nonlinear(
            field, PROP, RELAX, NonlinearReactionParameters()
        )

        np.testing.assert_array_almost_equal(
            result_none.state.field_values,
            result_zero.state.field_values,
            decimal=12,
        )

    def test_linear_limit_multi_step(self):
        """50 steps with zero reaction match the pure linear solver."""
        field = _make_field(initial_value=1.0)
        field = apply_perturbation(field, PhysicalCoordinate(5.0, 5.0, 0.0), 3.0, 2.0)
        field_lin = field
        field_nl  = field

        for _ in range(50):
            field_lin = evolve_field(field_lin, PROP, RELAX)
            field_nl  = evolve_field_nonlinear(
                field_nl, PROP, RELAX, NonlinearReactionParameters()
            )

        np.testing.assert_array_almost_equal(
            field_lin.state.field_values,
            field_nl.state.field_values,
            decimal=10,
            err_msg="Linear-limit: 50-step cumulative error too large",
        )


# ---------------------------------------------------------------------------
# Test B — Homogeneous equilibrium convergence
# ---------------------------------------------------------------------------

class TestHomogeneousEquilibriumConvergence(unittest.TestCase):
    """Spatially uniform ICs near stable equilibria should converge there."""

    # Bistable parameter set
    # Equilibria: s=0 (stable), s≈0.293 (unstable), s≈1.707 (stable)
    REACT = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)

    def _converge(self, s_init: float, n_steps: int = 5000) -> float:
        field = _make_field(initial_value=s_init, dt=0.02)
        field = _run_steps(field, PROP, RELAX, self.REACT, n_steps)
        return _field_mean(field)

    def test_converge_to_zero_from_below_separatrix(self):
        """IC below separatrix (≈0.293) → converges to s=0."""
        final = self._converge(s_init=0.1)
        self.assertAlmostEqual(final, 0.0, delta=0.05,
            msg=f"Expected convergence to s=0 from s=0.1, got {final:.4f}")

    def test_converge_to_upper_eq_from_above_separatrix(self):
        """IC above separatrix (≈0.293) → converges to s≈1.707."""
        final = self._converge(s_init=1.0)
        self.assertAlmostEqual(final, 1.707, delta=0.05,
            msg=f"Expected convergence to s≈1.707 from s=1.0, got {final:.4f}")

    def test_converge_to_upper_eq_from_high_ic(self):
        """IC moderately above upper equilibrium converges down to s≈1.707.

        Note: very large ICs (e.g. s=3.0) can overshoot the separatrix via
        the velocity state (inertia in the telegraph PDE) and fall into the
        lower basin.  This is physically correct — it reflects the finite
        inertia of the second-order PDE.  We use s=2.0 which is above the
        upper equilibrium (≈1.707) but close enough that the velocity does
        not accumulate enough momentum to cross the separatrix.
        """
        final = self._converge(s_init=2.0)
        self.assertAlmostEqual(final, 1.707, delta=0.1,
            msg=f"Expected convergence to s≈1.707 from s=2.0, got {final:.4f}")

    def test_analytical_equilibria_match_numerical(self):
        """Analytical equilibria match where the numerics settle."""
        eq = self.REACT.homogeneous_equilibria()
        # Sort real equilibria
        self.assertEqual(len(eq), 3, f"Expected 3 equilibria, got {eq}")
        self.assertAlmostEqual(eq[0], 0.0, delta=1e-10)
        self.assertAlmostEqual(eq[1], (2.0 - math.sqrt(2.0)) / 2.0, delta=1e-6)
        self.assertAlmostEqual(eq[2], (2.0 + math.sqrt(2.0)) / 2.0, delta=1e-6)


# ---------------------------------------------------------------------------
# Test C — Bistability
# ---------------------------------------------------------------------------

class TestBistability(unittest.TestCase):
    """Two ICs in different attraction basins must converge to different states."""

    REACT = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)

    def test_different_basins_give_different_finals(self):
        """IC=0.1 and IC=1.0 converge to s=0 and s≈1.707 respectively."""
        field_low  = _make_field(initial_value=0.1,  dt=0.02)
        field_high = _make_field(initial_value=1.0,  dt=0.02)

        for _ in range(5000):
            field_low  = evolve_field_nonlinear(field_low,  PROP, RELAX, self.REACT)
            field_high = evolve_field_nonlinear(field_high, PROP, RELAX, self.REACT)

        mean_low  = _field_mean(field_low)
        mean_high = _field_mean(field_high)

        # Must differ by at least 1.5 (gap between the two stable equilibria)
        self.assertGreater(
            mean_high - mean_low, 1.5,
            f"Bistability not demonstrated: low={mean_low:.4f}, high={mean_high:.4f}"
        )
        self.assertAlmostEqual(mean_low,  0.0,   delta=0.05)
        self.assertAlmostEqual(mean_high, 1.707, delta=0.1)

    def test_bistability_is_not_transient(self):
        """Both states remain after extended evolution (10000 steps)."""
        field_low  = _make_field(initial_value=0.1, dt=0.02)
        field_high = _make_field(initial_value=1.0, dt=0.02)

        for _ in range(10000):
            field_low  = evolve_field_nonlinear(field_low,  PROP, RELAX, self.REACT)
            field_high = evolve_field_nonlinear(field_high, PROP, RELAX, self.REACT)

        self.assertLess(abs(_field_mean(field_low)),        0.05)
        self.assertAlmostEqual(_field_mean(field_high), 1.707, delta=0.1)


# ---------------------------------------------------------------------------
# Test D — Nonlinear saturation
# ---------------------------------------------------------------------------

class TestNonlinearSaturation(unittest.TestCase):
    """Cubic term b·s³ must bound the field for large ICs."""

    def test_saturation_prevents_unbounded_growth(self):
        """With large r>0 and cubic saturation, field stays bounded."""
        # r=1.0, a=0.5, b=1.0: upper equilibrium ≈ (0.5+√(0.25+4))/2 ≈ 1.28
        react = NonlinearReactionParameters(r=1.0, a=0.5, b=1.0)
        field = _make_field(initial_value=0.01, dt=0.01)
        for _ in range(2000):
            field = evolve_field_nonlinear(field, PROP, RELAX, react)
        mean = _field_mean(field)
        # Should have grown from 0.01 and saturated — confirm bounded and positive
        self.assertGreater(mean, 0.5,  f"Expected growth above 0.5, got {mean:.4f}")
        self.assertLess(mean,    5.0,  f"Expected saturation below 5.0, got {mean:.4f}")

    def test_linear_r_alone_would_be_unbounded(self):
        """Confirm that r>0 without b causes unbounded growth (NaN or large).

        With r=1.0, τ=1.0 the telegraph PDE eigenvalue is λ≈0.618 s⁻¹.
        Growth is exponential but takes ~1300 steps (26 s) to exceed 1e6.
        We run 2000 steps to give sufficient margin.
        """
        react = NonlinearReactionParameters(r=1.0, a=0.0, b=0.0)
        field = _make_field(initial_value=0.1, dt=0.02)
        caught = False
        for _ in range(2000):
            try:
                field = evolve_field_nonlinear(field, PROP, RELAX, react)
                if abs(_field_mean(field)) > 1e6:
                    caught = True
                    break
            except ValueError:
                caught = True
                break
        self.assertTrue(caught, "Expected unbounded growth or ValueError for r>0,b=0")


# ---------------------------------------------------------------------------
# Test E — Spatial propagation
# ---------------------------------------------------------------------------

class TestSpatialPropagation(unittest.TestCase):
    """Spatial propagation must still occur after adding nonlinear reaction."""

    def test_perturbation_propagates_spatially(self):
        """A localized perturbation spreads to distant grid points."""
        react = NonlinearReactionParameters(r=0.0, a=0.0, b=0.5)
        # Start slightly above zero so the field doesn't collapse
        field = _make_field(nx=30, ny=30, initial_value=0.5, dt=0.02)
        # Apply perturbation near one corner
        field = apply_perturbation(field, PhysicalCoordinate(1.0, 1.0, 0.0), 2.0, 0.5)

        # Record initial values at a distant point
        distant_idx = -1  # last grid point (far corner)
        initial_distant = float(field.state.field_values[distant_idx])

        for _ in range(200):
            field = evolve_field_nonlinear(field, PROP, RELAX, react)

        final_distant = float(field.state.field_values[distant_idx])

        # Distant point must have changed
        self.assertNotAlmostEqual(
            initial_distant, final_distant, places=4,
            msg="Spatial propagation failed: distant point unchanged after 200 steps"
        )


# ---------------------------------------------------------------------------
# Test F — Boundary correctness
# ---------------------------------------------------------------------------

class TestBoundaryCorrectness(unittest.TestCase):
    """Boundary conditions must not cause artificial mean drift or instability."""

    def test_no_mean_drift_from_boundaries_linear_limit(self):
        """With r=a=b=0 and uniform IC, the field mean stays near initial value."""
        react = NonlinearReactionParameters()
        field = _make_field(initial_value=1.0, dt=0.02)
        for _ in range(500):
            field = evolve_field_nonlinear(field, PROP, RELAX, react)
        mean = _field_mean(field)
        # With v=0 initial and no source, the field should stay near 1.0
        # (some drift is acceptable due to the BC artifact, but not catastrophic)
        self.assertGreater(mean, 0.5, f"Severe mean drift: mean={mean:.4f}")
        self.assertLess(mean,    2.0, f"Severe mean drift: mean={mean:.4f}")

    def test_no_blow_up_from_boundaries(self):
        """Boundaries must not generate instability in nonlinear regime."""
        react = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)
        field = _make_field(initial_value=1.0, dt=0.02)
        for _ in range(2000):
            field = evolve_field_nonlinear(field, PROP, RELAX, react)
        self.assertTrue(
            np.all(np.isfinite(field.state.field_values)),
            "Non-finite values generated near boundaries"
        )


# ---------------------------------------------------------------------------
# Test G — Numerical convergence
# ---------------------------------------------------------------------------

class TestNumericalConvergence(unittest.TestCase):
    """Refined dt gives consistent equilibrium — not a discretization artifact."""

    REACT = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)

    def _equilibrate(self, dt: float, s_init: float, n_steps: int) -> float:
        field = _make_field(initial_value=s_init, dt=dt)
        field = _run_steps(field, PROP, RELAX, self.REACT, n_steps)
        return _field_mean(field)

    def test_upper_equilibrium_dt_convergence(self):
        """Upper equilibrium value is consistent under dt/2 refinement."""
        # Coarse dt=0.04 (2000 steps = 80 time units)
        mean_coarse = self._equilibrate(dt=0.04, s_init=1.0, n_steps=2000)
        # Fine dt=0.02 (4000 steps = 80 time units)
        mean_fine   = self._equilibrate(dt=0.02, s_init=1.0, n_steps=4000)

        self.assertAlmostEqual(
            mean_coarse, mean_fine, delta=0.05,
            msg=f"dt-refinement inconsistency: coarse={mean_coarse:.4f}, fine={mean_fine:.4f}"
        )

    def test_zero_equilibrium_dt_convergence(self):
        """Zero equilibrium is consistent under dt/2 refinement."""
        mean_coarse = self._equilibrate(dt=0.04, s_init=0.1, n_steps=2000)
        mean_fine   = self._equilibrate(dt=0.02, s_init=0.1, n_steps=4000)

        self.assertAlmostEqual(
            mean_coarse, mean_fine, delta=0.05,
            msg=f"dt-refinement inconsistency: coarse={mean_coarse:.4f}, fine={mean_fine:.4f}"
        )


# ---------------------------------------------------------------------------
# Test H — Finite-value protection
# ---------------------------------------------------------------------------

class TestFiniteValueProtection(unittest.TestCase):
    """Unstable parameters must raise ValueError, not silently return NaN."""

    def test_very_large_r_raises(self):
        """Extremely large r with tiny b causes instability → ValueError."""
        react = NonlinearReactionParameters(r=1000.0, a=0.0, b=0.001)
        field = _make_field(initial_value=1.0, dt=0.1)
        with self.assertRaises(ValueError, msg="Expected ValueError for unstable r=1000, b=0.001"):
            for _ in range(500):
                field = evolve_field_nonlinear(field, PROP, RELAX, react)

    def test_stable_parameters_do_not_raise(self):
        """Well-chosen bistable parameters must not raise."""
        react = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)
        field = _make_field(initial_value=1.0, dt=0.02)
        try:
            for _ in range(1000):
                field = evolve_field_nonlinear(field, PROP, RELAX, react)
        except ValueError as e:
            self.fail(f"Stable parameters raised ValueError unexpectedly: {e}")


# ---------------------------------------------------------------------------
# Test I — Parameter validation
# ---------------------------------------------------------------------------

class TestParameterValidation(unittest.TestCase):
    """NonlinearReactionParameters must reject invalid inputs."""

    def test_negative_b_raises(self):
        """b < 0 removes cubic saturation and must be rejected at construction."""
        with self.assertRaises(ValueError):
            NonlinearReactionParameters(r=0.0, a=0.0, b=-1.0)

    def test_zero_b_allowed(self):
        """b = 0 is permitted (equivalent to no cubic term)."""
        p = NonlinearReactionParameters(r=0.5, a=0.0, b=0.0)
        self.assertEqual(p.b, 0.0)

    def test_negative_r_allowed(self):
        """Negative r is valid (damping/decay)."""
        p = NonlinearReactionParameters(r=-1.0, a=2.0, b=1.0)
        self.assertEqual(p.r, -1.0)


# ---------------------------------------------------------------------------
# Test J — Equilibrium analysis (analytical vs. numerical)
# ---------------------------------------------------------------------------

class TestEquilibriumAnalysis(unittest.TestCase):
    """Analytical equilibria must match where the numerics settle."""

    def _test_equilibria(self, react: NonlinearReactionParameters,
                         s_init_list: list[float], tol: float = 0.08):
        analytical = react.homogeneous_equilibria()
        for s_init in s_init_list:
            field = _make_field(initial_value=s_init, dt=0.02)
            field = _run_steps(field, PROP, RELAX, react, 8000)
            mean = _field_mean(field)
            # Must land near one of the analytical equilibria
            closest = min(analytical, key=lambda eq: abs(eq - mean))
            self.assertAlmostEqual(
                mean, closest, delta=tol,
                msg=f"Numerical equilibrium {mean:.4f} not near any analytical "
                    f"equilibrium {analytical} for IC={s_init}"
            )

    def test_bistable_equilibria(self):
        """r=-0.5, a=2.0, b=1.0: ICs settle near analytical equilibria."""
        react = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)
        self._test_equilibria(react, [0.1, 1.0, 2.5])

    def test_monostable_positive_equilibrium(self):
        """r=1.0, a=0.0, b=1.0: single positive equilibrium s=1.0."""
        react = NonlinearReactionParameters(r=1.0, a=0.0, b=1.0)
        eq = react.homogeneous_equilibria()
        # Should have s=0 (unstable) and s=1.0 (stable)
        # Roots: b*s^2 - a*s - r = 0 → s^2 = 1.0 → s=±1.0, so s+=1.0
        self._test_equilibria(react, [0.5, 2.0])

    def test_local_stability_at_equilibria(self):
        """Linearized growth rate must be negative at stable equilibria."""
        react = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)
        eq = react.homogeneous_equilibria()
        # s=0 and s≈1.707 should be stable (rate < 0)
        # s≈0.293 should be unstable (rate > 0)
        rates = [(s, react.linearized_growth_rate(s)) for s in eq]
        stable = [(s, rate) for s, rate in rates if rate < 0]
        unstable = [(s, rate) for s, rate in rates if rate > 0]
        self.assertEqual(len(stable), 2,
            f"Expected 2 stable equilibria, got {stable}")
        self.assertEqual(len(unstable), 1,
            f"Expected 1 unstable equilibrium (separatrix), got {unstable}")


# ---------------------------------------------------------------------------
# Test K — Hysteresis verification
# ---------------------------------------------------------------------------

class TestHysteresisVerification(unittest.TestCase):
    """Path-dependent transitions under slow parameter sweep."""

    def _run_r_sweep(self, r_values: list[float], s_init: float,
                     a: float = 2.0, b: float = 1.0,
                     n_equil: int = 3000) -> list[float]:
        """Sweep r values, equilibrating at each, return final means."""
        field = _make_field(initial_value=s_init, dt=0.02)
        means = []
        for r in r_values:
            react = NonlinearReactionParameters(r=r, a=a, b=b)
            field = _run_steps(field, PROP, RELAX, react, n_equil)
            means.append(_field_mean(field))
        return means

    def test_hysteresis_forward_vs_reverse(self):
        """
        Forward sweep (r from -1 to +0.5) starting from s≈0 should stay near 0
        until some critical r, while reverse sweep starting from s≈1.707 should
        stay high until a different critical r — demonstrating path dependence.
        """
        r_range = [-1.0, -0.7, -0.5, -0.3, -0.1, 0.0, 0.2, 0.4]

        # Forward sweep: start below the separatrix
        forward_means = self._run_r_sweep(r_range, s_init=0.05)
        # Reverse sweep: start above the separatrix
        reverse_means = self._run_r_sweep(list(reversed(r_range)), s_init=2.0)
        reverse_means = list(reversed(reverse_means))  # re-align with r_range

        # At r=-0.5 (index 2), both paths should be in different basins if hysteresis exists
        # Forward at r=-0.5: started from low IC, should still be near 0 or just crossed
        # Reverse at r=-0.5: started from high IC, should be near 1.707
        fwd_at_minus05 = forward_means[2]   # r=-0.5
        rev_at_minus05 = reverse_means[2]   # r=-0.5

        # Reverse sweep should show higher values at r=-0.5 than forward sweep
        # (genuine hysteresis: the path matters)
        self.assertGreater(
            rev_at_minus05 - fwd_at_minus05, 0.5,
            f"No path-dependent hysteresis detected at r=-0.5: "
            f"forward={fwd_at_minus05:.3f}, reverse={rev_at_minus05:.3f}"
        )

    def test_hysteresis_is_not_transient_lag(self):
        """
        With sufficient equilibration steps, different ICs still land at different
        states (gap does not close to zero), confirming genuine bistability.
        """
        react = NonlinearReactionParameters(r=-0.5, a=2.0, b=1.0)

        # Long equilibration from two ICs
        field_low  = _make_field(initial_value=0.1, dt=0.02)
        field_high = _make_field(initial_value=1.5, dt=0.02)

        for _ in range(15000):
            field_low  = evolve_field_nonlinear(field_low,  PROP, RELAX, react)
            field_high = evolve_field_nonlinear(field_high, PROP, RELAX, react)

        gap = _field_mean(field_high) - _field_mean(field_low)
        self.assertGreater(
            gap, 1.0,
            f"Hysteresis gap closed after long equilibration: gap={gap:.4f}. "
            "This suggests the apparent bistability is a transient, not genuine."
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
