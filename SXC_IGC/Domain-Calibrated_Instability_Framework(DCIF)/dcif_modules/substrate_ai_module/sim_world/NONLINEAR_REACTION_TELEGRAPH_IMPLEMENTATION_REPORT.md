# Nonlinear Reaction-Telegraph Substrate — Implementation Report

**Date:** 2026-11-13  
**Status:** COMPLETE — all criteria verified

---

## 1. Implemented Equation

The active physical-field substrate now implements the **nonlinear reaction-telegraph equation**:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + r·s + a·s² − b·s³ + S(x,t)
```

Rewritten as a first-order system (state variables `s` and `v = ∂s/∂t`):

```
∂s/∂t = v
∂v/∂t = [c²∇²s + r·s + a·s² − b·s³ + S − v] / τ
```

**Parameters:**
- `s` — substrate field value (information density, bits/m³)
- `τ > 0` — relaxation time (s), controls wave-vs-diffusion regime
- `c > 0` — propagation speed (m/s)
- `r` — linear reaction coefficient (s⁻¹): positive → growth, negative → damping
- `a ≥ 0` — quadratic (autocatalytic) coefficient (1/(density·s))
- `b ≥ 0` — cubic saturation coefficient (1/(density²·s)): must be > 0 for global boundedness when r ≠ 0

Setting `r = a = b = 0` recovers the original linear telegraph equation exactly (verified to precision 10⁻¹²).

---

## 2. Numerical Scheme

**Method:** Asymmetric two-stage explicit Euler — same scheme as the original linear solver.

```
acceleration = (c²·∇²s + r·s + a·s² − b·s³ + S − v) / τ
v_new        = v + dt·acceleration
s_new        = s + dt·v_new
```

The spatial Laplacian uses the existing second-order finite-difference stencil with the same boundary conditions (zero-Laplacian at boundary nodes, as documented in `BOUNDARY_CONDITION_INVESTIGATION.md`).

---

## 3. Stability Analysis

### 3.1 Von Neumann stability (EXP3 parameters)

The characteristic equation for the amplification matrix of a spatial Fourier mode is:

```
λ² − (2 − ρ_k − dt/τ)λ + (1 − dt/τ) = 0
```

where `ρ_k = 4c²dt²/dx² · sin²(k·dx/2) ≥ 0`.

Stability requires `ρ_max ≤ 2 − dt/τ` (Nyquist worst case):

| Configuration | `4c²dt²/dx²` | `2 − dt/τ` | Stable? |
|---|---|---|---|
| EXP3 (c=1, dt=0.05, dx≈1.724 m, τ=1) | 0.00336 | 1.950 | ✓ |
| Kernel (c=1, dt=0.1, dx≈2.041 m, τ=1) | 0.00960 | 1.900 | ✓ |

Courant numbers: EXP3 `Cr = 0.029`, Kernel `Cr = 0.049`. Both well within the stability margin.

### 3.2 Nonlinear stiffness

The cubic term introduces a field-amplitude-dependent effective linearized rate of `|3b·s²|`. For large deviations from equilibrium the local stiffness increases. Under the documented bistable parameter set (`r=−0.5, a=2.0, b=1.0`) with `dt=0.02–0.05`, no instability was observed across 10,000-step runs (Test H and C).

**Warning:** Unstable parameter combinations (e.g. `r=1000, b=0.001`) correctly raise `ValueError` rather than returning NaN silently. Callers should reduce `dt` or increase `b` if instability occurs.

---

## 4. Stationary Homogeneous Equilibria

For spatially uniform fields (`∇²s = 0`) and `ṡ = s̈ = 0`:

```
r·s + a·s² − b·s³ = 0
```

Solutions:
```
s₀ = 0  (always)
s± = (a ± √(a² + 4·b·r)) / (2·b)   when discriminant ≥ 0
```

### 4.1 Documented bistable parameter set

`r = −0.5, a = 2.0, b = 1.0` — used in all bistability tests.

| Equilibrium | Value | f′(s*) | Stability |
|---|---|---|---|
| s₀ | 0.000000 | −0.500000 | **Stable** |
| s− | 0.292893 | +0.414214 | Unstable (separatrix) |
| s+ | 1.707107 | −2.414214 | **Stable** |

The analytical values match to `< 10⁻⁶` and are verified by `homogeneous_equilibria()` and `linearized_growth_rate()` methods on `NonlinearReactionParameters`.

### 4.2 Bistability condition

Genuine bistability (s₀ and s+ both stable, s− as separatrix) requires:
```
r < 0  AND  a² + 4·b·r > 0  →  a > 2√(−b·r)
```

For `r=−0.5, b=1.0`: requires `a > 2√0.5 ≈ 1.414`. With `a=2.0`: confirmed.

### 4.3 Coexistence (saddle-node boundary)

At `a² + 4·b·r = 0` (i.e. `a = 2√(−br)`), s− and s+ collide in a saddle-node bifurcation and the upper stable state disappears. For `b=1`: this occurs at `r = −a²/4`. The system transitions from bistable to monostable as `r` decreases below this threshold.

---

## 5. Numerical vs. Analytical Equilibrium Comparison

Test results from `test_nonlinear_reaction_telegraph.py` (Test J):

| Initial condition | Analytical target | Numerical final (mean) | Error |
|---|---|---|---|
| s=0.1 (below separatrix) | 0.000 | <0.05 | ✓ |
| s=1.0 (above separatrix) | 1.707 | 1.707 ± 0.05 | ✓ |
| s=2.0 (above upper eq.) | 1.707 | 1.707 ± 0.1 | ✓ |

Note: IC=3.0 overshoots the separatrix due to inertia in the second-order PDE (the velocity term carries the field into the lower basin). This is physically correct behavior — the telegraph PDE has memory of its trajectory, not just its position.

---

## 6. Hysteresis

A forward/reverse sweep in `r` (from −1.0 to +0.4, then reversed) with identical equilibration steps demonstrates path-dependent transitions:

- Forward sweep starting from s≈0: field stays near s=0 through the bistable regime
- Reverse sweep starting from s≈2.0: field stays near s≈1.707 at the same r values

At `r=−0.5` the gap between forward and reverse paths is **> 0.5 field units**. This is genuine dynamical hysteresis arising from the nonlinear potential of the ODE — not a threshold automaton.

Extended equilibration (15,000 steps) confirms the gap does not close, ruling out transient relaxation as an explanation.

---

## 7. Modified Files

| File | Change |
|---|---|
| `domains/physical_field/physical_field_models.py` | Added `NonlinearReactionParameters` dataclass with `homogeneous_equilibria()`, `linearized_growth_rate()`, `is_linear` |
| `domains/physical_field/physical_field_dynamics.py` | Added `evolve_field_nonlinear()` function; added `NonlinearReactionParameters` import |
| `domains/physical_field/physical_field_domain.py` | Updated `apply()` to call `evolve_field_nonlinear`; added `_reaction_params` global; added `set_nonlinear_reaction_parameters()`, `get_reaction_parameters()`, `set_reaction_parameters()` |
| `domains/physical_field/__init__.py` | Exported `NonlinearReactionParameters`, `evolve_field_nonlinear`, and new domain functions |
| `kernel/world_kernel.py` | Added `self._reaction_params`; updated `initialize_physical_field()` to init reaction params; added `set_nonlinear_reaction_parameters()` method; passes `reaction_params` in per-world context dict |
| `exp3_environment.py` | Added `evolve_field_nonlinear` and `NonlinearReactionParameters` imports; added `reaction_params` optional parameter to `run_trial()` (default `None` = linear, fully backward-compatible); updated field evolution call |
| `domains/physical_field/test_nonlinear_reaction_telegraph.py` | New file: 26 tests A–K covering all required verification criteria |

No other files were modified. No existing tests were broken.

---

## 8. Backward Compatibility

The nonlinear solver falls through to `evolve_field()` exactly when `reaction_params is None` or `reaction_params.is_linear` (all coefficients zero). This is the default in all three execution paths:

- `physical_field_domain.apply()`: `_reaction_params` defaults to `NonlinearReactionParameters()` (all-zero)
- `world_kernel`: `_reaction_params` initialized to `NonlinearReactionParameters()` (all-zero)
- `exp3_environment.run_trial()`: `reaction_params=None` default

Existing callers require no changes. All 26 prior regression tests pass unchanged.

---

## 9. Test Results

```
Test suite: domains/physical_field/test_nonlinear_reaction_telegraph.py
Ran 26 tests in ~18s

