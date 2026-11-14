# SUBSTRATE FOUNDATION VERDICT
**Date:** 2026-11-13  
**Investigation scope:** `domains/physical_field/physical_field_dynamics.py` and `physical_field_models.py`  
**Method:** Source inspection, analytical derivation, executed stress tests.  
**EXP3 and all existing experiments: not modified.**

---

## A. Mathematical Foundation

**Are the governing equations internally consistent?**  
YES. The implemented equations are a standard, well-studied PDE (the telegraph equation / damped wave equation). There are no internal contradictions. The first-order system (∂s/∂t = v, ∂v/∂t = c²∇²s − v/τ) is mathematically consistent with the stated telegraph equation τ∂²s/∂t² + ∂s/∂t = c²τ∇²s.

**Does the implementation faithfully represent the equations?**  
YES for the PDE interior. ONE undocumented deviation: boundary conditions are not stated anywhere but emerge as a zero-Laplacian artifact affecting 12.9% of nodes in the EXP3 30×30 grid. This is a partial defect — interior dynamics are correctly implemented; boundary behaviour is non-standard and unintentional.

**Are there mathematical contradictions or missing definitions?**  
One EXP3-level inconsistency: the `rng_precursor` stream (seed+5000) is documented but not instantiated. This is an EXP3 design issue, not a substrate equation issue.

---

## B. Numerical Foundation

**Is the solver numerically reliable?**  
YES for EXP3 parameters (dt=0.05, Courant number C_r=0.029 — 24× below the CFL instability limit of 0.707 in 2D). Instability threshold confirmed empirically at C_r≈0.87.

**Which phenomena survive convergence testing?**  
- Modal transition (overdamped↔propagating as τ varies): SURVIVES — resolution-independent
- C_spectral sign and regime classification: SURVIVES
- Spatial propagation: SURVIVES
- Velocity-mediated memory: SURVIVES

**Which observed effects are numerical artifacts?**  
The boundary condition zero-Laplacian artifact introduces systematic spectral contamination at ~12.9% of nodes. This is bounded and consistent — it does not change the sign of C_spectral or invalidate regime classification. The error does not decrease with grid refinement (confirmed by nx=32,64,128,256 convergence test), confirming it is a BC artifact, not a timestep/order problem.

---

## C. Intrinsic Substrate Functionality

**Does the substrate exhibit nontrivial dynamics?**  
YES — but not in the ways claimed in EXP2/EXP3 documentation.

**What actually exists and was confirmed by running tests:**

1. **Modal transition (VALIDATED).** C_spectral transitions continuously from ≈−1 (overdamped) to ≈+1 (propagating) as τ increases through the critical value. Measured transition at τ≈2.5–3.0 for the EXP3 grid. Follows directly from D(k) = 4c²τ²k² − 1 and is correctly computed by the spectral observable.

   | τ | C_spectral | Regime |
   |---|-----------|--------|
   | 0.5 | −0.820 | overdamped |
   | 2.0 | −0.002 | overdamped (at transition) |
   | 3.0 | +0.761 | coherent |
   | 5.0 | +1.000 | fully coherent |

2. **Velocity-mediated memory (VALIDATED).** The substrate stores momentum in its velocity field v = ∂s/∂t. After a perturbation is removed, the velocity continues to drive oscillatory evolution. C_spectral difference from an unperturbed control persists for > 10 time units at τ=3 (initial Δc_spectral = +1.86, still +0.93 at t=10). This is a genuine, explicitly represented memory mechanism.

3. **Spatial propagation (VALIDATED).** Disturbances spread across the grid. At τ=3.0 (propagating regime), 44/900 nodes are affected at t=2.0 vs 32/900 at τ=1.0 (overdamped). The propagating regime supports faster spatial spread.

4. **Slow transient persistence (VALIDATED as distinct from hysteresis).** Velocity field can persist across tau parameter changes, creating apparent path-dependence that closes completely at 1000 equilibration steps.

**What is claimed but absent from this implementation:**

1. **Bistability: ABSENT.** The system is linear; superposition holds to 10⁻¹⁵. Linear systems cannot have multiple coexisting attractors. The UTD mod's bistability claim applies to a nonlinear Java implementation — not to this Python substrate.

2. **Nonlinear dynamics: ABSENT.** No saturation functions, no threshold nonlinearities, no activation susceptibility modulation. Perturbation response ratio variation = 0.0000%. Exact superposition verified.

