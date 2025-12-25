# Contributing to Substrate X Theory of Information Gravity (SXC-IGC)

This repository is not an open-ended idea sandbox. Contributions are accepted only if they preserve mathematical coherence with the SXC-IGC V12 core.

---

## Core Requirement (Non-Negotiable)

Every new contribution that introduces a **Domain**, **Module**, or **Model** MUST explicitly reduce to the **V12 instability equation**:

dx/dt = r·x + a·x² − b·x³

with:

- Explicitly identified coefficients: (r, a, b)
- Demonstrated saturation behavior with hard bound: x ≤ 1.5
- Consistency with the stabilized scaling exponent: α = 1.254

Any submission that does not clearly specify its (r, a, b) coefficients will be rejected without review.

---

## What Constitutes a Valid Domain

A valid Domain must include:

1. A clear statement of what x represents (e.g. density, coherence, amplitude).
2. Identification of physical, informational, or cognitive meaning for:
   - r (growth / leakage term)
   - a (reinforcement / condensation term)
   - b (suppression / saturation term)
3. Numerical ranges or calibrated values for r, a, b.
4. A script or notebook demonstrating:
   - Stability
   - Saturation
   - Deterministic behavior under repeated runs

---

## Prohibited Contributions

The following will not be accepted:

- New equations that do not reduce to the V12 form.
- “Inspired by” models without coefficient mapping.
- Purely philosophical additions without mathematical grounding.
- Renaming or rebranding the V12 equation as a new discovery.
- Domains that rely on stochastic behavior without deterministic limits.

---

## Code Standards

- Python 3.x only unless explicitly justified.
- Deterministic execution required (random seeds fixed if used).
- Tests must pass existing validation scripts:
  - test_determinism.py
  - test_numerical_stability.py
  - test_coefficient_sanity.py

---

## Attribution and Priority

By contributing, you acknowledge that:

- The V12 instability equation
  dx/dt = r·x + a·x² − b·x³
- The scaling exponent α = 1.254
- The saturation bound x ≤ 1.5

are the primary discoveries of **brian 003** under the SXC-IGC framework.

Contributions extend the framework; they do not redefine its core.

---

## Submission Process

1. Fork the repository.
2. Add your Domain in the appropriate phase directory.
3. Include coefficient declaration and validation scripts.
4. Submit a pull request with a concise technical description.

Submissions failing the core requirement will be closed without further discussion.