A — Linear-limit recovery (3 tests)         PASS
B — Homogeneous equilibrium convergence (4) PASS
C — Bistability (2)                         PASS
D — Nonlinear saturation (2)                PASS
E — Spatial propagation (1)                 PASS
F — Boundary correctness (2)                PASS
G — Numerical convergence / dt refinement (2) PASS
H — Finite-value protection / ValueError (2) PASS
I — Parameter validation (3)                PASS
J — Equilibrium analysis (3)                PASS
K — Hysteresis (2)                          PASS

Result: 26/26 PASSED

Regression suite: domains/physical_field/test_physical_field.py
Result: 26/26 PASSED (zero regressions)

EXP3 end-to-end:
  linear   c_spectral_mean = −0.9199
  nonlinear c_spectral_mean = −0.2809  (diff = 0.639 — nonlinear dynamics active)
  Both trials: valid=True, 40 per-tick records each
```

---

## 10. Remaining Limitations

1. **Boundary condition artifact** (pre-existing, not introduced by this change): Zero-Laplacian BCs contaminate ~12.9% of grid nodes and shift the C_spectral regime transition. Documented in `BOUNDARY_CONDITION_INVESTIGATION.md`. Repair: implement Neumann or periodic BCs.

2. **Euler timestep adequacy for stiff nonlinear regimes**: For large `a` or small `b`, the cubic term can create fast timescales that require `dt < 1/(3b·s²)`. The solver raises `ValueError` on overflow rather than silently corrupting results. Users must verify `dt` is appropriate for their parameter regime.

3. **Source term S not used in EXP3**: The PDE accepts an external source `S(x,t)` but EXP3 passes `source_term=None`. All forcing remains impulsive (via `apply_perturbation`). This is unchanged from the linear implementation.

4. **C_spectral is location-agnostic** (pre-existing): As documented in `PHASE_II_FINAL_VERDICT.md`, C_spectral cannot encode the spatial location of a perturbation. The nonlinear substrate adds genuine field-level nonlinear dynamics but does not change this property of the scalar summary observable.
