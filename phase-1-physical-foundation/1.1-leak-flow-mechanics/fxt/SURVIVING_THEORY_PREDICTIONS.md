# SURVIVING_THEORY_PREDICTIONS.md
## C2/SXC-IGC — Predictions That Survive All Four Criteria

**Date:** 2026-08-22
**Four criteria for a prediction to survive:**
  1. Derivable from C2 (not assumed, not imported)
  2. Quantitatively constrained (not a free-parameter shape fit)
  3. Not reproduced by generic conventional stochastic mechanisms
  4. Experimentally measurable in principle

**Sources:** THEORY_CLOSURE_AUDIT.md, GAP7_REDERIVATION.md,
  PARAMETER_OBSERVABLE_RANK.md, CONVENTIONAL_EQUIVALENCE_AUDIT.md,
  ADVERSARIAL_NULL_AUDIT.md, EXPERIMENTAL_RESCUE_AUDIT.md

---

## Screening Table: All Candidates

Every C2 prediction listed, evaluated against all four criteria.

| Prediction | (1) Derived? | (2) Constrained? | (3) Not conventional? | (4) Measurable? | Survives? |
|-----------|-------------|------------------|-----------------------|-----------------|-----------|
| Lorentzian S_JJ(ω) | Yes [T] | No — τ_B, S₀ free | No — identical to OU | Yes | **FAIL (2,3)** |
| Γ_φ ∝ ω_rot² | Yes [T conditional] | No — k_rot free | No — any bath with flat PSD | Yes | **FAIL (2,3)** |
| Gaussian NM onset | Yes [T] | No — τ_B free | No — any finite-memory bath | Yes | **FAIL (2,3)** |
| K₀ spatial shape | Yes [T partial] | No — ξ_c free | No — M7/M9 degenerate | Yes (hardware blocked) | **FAIL (2,3)** |
| T₂ ≤ 2T₁ structural bound | Yes [T] | Yes — no free params | No — standard QC bound | Yes | **FAIL (3)** |
| P3 consistency c = ξ_c/(2τ_B) | Yes [exact] | Yes — ratio is exact | **Conditional** — not if c ≈ v_sound | Blocked (NMP=0.033) | **CONDITIONAL** |
| c(T) = const vs temperature | Yes [exact] | Yes — ratio const at all T | Yes — 1/f bath has no speed | No — T-variation unavailable | **FAIL (4)** |

---

## Result: Zero Unconditionally Surviving Predictions

No prediction passes all four criteria unconditionally.

---

## The One Conditional Survivor

**Prediction: P3 self-consistency — c = ξ_c / (2τ_B)**

### Criterion 1: Derived from C2?

**YES — exact derivation.**

From the PRW: τ_B = 1/(2λ) and ξ_c = v/λ.
Therefore: ξ_c / (2τ_B) = (v/λ) / (2 · 1/(2λ)) = (v/λ) · (λ) = v = c.

This is an exact algebraic identity. No approximation. No assumption
beyond the PRW definition itself. Source: substrate_transport_derivation.md,
parameter identification section [T].

### Criterion 2: Quantitatively constrained?

**YES — once c is measured once, all future measurements are constrained.**

The constraint is: if (ξ_c, τ_B) are measured at conditions A and (ξ_c', τ_B')
at conditions B (different substrate fraction, different temperature, different
chip), then the theory predicts:

```
ξ_c / (2τ_B) = ξ_c' / (2τ_B') = c
```

This ratio must be the same constant c across all conditions. This is a
genuine quantitative constraint: measuring at one condition fixes a prediction
for all other conditions.

However: the value of c is not predicted by C2. It must first be measured
from data. Therefore this is a consistency constraint, not a forward prediction.

### Criterion 3: Not reproduced by generic conventional mechanisms?

**CONDITIONALLY YES.**

A conventional two-bath model has separate (ξ₁, τ₁) and (ξ₂, τ₂) from
independent processes. There is no reason for ξ₁/(2τ₁) = ξ₂/(2τ₂) in general.
An OU bath with spatial correlation ξ_OU has no mechanism coupling ξ_OU
to its temporal correlation time τ_OU via a velocity.

Therefore: if ξ_c/(2τ_B) is measured to be constant across conditions AND
that constant value is anomalous (≪ v_sound), then no conventional mechanism
predicts this behavior.