3. **Genuine hysteresis: ABSENT.** What appeared as hysteresis (gap 0.854) in a 200-step sweep closes to 0.000 at 1000 steps. Transient persistence, not path-dependent stable states.

---

## D. Distinctive Capability

**What does the substrate do that matched conventional systems do not?**

| Property | First-order scalar decay | Substrate (telegraph) |
|----------|------------------------|-----------------------|
| Equilibrium at IC mean | NO (decays to zero) | YES (mean preserved exactly) |
| Oscillating modes | NO | YES (propagating regime, τ > τ_c) |
| Spatial communication | NO | YES (via Laplacian coupling) |
| Velocity-mediated memory | NO | YES (C_spectral half-life > 10 time units) |
| Modal transition | NO | YES (D(k) sign change at τ_c) |
| Spectral regime classification | NO | YES (C_spectral ∈ [−1, +1]) |

The substrate provides three genuinely distinctive capabilities over simpler controls:
1. A mean-preserving equilibrium structure — perturbations don't erase history encoded in the mean
2. A tunable modal regime creating qualitatively different dynamics depending on τ
3. A velocity-state memory that retains spectral signatures of past perturbations for many time constants

**Is the effect robust and reproducible?**  
YES. C_spectral std across 20 seeds is 0.04–0.05 at both τ=1 and τ=3. The regime classification is reliable.

---

## E. Mechanism Classification

| Mechanism | Classification | Evidence |
|-----------|---------------|----------|
| Telegraph equation (PDE) | **Validated** | Reconstructed from source; analytically correct; mode decay rates match theory |
| Explicit Euler solver | **Operational but partially defective** | Correct execution; first-order time accuracy; 12.9% BC artifact |
| Boundary conditions | **Defective** (undocumented zero-Laplacian) | Source inspection + convergence test proves BC, not Δt, causes error |
| Spatial propagation | **Validated** | Spatial spread confirmed; faster at higher τ |
| Modal discriminant D(k) | **Validated** | Analytically derived; tau-scan confirms transition at predicted τ_c |
| C_spectral transition | **Validated** | Measured; reproducible; consistent with k_c = 1/(2cτ) |
| Velocity-mediated memory | **Validated** | C_spectral difference > 50% of initial at t=10 |
| Bistability | **Mathematically unsupported** | Linear system; superposition to 10⁻¹⁵; impossible without nonlinearity |
| Genuine hysteresis | **Mathematically unsupported** | Gap closes at 1000 equilibration steps |
| Nonlinear dynamics | **Absent** | 0.0000% ratio variation; exact superposition |
| rng_precursor independence | **Not implemented** | Precursor uses rng_schedule; seed+5000 stream not instantiated |
| Self-organised criticality | **Not tested** | Requires larger parameter space investigation |

---

## Final Verdict

**VERDICT 2 — Functioning but incomplete substrate.**

> Genuine dynamics exist, but important mechanisms require development.

**What is there and validated:**  
A correctly implemented damped wave equation with a well-designed spectral observable. The substrate genuinely classifies transport regimes, encodes memory in its velocity field, supports spatial propagation, and undergoes a real modal transition controlled by τ. These are nontrivial, reproducible, and mathematically grounded properties.

**What is not there:**  
Nonlinearity. Bistability. Genuine hysteresis. These were implied or stated in earlier documentation (EXP2, EXP3, UTD descriptions) but are absent from the Python implementation. The UTD Minecraft mod presumably has them through its six-variable nonlinear Java system. The Python substrate does not replicate UTD — it implements a linear subset of UTD's physics.

**What needs to be added to match the full stated architecture:**
1. Nonlinear activation susceptibility (makes memory formation threshold-dependent)
2. Logistic saturation (bounds field growth; enables multiple equilibria)
3. Genuine structural resistance term (gates perturbation amplitude)
4. Documented, tested, and physically justified boundary conditions

**What is immediately usable:**  
The spectral pipeline (s → FFT → D(k) → C_spectral → agent) is correctly implemented and produces reproducible, meaningful regime classifications. The velocity-mediated memory is real. The modal transition is real. These are sufficient to proceed with EXP4 — provided all claims made about the substrate are limited to what has been demonstrated here, and do not invoke bistability, hysteresis, or nonlinear dynamics that this implementation does not contain.
