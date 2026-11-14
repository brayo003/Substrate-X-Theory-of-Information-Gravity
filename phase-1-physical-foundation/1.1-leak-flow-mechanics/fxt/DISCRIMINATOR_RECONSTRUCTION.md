# DISCRIMINATOR_RECONSTRUCTION.md
## Only Predictions Surviving Conventional-Equivalence Analysis

**Date:** 2026-08-22
**Method:** Take every C2 prediction from PREDICTION_LADDER.md and test it
  against the strongest physically plausible conventional null. Retain only
  predictions that a conventional mechanism cannot generically reproduce.
**Sources:** THEORY_EXTENSION_SEARCH.md, PREDICTION_LADDER.md,
  CONVENTIONAL_EQUIVALENCE_AUDIT.md, ADVERSARIAL_NULL_AUDIT.md

---

## The Four-Criterion Filter

A prediction survives only if it passes ALL of:

1. DERIVABLE from C2 (not assumed post-hoc)
2. QUANTITATIVELY CONSTRAINED (not a free-parameter shape fit)
3. NOT REPRODUCED by a physically plausible conventional mechanism
4. MEASURABLE IN PRINCIPLE

---

## Candidate 1: Lorentzian Temporal PSD

**C2 prediction:** S_JJ(ω) = 2S₀τ_B / (1+ω²τ_B²)
**Conventional null:** Any OU bath with same amplitude and τ_B gives identical S(ω).
**Criterion (3): FAIL.** Fully reproduced by conventional OU bath.
**Status: REJECTED.**

---

## Candidate 2: ω_rot² Ramsey Scaling

**C2 prediction:** Γ_φ(ω_rot) = k_rot · ω_rot²
**Conventional null:** Any bath with finite PSD at ω_rot and rotating-frame coupling
  geometry gives the same ω_rot² dependence (filter function argument).
**Criterion (3): FAIL.** Fully reproduced.
**Status: REJECTED.**

---

## Candidate 3: Gaussian Non-Markovian Onset

**C2 prediction:** W(t) ≈ exp(−Γt − Gt²/2) for t ≪ τ_B
**Conventional null:** Any finite-memory Gaussian bath gives this universal
  short-time behavior. It is the Kubo cumulant expansion to second order.
**Criterion (3): FAIL.** Universal for any Gaussian bath.
**Status: REJECTED.**

---

## Candidate 4: K₀ Spatial Shape (current hardware)

**C2 prediction:** C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c)
**Conventional null:** M7 power-law (FP=19.7%), M9 two-bath (FP=15.3%) — both
  physically motivated for SC qubits. Shape distance from power-law = 0.073,
  SNR ≈ 2. Adversarial null family defeats this test on 11-bin geometry.
**Criterion (3): FAIL on current hardware.** Shape degenerate with M7/M9.
**Status: REJECTED (current hardware). Conditionally revisable with ≥20 bins spanning 0.1–10 ξ_c.**

---

## Candidate 5: T₂ ≤ 2T₁ Structural Bound

**C2 prediction:** T₂ ≤ 2T₁ [DERIVED from telegrapher decay structure]
**Conventional null:** This is the standard quantum channel bound derivable from
  Lindblad structure alone. Not substrate-specific.
**Criterion (3): FAIL.** Standard quantum channel result.
**Status: REJECTED.**

---

## Candidate 6: Causal Wavefront Propagation

**C2 prediction:** C_Γ(r,t) = 0 for t < r/c (telegrapher causality).
  Correlations between qubits at separation r cannot be established before
  t = r/c.
**Conventional null A (diffusion bath):** Diffusion has no wavefront — correlations
  are formally non-zero at all t > 0. C2 DISCRIMINATES from diffusion.
**Conventional null B (phonon bath):** A phonon-mediated decoherence model also
  has a causal wavefront at t = r/v_s. Under Extension A (c = v_s), C2 predicts
  the same wavefront as the phonon bath.
**Criterion (3):**
  - vs. diffusion: PASS (telegrapher has wavefront, diffusion does not)
  - vs. phonon bath: FAIL (phonon bath has same wavefront)

