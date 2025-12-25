# Phase 4 — Validation Protocol
Cognitive / Informational Interface (DCIF)

## Purpose

This document defines the mandatory validation procedure for any Phase 4
Cognitive / Informational Domain submitted under the SXC-IGC framework.

Passing this protocol is required for domain acceptance.
Failure at any stage constitutes rejection.

---

## 1. Required Inputs

Each candidate domain MUST provide:

1. A deterministic time series x(t)
2. Explicit parameters (r, a, b)
3. Measurement description for x(t)
4. A reproducible simulation or data pipeline

Stochastic-only models are not admissible.

---

## 2. Reduction Test

The domain must demonstrate reduction to the V12 core equation:

dx/dt = r·x + a·x² − b·x³

Procedure:
- Fit dx/dt numerically from x(t)
- Perform nonlinear regression against V12 form
- Extract (r, a, b)

Acceptance threshold:
- R² ≥ 0.95

---

## 3. Saturation Test

The system must demonstrate bounded behavior:

0 ≤ x(t) ≤ 1.5

Procedure:
- Run long-horizon simulation or observation
- Confirm absence of unbounded growth
- Identify saturation or collapse regime

Failure modes:
- Divergence
- Chaotic escape
- Undefined upper bounds

---

## 4. Determinism Test

Procedure:
- Run identical initial conditions ≥ 10 times
- Confirm trajectory convergence within tolerance

Acceptance:
- Variance → 0 as dt → 0

Domains requiring irreducible randomness are rejected.

---

## 5. Scaling Classification (α-Space)

Procedure:
- Evaluate stress vs integrity or equivalent variables
- Fit power-law scaling
- Extract domain-specific α

Notes:
- α = 1.254 is NOT required
- α-class separation is admissible and informative

---

## 6. Cross-Domain Consistency Check

If the same domain can be measured via multiple modalities:
- EEG vs MEG
- simulation vs empirical
- hardware vs software

Then (r, a, b) must remain consistent within error bounds.

---

## 7. Explicit Exclusions

The following invalidate a submission:

- Claims of consciousness or phenomenology
- Metaphysical explanations
- Undefined variables
- Narrative-only justification
- Failure to specify coefficients

---

## Outcome States

- ACCEPTED: Domain satisfies all criteria
- CONDITIONAL: Minor numerical issues, correct structure
- REJECTED: Structural or methodological failure

---

## Authority

This protocol operationalizes Phase 4 of the
Substrate X Theory of Information Gravity (SXC-IGC).

It enforces interface integrity.
It does not adjudicate meaning.

