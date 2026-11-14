# UNIQUE_PREDICTIONS
## Gate 7 — Predictions That Uniquely Identify the Framework

---

### Status Notice

**TEMPLATE — Gates 5 and 6 not yet passed.**

This file will record predictions that survive the null model tests and uniquely identify the framework. It is empty until derivation is complete.

---

## Section 1: The Prediction Requirement

A prediction qualifies as unique if it passes all tests in STANDARD_MODEL_NULL.md and ALTERNATIVE_THEORY_NULLS.md:
- Not reproducible by ΛCDM parameter tuning
- Not reproducible by any alternative theory in the null set
- In principle measurable with existing or foreseeable technology

---

## Section 2: Candidate Prediction Types (Pre-Derivation Guidance)

Based on the candidate primitives, the following types of predictions are most likely to be unique:

### Type 1 — Specific Relationship Between CMB Parameters

If the primitive constrains a relationship between two ΛCDM parameters that are otherwise independent (e.g., n_s and r are related through the primitive, not just through a specific inflation model), this would be a unique prediction.

**Why unique:** ΛCDM treats n_s and r as independent. Inflation models predict a relation (slow-roll approximation: n_s ≈ 1 - 6ε + 2η; r = 16ε), but different models give different curves. A primitive-derived relation would be model-independent and more fundamental.

### Type 2 — Specific Non-Gaussianity Signature

The primitive may predict a specific form or amplitude of non-Gaussianity (f_NL, g_NL) that differs from standard slow-roll inflation predictions.

**Why potentially unique:** Non-Gaussianity from slow-roll inflation is small. The shape of non-Gaussianity (equilateral, squeezed, folded) depends on the mechanism. A primitive that acts on the entire state space might produce a different shape.

### Type 3 — Specific Gravitational Wave Spectrum Feature

If the primitive modifies the pre-inflationary dynamics, it would alter the primordial gravitational wave spectrum at frequencies corresponding to pre-inflationary scales. These frequencies are accessible to future space-based detectors (BBO, LISA, DECIGO).

**Why potentially unique:** Standard inflation predicts a nearly scale-invariant tensor spectrum with amplitude r. Pre-inflationary modifications would add features at specific frequencies not predicted by any inflation model.

### Type 4 — Violation of Scale Invariance at Super-Horizon Scales

The primitive may impose a specific correlation structure at scales larger than the current Hubble horizon. These are observable in the low-ℓ CMB (the "lack of power" anomaly at ℓ < 10 is already observed and unexplained in ΛCDM).

**Why potentially unique:** If the primitive predicts the specific pattern of large-scale CMB anomalies, this would be a retroactive prediction of an already-observed anomaly.

---

## Section 3: The Prediction Register

*This section is populated when Gate 6 produces derivation results.*

| Prediction ID | Observable | Predicted value | ΛCDM prediction | July 2026 prediction | Distinguishable? | Measurable by |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

---

## Section 4: The Measurement Feasibility Check

For each unique prediction, the following must be assessed before Gate 7 passes:

1. **Is the prediction currently constrained?** If yes and the prediction is consistent with data, it is a postdiction (weak). If inconsistent, it is a falsification.
2. **Can the prediction be measured with current instruments?** (e.g., Planck, BICEP/Keck, SDSS)
3. **Can it be measured with near-future instruments?** (e.g., CMB-S4, Simons Observatory, LiteBIRD, LISA)
4. **Is the precision sufficient to distinguish the prediction from null models?**

---

## Section 5: What Constitutes Gate 7 PASS

Gate 7 passes when:
- At least one prediction is logged in Section 3
- That prediction is distinguishable from all null models
- That prediction is measurable (current or near-future technology)
- No existing measurement already falsifies the prediction

If Gate 7 passes, the program proceeds to `08_VERDICT/SURVIVAL.md`.

If Gate 7 fails (no unique prediction survives), the program records the failure and proceeds to `08_VERDICT/KILL.md`.

---

*Document status: TEMPLATE — awaiting derivation output from 06_DERIVATION/*