**Net verdict:** The causal wavefront discriminates C2 from diffusion-type baths
but NOT from phonon baths. Since phonon baths are physically more motivated for
SC chips than pure diffusion, this is only a weak discriminator.

The discrimination requires measuring the ONSET TIME of spatial correlations —
a time-resolved two-qubit correlation measurement with sub-microsecond resolution.
For c = v_s = 6000 m/s and qubit separation r = 1 mm:
  t_onset = r/c = 1×10⁻³ / 6×10³ ≈ 0.17 µs

This is within the T₂ window but requires fast time-resolved measurement.

**Criterion (4): MEASURABLE IN PRINCIPLE** — requires time-resolved joint Ramsey
measurement with ns-scale time steps and qubit separations 1–10 mm.

**Status: CONDITIONALLY SURVIVING — vs. diffusion-type null only.**
Not a GENUINE DISCRIMINATOR vs. phonon bath under Extension A.

---

## Candidate 7: P3 Self-Consistency with Anomalous c

**C2 prediction:** c = ξ_c/(2τ_B) = constant across experimental conditions.
**Derivation:** Exact (ξ_c = v/λ, τ_B = 1/(2λ) → ξ_c/(2τ_B) = v = c).
**Quantitative constraint:** Once c is measured at one condition, all future
  measurements must give the same ratio.
**Conventional null:**
  - If c_measured ≈ v_sound (Si): consistent with phonon bath. NOT DISCRIMINATING.
  - If c_measured ≈ c_EM: consistent with EM coupling. NOT DISCRIMINATING.
  - If c_measured ≪ v_sound (e.g., 10–500 m/s): no conventional mechanism predicts
    a persistent velocity-linked spatial-temporal correlation at this speed.
    GENUINELY DISCRIMINATING.

**Criterion (2):** YES — once c is measured, subsequent predictions are constrained.
**Criterion (3):** CONDITIONAL — only if c_measured is anomalous.
**Criterion (4):** BLOCKED on current hardware (NMP = 0.033, need ≥ 0.1).

**Status: CONDITIONALLY SURVIVING — the only prediction that could be genuinely
discriminating, but only if the measured c is anomalous, which the theory cannot
predict in advance.**

---

## Candidate 8: Material-Dependent ξ_c [Extension A only]

**C2 prediction (Extension A):** ξ_c(material) = 2·v_s(material)·τ_B
  → ξ_c(Si)/ξ_c(Nb) = v_s(Si)/v_s(Nb) ≈ 6000/3480 ≈ 1.72

**Conventional null:** A conventional acoustic phonon bath with the same coupling
  geometry also predicts ξ_corr ∝ v_s(material). The material scaling is a
  property of phonon propagation, not uniquely of C2.
**Criterion (3): FAIL.** Phonon bath gives same material scaling.
**Status: REJECTED (conventional phonon phenomenology).**

---

## Candidate 9: Frequency-Independent Spatial Kernel

**C2 prediction:** At every qubit, S_JJ(ω) is a SINGLE Lorentzian (one τ_B, one
  spatial scale ξ_c). A two-bath model (M9) has TWO temporal scales at each qubit.

The test: measure S_JJ(ω) per qubit and determine whether it is fit better by
  one Lorentzian or two Lorentzians.

**Conventional null:**
  - M2 (single OU bath): IDENTICAL to C2 temporal spectrum. NOT DISCRIMINATING.
  - M9 (two-bath): has two Lorentzian components. C2 discriminates FROM M9.
  - Real qubits: noise spectra on IBM chips are known to have multiple
    components (1/f background + Lorentzian peaks from TLS). Multiple Lorentzian
    components are common. A single Lorentzian is a simplified model.

**Criterion (3): PARTIALLY.** C2 is discriminable from M9 on temporal structure,
  but not from M2 (single OU bath). Since M2 is in the adversarial null family
  and is physically plausible, this does not constitute a full discriminator.

**Status: WEAK — discriminates from M9 but not from M2.**