**Non-discriminating outcomes:**
- c_measured ≈ v_sound (~5000–8500 m/s, Si acoustic): consistent with phonon bath.
  A conventional phonon-mediated decoherence model would also have ξ_phonon/(2τ_phonon) ≈ v_sound.
  P3 cannot then distinguish C2 from phonon bath.
- c_measured ≈ v_light (EM): consistent with electromagnetic coupling.
- c_measured varies across conditions: falsifies C2.

**Discriminating outcome:**
- c_measured = ξ_c/(2τ_B) ≈ 1–500 m/s, constant across conditions.
  No known conventional mechanism for a superconducting qubit chip predicts
  a persistent velocity-linked correlation at ~10–500 m/s. This range is
  ×10–×1000 below any known phonon mode in Si, Al, or Nb.

### Criterion 4: Measurable in principle?

**YES in principle. NO on current hardware.**

Measuring ξ_c requires spatial decoherence correlation (O4).
Measuring τ_B requires NM Ramsey curvature (O3/O5) with NMP ≥ 0.1.

Current hardware blockers:
- NMP = 0.033 on Brisbane (need ≥ 0.1): τ_B not extractable
- K₀/power-law shape degeneracy: ξ_c not reliably measurable on 11-bin geometry
- No temperature variation available (IBM Open Plan)

The measurement is feasible in principle on a device with:
- NMP ≥ 0.1 (requires τ_B ≥ 15 µs or T₂ ≪ Brisbane median)
- Spatial range spanning ≥ 20 bins from 0.1–10 ξ_c
- Independent M7/M9 exclusion by non-decoherence measurement

### Summary of P3

| Criterion | Status | Notes |
|-----------|--------|-------|
| (1) Derived from C2 | YES — exact | ξ_c = 2cτ_B is exact algebra |
| (2) Quantitatively constrained | YES — conditional | Fixes ratio once c is measured |
| (3) Not conventional | CONDITIONAL | Only if c ≪ v_sound |
| (4) Measurable in principle | YES in principle, NO on current hardware | NMP and spatial range blockers |

**P3 is the only surviving candidate, and it is conditional on (3) and
blocked on (4). It is not currently executable.**

---

## What P3 Can and Cannot Establish

**If executed and c_measured ≪ v_sound (e.g., c ~ 50 m/s):**
- Establishes: a spatial-temporal coupling exists with anomalous velocity
- Supports: the existence of a substrate propagating at ~50 m/s
- Does NOT establish: the PRW mechanism is the correct explanation
- Does NOT confirm: SXC-IGC as a complete theory
- Requires: independent replication on a different chip geometry

**If executed and c_measured ≈ v_sound:**
- Establishes: a spatial-temporal coupling exists consistent with phonon bath
- Does NOT distinguish C2 from phonon-mediated conventional decoherence
- Result: inconclusive

**If executed and the ratio c = ξ_c/(2τ_B) varies across conditions:**
- Falsifies C2: the substrate speed would not be constant
- The PRW model would not be the correct description of the noise source

---

## Predictions That Were Rejected and Why

**T₂ ≤ 2T₁ bound:**
Derived from the substrate [T] (C2_FOUNDATIONS.md Theorem HC-4, Q-4).
But this is the standard quantum channel bound, derivable without the substrate
framework from the Lindblad structure alone. Criterion (3) fails.

**ω_rot² Ramsey scaling:**
Derived [T conditional]. But the same scaling follows from any bath with
finite variance at ω_rot (rotating-frame coupling geometry). Criterion (3) fails.

**K₀ spatial shape:**
Derived from 2D telegrapher Green's function [partial T]. But degenerate with
power-law covariance on accessible hardware. Criteria (2) and (3) fail.

**Lorentzian temporal PSD:**
Derived [T]. But identical to any OU bath. Criterion (3) fails completely.

---

## Conclusion

**Exactly zero unconditional predictions survive all four criteria.**

**Exactly one conditional prediction survives (P3), subject to:**
- c_measured being anomalous (not computable from theory — criterion 3 is conditional)
- Hardware enabling NMP ≥ 0.1 and spatial range ≥ 20 bins (criterion 4 blocked)

The conditional survivor P3 is important: it is the only C2 prediction that
asks a question conventional physics cannot answer in advance. But it cannot
be executed under current conditions, and its discriminating power is not
guaranteed even if executed.
