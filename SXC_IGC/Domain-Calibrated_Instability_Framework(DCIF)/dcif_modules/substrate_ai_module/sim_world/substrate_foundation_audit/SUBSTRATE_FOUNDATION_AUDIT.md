# SUBSTRATE FOUNDATION AUDIT
**Date:** 2026-11-13  
**Scope:** Complete mathematical, implementation, and experimental audit of the Python substrate  
**Files inspected:** `physical_field_dynamics.py`, `physical_field_models.py`  
**Tests executed:** 12 stress tests + convergence, stability, and control comparisons  
**Existing experiments:** Not modified.

---

## 1. What Was Investigated

The substrate was isolated from all agent, task, and EXP3 code. Tests were run on the field solver alone: `evolve_field`, `apply_perturbation`, `compute_spectral_transport_observable`, and the underlying `compute_laplacian`.

---

## 2. The Actual Governing Equation

Inspected directly from `evolve_field` (lines 104–125). The implemented equations are:

```
∂s/∂t  =  v
∂v/∂t  =  c² ∇²s  −  v/τ  +  S/τ
```

This is the first-order system form of the **telegraph equation**:

```
τ ∂²s/∂t²  +  ∂s/∂t  =  c²τ ∇²s  +  S(x,t)
```

This is a standard hyperbolic PDE with damping. It is linear, well-posed, and well-studied in mathematical physics. No nonlinear terms are present anywhere in the Python implementation.

---

## 3. Implementation Findings

### Correct
- PDE interior: exact match between documented equation and implemented update
- Spectral observable: mathematically rigorous FFT-based classification using D(k) = 4c²τ²k² − 1
- Mean-subtraction before FFT (prevents DC dominance)
- Courant number at EXP3 parameters: C_r = 0.029 (24× below instability threshold)

### Defective
- **Boundary conditions:** Not documented. The Laplacian at boundary nodes (i=0, i=nx-1, j=0, j=ny-1) is set to zero by stencil truncation. This is not standard Dirichlet or Neumann BC. It affects 12.9% of nodes in the EXP3 30×30 grid. Convergence test confirms the error is BC-driven (does not decrease with refinement).

### Absent (documented but not implemented)
- `rng_precursor` stream (seed+5000): mentioned in EXP3 code comments, never instantiated
- Nonlinear terms: none present — the system is strictly linear

---

## 4. Analytical Properties Derived

### Characteristic roots for spatial mode k

**Discriminant:** Δ = 1 − 4c²τ²k²

| Regime | Condition | Roots | Behaviour |
|--------|-----------|-------|-----------|
| Propagating | 4c²τ²k² > 1 | Complex conjugates λ = −1/(2τ) ± iω | Damped oscillation, decay rate γ = 1/(2τ) |
| Overdamped | 4c²τ²k² < 1 | Two real negatives | Pure exponential decay |
| Critical | 4c²τ²k² = 1 | Repeated root −1/(2τ) | A(t)·exp(−t/(2τ)) |

### Critical wavenumber and tau

```
D(k) = 0  →  k_c = 1/(2cτ)
```

For EXP3 grid (L=50m, c=1): k_c = 1/(2τ). The lowest resolved mode k_min = 2π/50 = 0.126 crosses into propagating at τ_c = 1/(2·0.126) = 3.97. Empirically measured transition at τ≈2.5–3.0 (higher-k modes cross first).

### Equilibria

The uniform field s(x) = C, v(x) = 0 is an equilibrium for any C. The spatial mean is exactly conserved. All spatial fluctuations (k≠0 modes) decay. There is no unique equilibrium — there is a continuous family indexed by the spatial mean.

---

## 5. Stress Test Results (all executed, not fabricated)

| Test | Hypothesis | Result |
|------|-----------|--------|
| T1: Uniform field stability | s=constant stays constant | PASS — exact (numerical zero change) |
| T2: Mode decay rate | Propagating: γ=1/(2τ); Overdamped: λ_slow matches | BC artifact prevents exact match; overdamped 11.9% error (WARN) |
| T3: CFL stability | Stable for C_r < 0.707 | PASS — instability at C_r=0.87 confirmed |
| T4: Equilibrium convergence | Mean preserved; gradients decay | PASS — mean preserved; std drops to 20–32% in 500 steps |
| T5: Perturbation linearity | Ratio variation = 0% | PASS — 0.0000% variation; perfect linearity |
| T6: Memory retention | Δc_spectral persists after perturbation removed | PASS — half-life > 10 time units at τ=3 |
| T7: Bistability | Cannot exist in linear system | CONFIRMED ABSENT — multiple IC tests, no attractor switching |
| T8: Hysteresis | Gap closes with equilibration | CONFIRMED TRANSIENT — gap 0.854 → 0.000 at 1000 steps |
| T9: Modal dynamics | C_spectral transition at τ_c | PASS — transition measured at τ≈2.5–3.0 |
| T10: C_spectral validation | Narrow perturbation raises C_spectral | PASS — Δc=+0.19 at τ=1, Δc=+0.03 at τ=3 (already high) |
| T11: Control comparison | Substrate richer than first-order decay | PASS — mean preservation, oscillation, memory absent in control |
| T12: Superposition | Linear: evolve(A+B) = evolve(A)+evolve(B) | PASS — error 6.5×10⁻¹⁶ |

---

## 6. What the Substrate Is and Is Not

### Is
- A linear, second-order, dissipative PDE with spatial coupling
- A mean-preserving dynamical system with velocity-mediated memory
- A system with tunable modal character (overdamped/propagating) controlled by τ
- A system where perturbations spread spatially and leave spectral traces that persist

### Is Not
- Nonlinear
- Bistable
- Hysteretic
- An implementation of UTD's full six-variable nonlinear dynamics
- Capable of producing emergent attractors or self-organised criticality

---

## 7. Files Produced

| File | Contents |
|------|----------|
| `SUBSTRATE_EQUATION_MAP.md` | Complete equation-to-code correspondence |
| `SUBSTRATE_NUMERICAL_VALIDATION.md` | CFL, convergence, BC artifact, energy budget |
| `SUBSTRATE_DYNAMICS_REPORT.md` | All 8 dynamical phenomenon tests with measurements |
| `SUBSTRATE_FOUNDATION_AUDIT.md` | This file — complete overview |
| `SUBSTRATE_FOUNDATION_VERDICT.md` | Final verdict and mechanism classification |

All test code was executed in the same session using `PYTHONPATH=.. .venv/bin/python`. No results are inferred or fabricated.
