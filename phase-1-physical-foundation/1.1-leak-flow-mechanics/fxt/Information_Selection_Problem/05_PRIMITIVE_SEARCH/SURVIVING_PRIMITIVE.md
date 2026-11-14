# SURVIVING_PRIMITIVE
## Gate 5 — The Primitive That Survives Kill Tests

---

### Purpose

Record which primitive(s) survive the kill tests and are cleared for derivation in `06_DERIVATION/`. This document is updated as kill tests are applied and candidates are resolved.

At program initialization, this document records the status as of the first pass through Gate 5.

---

## Section 1: Current Status

As of the first pass through Gate 5:

**Candidates A and B are conditional survivors.**
**Candidate D is an active speculative candidate.**
**Candidates C and E are killed.**

No candidate has yet been fully developed to the point of passing all five kill tests. This means:

**Gate 5 is not yet passed. No primitive is cleared for derivation.**

This is the correct and expected state at this point in the program. Gate 5 is a research gate, not a formality.

---

## Section 2: What Needs to Happen for Gate 5 to Pass

### For Candidate A (D-constraint) to fully survive:

Required: A background-independent mathematical criterion that defines the low-dimensional subspace of GR initial data without encoding smoothness in the definition.

Candidate criterion options:
- Minimum description length (Kolmogorov complexity) — but this is not computable; must find a computable analogue
- Spectral dimension of the initial-data manifold — requires a precise definition of spectral dimension for GR initial data
- Covariant entropy bound (Bousso) applied to the initial data — already assessed as insufficient alone (Candidate E killed)
- Renormalization group fixed point — the physical initial state lies on or near an RG fixed point of some relevant theory. This is background-independent and well-defined in QFT. Its extension to gravity is the outstanding question.

**Most promising option for A:** RG fixed point / asymptotic safety. The asymptotic safety program (Reuter et al.) proposes that GR has a UV fixed point. Initial states near this fixed point might be required for UV completion. This does not assume FLRW. This is a live candidate.

### For Candidate B (Q-bound) to fully survive:

Required: Specification of what physical system and measurement protocol defines the Fisher information bound.

Candidate specification:
- Fisher information of the metric field with respect to perturbations around a background: this is well-defined for linear perturbation theory but requires a background (potential circular)
- Quantum Fisher information of the cosmological quantum state (if a quantum cosmology framework is adopted): this requires specifying the quantum state, which is part of the initial-state problem
- Fisher information of the matter distribution: this is background-independent but may not constrain geometry

**Most promising option for B:** Quantum Fisher information in a specific limit of loop quantum cosmology or similar framework, where the quantum state of geometry is well-defined without assuming FLRW.

### For Candidate D (C-constraint) to develop:

Required: A calculation of the quantum channel capacity of the gravitational interaction as a function of spacetime curvature/complexity, showing that high-Weyl states have lower capacity or that a capacity bound restricts realized geometry.

This requires the quantum information/gravity channel literature (documented in ENTANGLEMENT_SPACETIME.md) and extension to the pre-inflationary regime.

**This is the most technically demanding candidate but potentially the most powerful — it would connect both research branches.**

---

## Section 3: The Merged Candidate (If Derivation Forces It)

It is possible that the eventual surviving primitive is not one of A, B, or D alone, but a combination: for example, a condition that restricts the Fisher information of a quantum geometric state to values consistent with the channel capacity bound.

This is speculative at this stage. The derivation must come first. Naming or characterizing the merged structure before the derivation is the assumption-laundering error.

---

## Section 4: Kill Conditions for This Document

This document is killed (program terminated) if:
- All candidates A, B, D are killed by further adversarial tests
- A candidate passes all tests but reduces to an existing proposal (no-boundary, July 2026 paper) — then the program terminates because the residual was already addressed
- Gate 3 is re-evaluated and the residual R1 is found to be closed by an existing framework

---

## Section 5: Instructions for Future Work

When a candidate is fully developed and passes all five kill tests:
1. Record the mathematical definition of the primitive here
2. Record its provisional name (descriptive of mathematical properties, per ONTOLOGY_PROHIBITION §D)
3. Verify that ONTOLOGY_PROHIBITION.md does not prohibit the name
4. Proceed to 06_DERIVATION/STATE_SPACE.md

The primitive gets its name from what the derivation forces, not from what sounds appealing.

---

*Document status: PENDING — Gate 5 not yet passed; candidates A, B, D require further development*
*This document will be updated when a primitive clears all kill tests*
