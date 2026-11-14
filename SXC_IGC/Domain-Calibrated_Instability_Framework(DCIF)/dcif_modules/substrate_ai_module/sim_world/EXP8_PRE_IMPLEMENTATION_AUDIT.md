# EXP8 Pre-Implementation Audit

**Date:** 2026-11-13  
**Mode:** Repository-grounded inspection before any Task 8 code changes.  
**Preservation:** `exp8/task6_checksums_before.txt`, `exp8/task7_checksums_before.txt` recorded.

---

## 1. Actual repository structure (relevant subset)

```
sim_world/
  domains/physical_field/
    physical_field_dynamics.py   # evolve_field, evolve_field_nonlinear, apply_perturbation
    physical_field_models.py     # NonlinearReactionParameters, Propagation/Relaxation
    physical_field_domain.py
    test_nonlinear_reaction_telegraph.py
    test_physical_field.py
    test_modal_validation.py
  kernel/world_kernel.py         # WorldKernel orchestration (not the field solver)
  exp6_corrected/                # IMMUTABLE Task 6 corrective package
  exp7/                          # IMMUTABLE Task 7 package
  exp8/                          # NEW (this task)
```

`world_kernel.py` orchestrates simulation/planning/governance. Field evolution used by Tasks 6–8 is **not** routed through the kernel for these offline experiments; it calls `evolve_field_nonlinear` directly.

---

## 2. Active field evolution path

**Independently verified in source:**

1. `initialize_field_state(...)` → `InformationDensityField`
2. `apply_perturbation(field, PhysicalCoordinate, amp, width)` — additive Gaussian
3. `evolve_field_nonlinear(field, prop, relax, react)` — one explicit Euler step
4. Linear limit: `react is None` or `react.is_linear` → fall-through to `evolve_field`

Task 7 path: `exp7/memory.py` → `Exp7SubstrateMemory.tick_update` → `evolve_field_nonlinear`.

---

## 3. Mathematical equation implemented

**Docstring claim** (`evolve_field_nonlinear`):

\[
\tau s_{tt}+s_t=c^2\tau\nabla^2 s+rs+as^2-bs^3+S
\]

**Code-implemented update** (verified lines 279–283):

```
acceleration = ((c**2)*laplacian + reaction + source - v) / tau
v_new = v + dt * acceleration
s_new = s + dt * v_new
```

which is equivalent to:

\[
\tau s_{tt}+s_t=c^2\nabla^2 s+rs+as^2-bs^3+S
\]

**Ambiguity (documented, not “fixed” for Task 8):** The Laplacian term lacks a factor of \(\tau\) relative to the docstring and to `evolve_field`’s linear scheme (which yields \(c^2\tau\nabla^2 s\)). **At Task 6/7 parameters \(\tau=1\), the two forms coincide.** Task 8 keeps \(\tau=1\) for confirmatory work and treats \(\tau\neq 1\) as a sensitivity probe only, with this caveat.

---

## 4. Parameter definitions and units

From `NonlinearReactionParameters` docstring (models.py):

| Symbol | Role | Units (if \(s\) has density \(\rho\)) |
|---|---|---|
| \(r\) | linear reaction | s⁻¹ |
| \(a\) | quadratic | 1/(ρ·s) |
| \(b\) | cubic saturation (≥0) | 1/(ρ²·s) |
| \(c\) | propagation speed | m/s |
| \(\tau\) | relaxation / inertia | s |
| \(\Delta t\) | time step | s |

Task 7 frozen bistable set: \(r=-0.5,a=2,b=1,\tau=1,c=1,\Delta t=0.05\).

Homogeneous equilibria: \(s=0\), \(s_-=(2-\sqrt{2})/2\approx0.293\), \(s_+=(2+\sqrt{2})/2\approx1.707\).

---

## 5. Boundary conditions

`compute_laplacian` updates only interior indices `[1:-1]`. Boundary cells receive **zero Laplacian contribution** (Dirichlet-like fixed-boundary stencil). Boundary cells still evolve via reaction/velocity updates. No periodic BC in the active path.

---

## 6. Numerical integration method

Two-stage explicit Euler (asymmetric): update \(v\) then \(s\) with \(v_{\mathrm{new}}\). Non-finite check raises `ValueError`. No implicit or symplectic integrator.

