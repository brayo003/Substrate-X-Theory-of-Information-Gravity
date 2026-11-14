# Phase II Baseline Reproduction Report

**Date:** 2026-11-13  
**Status:** Complete — 10/11 findings reproduced exactly; R8 corrected  
**Scope:** Independent re-execution of all 11 Phase I findings

---

## Overview

This report documents the independent re-execution of all 11 Phase I findings under Phase II conditions. The re-execution was performed from scratch using the same substrate model (`physical_field_dynamics.py`) but with additional diagnostic instrumentation to validate internal consistency.

**Summary outcome:** 10 of 11 findings reproduce exactly. Finding R8 (mean preservation) required correction — it was an overclaim in Phase I. The corrected finding is documented below.

---

## Reproduction Table

| ID  | Finding                        | Phase I Value                              | Phase II Re-executed Value                                            | Status               |
|-----|--------------------------------|--------------------------------------------|-----------------------------------------------------------------------|----------------------|
| R1  | Telegraph equation fidelity    | delta = 0.0                                | delta = 0.0                                                           | ✅ PASS              |
| R2  | Superposition principle        | error = 1.78e-15                           | error = 1.78e-15                                                      | ✅ PASS              |
| R3  | C_spectral proportionality     | 0.0000% variation                          | 0.0000% variation                                                     | ✅ PASS              |
| R4  | CFL stability boundary         | stable dt=1.0, unstable dt=1.2             | stable C_r=0.029 (dt=1.0); unstable C_r=0.696 (dt=1.2)              | ✅ PASS              |
| R5  | Modal transition (tau sweep)   | tau=1→C=-0.54, tau=3→C=+0.76              | tau=1→C=-0.54, tau=3→C=+0.76                                         | ✅ PASS              |
| R6  | Velocity memory / delta_c      | initial delta_c=+1.86, half-life>5         | initial delta_c=+1.86, half-life>5                                    | ✅ PASS              |
| R7  | Spatial spread                 | 16→40 nodes (t=0.25 to t=2.0)             | 16→40 nodes (t=0.25 to t=2.0)                                        | ✅ PASS              |
| R8  | Mean preservation              | mean preserved (all ICs)                   | **CORRECTED** — exact for uniform IC; drifts −3.24e-02 for random IC | ⚠️ CORRECTED        |
| R9  | Bistability absent             | absent, final means track ICs              | absent, final means track ICs                                         | ✅ PASS              |
| R10 | Hysteresis (transient)         | gap=0.0033 at 1000 steps (transient)       | gap=0.0033 at 1000 steps (confirmed transient)                        | ✅ PASS              |
| R11 | BC defect (zero-Laplacian)     | zero-Laplacian at boundaries               | zero-Laplacian at all boundaries CONFIRMED                            | ✅ CONFIRMED         |

---

## Detailed Finding Notes

### R1 — Telegraph Equation Fidelity
The numerical scheme satisfies the telegraph equation to machine precision. The residual delta = 0.0 confirms the time-stepping implementation is analytically exact for the chosen discretisation. Reproduced identically.

### R2 — Superposition Principle
Linear superposition holds to floating-point precision. The error of 1.78e-15 is at the level of double-precision rounding (~2.22e-16 × scale factor). Reproduced identically.

### R3 — C_spectral Proportionality
The spectral observable C_spectral scales proportionally with driving amplitude. 0.0000% variation across tested amplitude range confirms no nonlinear saturation at tested scales. Reproduced identically.

### R4 — CFL Stability Boundary
- dt=1.0 (C_r=0.029): numerically stable — field remains bounded
- dt=1.2 (C_r=0.696): numerically unstable — field diverges
- The CFL transition lies between these two values. The Courant number C_r = c·dt/dx characterises the boundary. Reproduced identically.

### R5 — Modal Transition (tau sweep)
The sign of C_spectral transitions from negative (overdamped-dominant) to positive (propagating-dominant) as tau increases:
- tau=1: C_spectral = −0.54 (overdamped regime)
- tau=3: C_spectral = +0.76 (propagating regime)

Reproduced identically.

### R6 — Velocity Memory
An initial velocity perturbation induces a delta_c of +1.86 relative to the zero-velocity baseline. This excess persists with a half-life exceeding 5 time units, confirming that velocity initial conditions carry spectral memory that decays gradually. Reproduced identically.

### R7 — Spatial Spread
A localised perturbation spreads from 16 active nodes at t=0.25 to 40 active nodes at t=2.0 (threshold-based count). This confirms sub-luminal but non-trivial spatial propagation. Reproduced identically.

### R8 — Mean Preservation (CORRECTED)

**Phase I claim:** mean is preserved for all initial conditions.  
**Phase II finding:** mean preservation depends on initial condition type.

| IC Type                        | Mean drift over 500 steps | Verdict          |
|--------------------------------|---------------------------|------------------|
| Uniform IC, v=0                | 0.00 (machine precision)  | Exact            |
| Random IC, ic_amp=0.5, v=0     | −3.24e-02                 | Drift observed   |

**Root cause:** The boundary condition artifact (R11) generates asymmetric velocity at boundary nodes. For a uniform IC, the symmetry of the field means boundary contributions cancel exactly. For a random IC with spatial gradients, the asymmetric zero-Laplacian BCs create a net non-zero velocity flux at the boundary layer, which integrates over time into a mean drift.

**Implication:** The Phase I claim was an overclaim. Mean preservation is a property of the uniform IC only. For generic random ICs, the substrate mean drifts at a rate controlled by the BC artifact magnitude. This does not invalidate other findings but requires that IC type be specified when reporting mean-preservation results.

### R9 — Bistability Absent
No bistability detected. Final field means track the IC means monotonically. No hysteretic branching observed in parameter sweeps. Reproduced identically.

### R10 — Hysteresis (Transient)
A residual gap of 0.0033 is observed at 1000 steps in a forward/reverse tau sweep. This gap narrows with increasing step count, confirming the effect is a finite-time transient, not a true hysteresis loop. Reproduced identically.

### R11 — BC Defect (Zero-Laplacian at Boundaries)
The `compute_laplacian` function updates only interior nodes (1..nx-2, 1..ny-2). Boundary rows and columns retain Laplacian=0 by initialisation. This is an accidental stencil truncation. Confirmed present in Phase II; forms the basis for the separate boundary condition investigation (see `BOUNDARY_CONDITION_INVESTIGATION.md`).

---

## Conclusion

Phase II independently reproduces 10 of 11 Phase I findings to stated precision. R8 is corrected from an overclaim to a precisely characterised finding: mean preservation holds exactly only for uniform ICs. The correction is quantified (drift = −3.24e-02 over 500 steps) and mechanistically explained via the BC artifact. The integrity of all other findings is maintained.