---

## Candidate 10: Non-Gaussian Spatial Statistics

**C2 prediction:** None. The PRW substrate generates Gaussian statistics (linear
  coupling H_int = g·J·σ_z, and J is a Gaussian process from linear PRW dynamics).
  All n-point correlations factorise (Wick's theorem).

**Status: NOT A DISCRIMINATOR — Gaussian substrate predicts Gaussian statistics
  identical to any Gaussian bath.**

---

## Summary: All Candidates

| # | Prediction | Derivation | Conventional null | Survives? |
|---|-----------|-----------|------------------|-----------|
| 1 | Lorentzian S_JJ(ω) | DERIVED | OU bath identical | NO |
| 2 | ω_rot² Ramsey | DERIVED conditional | Rotating-frame bath | NO |
| 3 | Gaussian NM onset | DERIVED | Any Gaussian bath | NO |
| 4 | K₀ spatial shape | DERIVED partial | M7/M9 degenerate | NO (current HW) |
| 5 | T₂ ≤ 2T₁ | DERIVED | Standard QC bound | NO |
| 6 | Causal wavefront | DERIVED | Phonon bath same | WEAK (vs diffusion only) |
| 7 | P3 anomalous c | DERIVED | None if c ≪ v_s | CONDITIONAL |
| 8 | Material ξ_c scaling | THEORY EXT | Phonon bath same | NO |
| 9 | Single Lorentzian | DERIVED | M2 identical | WEAK (vs M9 only) |
| 10 | Non-Gaussian stats | N/A | Not predicted | N/A |

---

## The Two Surviving (Weak) Candidates

### Survivor 1: Causal Wavefront (vs. diffusion)

**What it tests:** Whether decoherence correlations propagate with a sharp
  causal front (telegrapher) or spread instantaneously (diffusion/OU).

**Why it is weak:** Phonon baths also have causal fronts. This only discriminates
  C2 from diffusion-type conventional models — not from phonon bath models,
  which are more physically relevant for SC chips.

**Observable:** Time-resolved onset of spatial decoherence correlation.
  Measure C_Γ(r, t_wait) as a function of wait time t_wait.
  Telegrapher: C_Γ(r, t) = 0 for t < r/c; phonon bath: same.
  Diffusion bath: C_Γ(r, t) > 0 for all t > 0 (exponentially small but nonzero).

**Discriminating only against:** Diffusion-type (OU, 1/f) noise models.
  NOT against: phonon bath, EM coupling.

### Survivor 2: P3 Anomalous Speed (conditional)

**What it tests:** Whether the ratio c = ξ_c/(2τ_B) is anomalously slow,
  inconsistent with any known conventional propagation mechanism.

**Why it is conditional:** If c ≈ v_s (phonon speed), no discrimination.
  Only if c ≪ v_s is the result genuinely anomalous.

**Observable:** Both ξ_c (spatial) and τ_B (temporal) must be independently
  measured, then c computed. Requires NMP ≥ 0.1 and spatial range 0.1–10 ξ_c.

**Currently blocked:** NMP = 0.033 on Brisbane. Hardware gap remains.

---

## Conclusion

**Zero unconditional surviving discriminators.**

**Two conditional/weak survivors:**
1. Causal wavefront: discriminates from diffusion only (weak, not vs phonon bath)
2. P3 anomalous c: discriminates if and only if c_measured ≪ v_s (not predictable from theory)

**The strongest available discriminator remains P3**, and it requires hardware
conditions and theoretical closure (identification of why c would be anomalous)
not currently available.

Under Extension A (c = v_s), even P3 becomes non-discriminating.
The discriminators identified here do not survive Extension A.

**If Extension A is the only available extension, the conclusion is:**
C2 produces CONVENTIONAL PHENOMENOLOGY — predictions equivalent to a 2D
acoustic phonon bath with telegrapher (not diffusion) propagation dynamics.
That is a scientifically valid and testable model, but it is NOT a
GENUINE DISCRIMINATOR for the SXC-IGC ontology.
