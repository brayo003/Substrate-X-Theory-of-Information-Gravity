# DERIVATION_REQUIREMENTS
## Gate 5 — Necessary Capabilities of Any Closing Primitive

**Status:** ONTOLOGY JUSTIFICATION PENDING — PRIMITIVE GENERATION AUTHORIZED
**Basis:** FINAL_GATE4_STATUS.md, Branch C determination

---

## The Surviving Residual (Precise Statement)

There is no derivation — in standard GR, quantum cosmology, cyclic models, or information theory — of why the gravitational degrees of freedom of the early universe occupied an extremely small region of their available phase space, independently of the assumption that they did.

The residual after ekpyrosis (the strongest existing mechanism) is specifically:

> Why was the pre-contraction state within the attractor basin — i.e., why was the initial Weyl curvature below the black-hole-formation threshold, and why did the requisite scalar field exist with the required potential?

---

## What the Missing Structure Must Do

The following requirements are expressed as capabilities, not as names or ontological types. The primitive is not yet named. These are the mathematical necessities.

---

### Requirement 1 — Phase-Space Restriction

The missing structure must generate a nontrivial restriction on gravitational initial-data phase space.

Formally: it must define or imply a subset Γ_phys ⊊ Γ_GR of the space of all GR initial data (h_ij, K_ij satisfying the constraint equations), such that Γ_phys has small measure in Γ_GR under any reasonable measure, and all elements of Γ_phys have small Weyl curvature.

This restriction must be derivable — not postulated — from the primitive's defining properties.

**What does NOT satisfy this requirement:**
- Restricting to the FLRW sector (assumes the conclusion)
- Asserting a boundary condition (relocates the question)
- Appealing to typicality without a derived measure (undefined)

---

### Requirement 2 — Background Independence

The restriction must be expressible in background-independent language. It must not require a pre-existing geometric background (FLRW, de Sitter, flat space) to be stated.

This rules out: any constraint defined in terms of "deviations from FLRW," "perturbations around a homogeneous background," or "distance from a maximally symmetric geometry."

**Test:** Can the constraint be evaluated for a completely general Riemannian 3-manifold (h_ij, K_ij) satisfying the GR constraint equations, without any reference to a background metric?

---

### Requirement 3 — The Adversarial Substitution Must Fail

Construct a maximally pathological initial data set: highly inhomogeneous (large spatial gradients in h_ij), large Weyl curvature, anisotropic (Bianchi IX or mixmaster-type). This configuration must NOT satisfy the primitive's defining condition.

If it does satisfy the condition, the primitive has not selected the smooth initial state — it has selected a class that contains both smooth and highly inhomogeneous states. That is not a restriction.

**The test is mandatory.** No candidate primitive proceeds to derivation without passing this test.

---

### Requirement 4 — No Assumption Laundering

The primitive must not encode the desired conclusion in its definition. Specifically:

The primitive's definition must not contain, explicitly or implicitly:
- Homogeneity
- Isotropy
- FLRW symmetry
- Low Weyl curvature
- Smooth geometry
- Small gravitational entropy (by any name)
- Near-equilibrium matter distribution

**Detection protocol (from ASSUMPTION_FIREWALL.md):** Replace all named concepts in the definition with abstract symbols. Ask: does the argument still go through? If the argument requires interpreting a symbol as "smooth" or "homogeneous" to see why it selects the target state, the definition launders the conclusion.

---

### Requirement 5 — Consistency with Established Physics

The primitive must be consistent with:
- General relativity in the classical limit
- QFT in the appropriate regime
- Thermodynamic laws
- Observational constraints (CMB, BBN, large-scale structure)

It must reproduce the standard post-inflationary cosmological evolution as a limit or approximation. Deviations from GR+ΛCDM are permitted only as subleading corrections (except at the specific epoch where the primitive is active) or as testable predictions.

---

### Requirement 6 — The Ekpyrotic Gap Must Be Addressable

The surviving residual (from the ekpyrotic audit) is: why was the pre-contraction state within the attractor basin? A successful primitive should either:

(a) Derive why a contracting scalar field with the required potential generically exists and is in the correct initial state — in which case it supplements ekpyrosis at the pre-contraction level.

(b) Provide a completely independent derivation of the low-Weyl initial state that does not require a slow-contraction phase at all.

Option (b) is stronger. Option (a) is sufficient if the scalar field's existence is independently motivated by the primitive.

---

### Requirement 7 — Independent Motivation

The primitive must have motivation independent of the desire to close R1. It must not be constructed specifically to close R1 and nothing else.

**Why this matters:** A primitive constructed for the sole purpose of closing R1 is a sophisticated form of assumption laundering. It names a new object, defines it to have exactly the properties needed to select smooth initial states, and then "derives" that smooth initial states are selected. This is the C2 failure mode applied at a higher level.

**The test:** Does the primitive have applications or consequences outside the cosmological initial-state problem? Does it make contact with established physics in non-cosmological contexts? If it has zero independent motivation and zero non-cosmological consequences, it is suspiciously tailored.

---

### Requirement 8 — Distinguishable Prediction

If the primitive succeeds in restricting Γ_phys, it must produce at least one prediction distinguishable from ΛCDM + inflation + ekpyrosis + standard cosmological model.

Candidates (from 07_DISCRIMINATION/UNIQUE_PREDICTIONS.md):
- A specific relationship between CMB parameters not reproduced by adjusting existing ΛCDM free parameters
- A specific non-Gaussianity signature with a particular shape (equilateral, squeezed, etc.) not produced by standard slow-roll inflation
- A specific feature in the primordial gravitational wave spectrum at pre-inflationary scales
- A specific pattern of large-scale CMB anomalies

No requirement specifies WHICH prediction — that is for derivation to determine. But if derivation produces no prediction distinguishable from existing theories, Gate 6 fails.

---

## What the Requirements Do NOT Specify

The requirements are intentionally silent on:

- The name of the primitive
- Whether the primitive is a field, a constraint, a symmetry, an information-theoretic quantity, or something else entirely
- Whether the primitive is classical or quantum
- Whether the primitive requires modification of GR's action or is an external selection principle

The primitive gets whatever mathematical status the derivation forces upon it. Naming it before derivation is prohibited (ONTOLOGY_PROHIBITION.md).

---

## Summary Table

| Requirement | What it rules out | What passes |
|---|---|---|
| 1 — Phase-space restriction | Assumptions of FLRW, boundary conditions, undefined typicality | A derived constraint on (h_ij, K_ij) |
| 2 — Background independence | Constraints defined relative to FLRW or any fixed background | Covariant, metric-independent conditions |
| 3 — Adversarial substitution | Primitives that permit highly inhomogeneous configurations | Primitives that provably exclude them |
| 4 — No assumption laundering | Definitions that encode smoothness under another name | Definitions with no hidden homogeneity/isotropy |
| 5 — Consistency | New physics that breaks GR/QFT in established regimes | Subleading corrections or predictions in specific epochs |
| 6 — Ekpyrotic gap | Primitives that only work post-contraction | Primitives addressing pre-contraction or all-epoch selection |
| 7 — Independent motivation | Primitives with no application outside R1 | Primitives with contact to established physics elsewhere |
| 8 — Distinguishable prediction | Primitives producing only ΛCDM-reproducible predictions | At least one novel, measurable prediction |

---

*Document status: ACTIVE — Gate 5 entry requirements established*
*Primitive generation is authorized to proceed from these requirements*
*No primitive name, type, or ontology is specified here*