---

## 7. Stability and numerical limitations

**From existing tests** (`test_nonlinear_reaction_telegraph.py`):

- Homogeneous basin attraction below/above separatrix.
- dt convergence near equilibria.
- Saturation prevents unbounded growth for tested params.
- Large \(r\) can raise; bistable params stable at \(\Delta t\le0.05\).
- Hysteresis tests present.

**Limitations:** Explicit Euler + cubic stiffness; localized deposits can overshoot; grid 30×30 used in Tasks 6–7 may under-resolve fine separation scans.

---

## 8. Existing computational capabilities

| Capability | Status | Evidence type |
|---|---|---|
| Passive retention / delayed recovery | Established | Task 6 G5 (report + raw JSON; not re-verified here) |
| Cross-agent communication via field | Established | Task 7 Track A (report + raw JSON) |
| Bistable spatial AND (coincidence) | Established vs linear | Task 7 Track B T7–T8 |
| Advantage vs messaging/blackboard | Not established | Task 7 T9 FAIL |
| Temporal order discrimination | Failed (secondary) | Task 7 B_temporal nonlinear acc=0 |

---

## 9. Existing tests and coverage

`test_nonlinear_reaction_telegraph.py`: linear limit, basin attraction, equilibria, spatial propagation, boundary mean drift, dt convergence, parameter validation, hysteresis.

**Gaps for Task 8:** No response-surface coincidence scan; no temporal-integration suite; no matched-mass spatial discrimination; no conflict/interference suite; no pattern-completion suite; no readout-vs-dynamics controls as first-class tests.

---

## 10. Task 6 / 7 evidence carried forward (as prior experimental findings)

Carried forward **as reported results**, not independently re-run:

1. Bistable dynamics with IC \(s=0\).
2. Recoverable deposits at delay 30 (linear and nonlinear).
3. Hazard behavioural utility under corridor protocol (Task 7 Track A).
4. Nonlinear AND F1≈0.987 vs linear F1=0 under Task 7 encoding; messaging/BB F1=1.0.
5. Reaction ablation abolishes AND.

Task 8 does **not** treat these as Task 8 confirmatory evidence.

---

## 11. Defects / ambiguities relevant to Task 8

1. Docstring vs code \(\tau\) factor on Laplacian (see §3).
2. Single scalar field — polarity ≠ multi-semantic channels.
3. Hand-designed local-max readout can smuggle computation if not constrained.
4. Task 7 AND used a single threshold near one operating point — need response surface.
5. Negative deposits: mathematically allowed as signed perturbations; semantic “inhibitory channel” not established.
6. **Task 7 AND encoding ambiguity (independently verified in `exp7/collective_computation.py`):** `_deposit_and` deposits each logical input twice (kind `X`/`Y` **and** kind `event`), so `AND_SUB_AMP=0.18` is effectively ~0.36 per site. Task 8 does **not** edit Task 7; it uses a clean single-Gaussian-per-input encoding with pilot-calibrated `A_SUB_AMP=0.40`.

---

## 12. Proposed experimental architecture

```
exp8/
  config.py, field_core.py, decode.py, ablations.py
  exp_a_coincidence.py … exp_f_pattern.py
  numerical_validation.py, baselines.py, behavioural_bridge.py
  runner.py, classify.py
exp8_substrate_computational_expressivity.py
tests/test_exp8_computational_expressivity.py
```

**Hypotheses (new, to be tested):**

- H1: Coincidence detection is a Category 3–4 nonlinear primitive with a finite separation/amplitude window.
- H2: Temporal integration has a finite memory window; order discrimination is weak under scalar bistability.
- H3: Spatial discrimination of equal-mass arrangements is limited; arrangement effects are often Category 2/3 amplitude-localization effects.
- H4: Threshold integration + hysteresis is Category 3 and mechanistically reaction-dependent.
- H5: Conflict/interference lacks reliable semantic resolution in the scalar model (Category 0–2).
- H6: Pattern completion beyond amplification is not supported without a stored attractor template (likely Category 0–1).

**Distinction:** Storage/communication (Tasks 6–7) vs intrinsic input→dynamics→output transformations (Task 8 Track C).
