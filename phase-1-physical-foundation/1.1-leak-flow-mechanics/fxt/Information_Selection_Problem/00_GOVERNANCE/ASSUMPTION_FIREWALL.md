# ASSUMPTION_FIREWALL
## Explicit Register of Forbidden Assumptions

---

### Purpose

This document lists assumptions that are **prohibited from entering any derivation** in this workspace, regardless of the name used.

The firewall exists because the primary failure mode of the predecessor project (C2 / SXC-IGC) was **assumption laundering**: introducing the desired conclusion under a new name as a premise, then claiming to have derived the conclusion. The most dangerous form was:

> Define a "primitive" whose properties encode the target behavior, then "derive" that the target behavior follows.

For the cosmological initial-state problem, the specific dangerous version is:

> Derive W_μνρσ ≈ 0 by secretly assuming homogeneity/isotropy/FLRW.

---

### Section A: Geometric/Cosmological Assumptions

The following assumptions are **prohibited as inputs** to any derivation whose goal is to explain the early cosmological state. They may appear as **outputs** only if derived from independent premises.

| Prohibited Assumption | Prohibited Synonyms / Disguises |
|---|---|
| Homogeneity of the early universe | "uniform distribution," "translation-invariant state," "spatially averaged initial condition" |
| Isotropy of the early universe | "rotationally symmetric state," "no preferred direction," "SO(3)-symmetric initial condition" |
| FLRW metric as the physical metric | "background metric," "zeroth-order geometry," "unperturbed spacetime" |
| Low Weyl curvature as an input | "gravitational entropy is low," "Penrose condition satisfied," "Weyl = 0 initial condition" |
| Any prescribed cosmological boundary condition | "the universe started in state X," "initial condition at t=0 is..." |
| The scale factor as given | "a(t) as background," "expanding universe as context" |
| Thermodynamic equilibrium at t_recombination | "matter was thermalized," "Maxwell-Boltzmann distributed matter" |

**Test for violation:** Can an adversarial mathematician construct a wildly inhomogeneous, anisotropic, high-Weyl-curvature spacetime that satisfies the proposed primitive? If yes, the primitive has not performed the required selection — and any "derivation" of the smooth early universe from it was assumption laundering.

---

### Section B: Information-Theoretic Assumption Laundering

The following patterns are specifically prohibited. Each is a known disguise for inserting the conclusion as a premise.

| Prohibited Pattern | Example of Violation |
|---|---|
| Define an "information capacity" that is maximized by homogeneous states | "bounded realizability ⇒ homogeneous state" (if homogeneity is encoded in the definition of bounded realizability) |
| Define an "information saturation" that selects FLRW geometry | Any definition of saturation whose boundary conditions already require FLRW |
| Claim entropy suppression by defining entropy so it is low for smooth states | Gravitational entropy definitions that encode smoothness as low-entropy by construction |
| Assume information-theoretic equilibration requires spatial homogeneity | Without deriving this from a substrate-independent theorem |
| Use "maximum entropy principle" applied only to matter, ignoring gravitational degrees of freedom | This selects thermal matter but leaves gravitational DOF unconstrained |

---

### Section C: Known Literature Failure Modes (from `fxt/` Catalog)

The following failure modes are documented in the predecessor project. Each is prohibited from recurring under a new name.

| Failure Mode | Source File in `fxt/` | Prohibition |
|---|---|---|
| Starting from decoherence and promoting to cosmological selection | `DECOHERENCE_ROLE_AUDIT.md` | Decoherence is a local quantum process. It does not select cosmological initial states. |
| Identifying an effective interaction and calling it a substrate | `SUBSTRATE_CANDIDATE_AUDIT.md` | Effective interactions are not fundamental substrates. |
| Introducing a transport law and calling it a prediction | `TLS_SUBSTRATE_DERIVATION.md` | A transport law must be derived, not postulated, and must be falsifiable. |
| Retrofitting an information interpretation after the observable fails | `FINAL_DISTINCTIVENESS_DECISION.md` | If the physics fails, reinterpreting it informationally does not rescue it. |
| Extending ontology after original prediction fails | `THEORY_EXTENSION_GATE.md` | Extension after failure is a rescue operation, not a prediction. |
| Underdetermined parameter masking the theory | `C2_PARAMETER_IDENTIFIABILITY_FINAL.md` | Parameters without independent determination are not predictions. |
| Assuming W=0 to derive W=0 | `FOUNDATIONAL_REASSESSMENT/00_FOUNDATIONAL_REASSESSMENT.md` | This is circular. The derivation must work without the conclusion as input. |

---

### Section D: The Assumption Audit Protocol

Before any step in a derivation is accepted, apply the following tests:

**Test 1 — Provenance check:**
Where does each input to this step come from? Is it an empirical observation, an established theorem, an experimental result, or a physical constant? If it is a postulate, what is its justification, and does the justification encode the target conclusion?

**Test 2 — Adversarial substitution:**
Replace the assumed state with a maximally pathological alternative (maximally anisotropic, maximally inhomogeneous, maximally high Weyl curvature). Does the derivation still produce the same "selection"? If yes, the primitive selected nothing. If no, identify exactly which step the pathological state fails, and confirm that step is independently justified.

**Test 3 — Name independence:**
Does the derivation work if all names are replaced with abstract symbols (Primitive P has property Q)? If the derivation requires the reader to interpret P as "information" to understand why Q implies the target behavior, then P was not derived to have that connection — it was assumed.

**Test 4 — Competitor universality:**
Does the proposed primitive also hold in a wildly different, non-cosmological setting? If the primitive is supposed to be general, it must apply outside cosmology. If it only appears in cosmological contexts, it is a restatement of the cosmological initial condition, not an explanation of it.

---

### Section E: Permitted Inputs

The derivation is permitted to use:

- Established mathematical structures (differential geometry, measure theory, information theory, functional analysis, probability theory)
- Experimentally supported physical constants (c, ℏ, G, k_B, etc.)
- Generally accepted physical principles (conservation laws, thermodynamic laws, causality, unitarity)
- Observational data (CMB measurements, large-scale structure surveys, BBN abundances)
- Logical constraints (mathematical theorems, consistency requirements)
- Information-theoretic theorems (Shannon's theorem, data processing inequality, etc.)
- GR and QFT where applicable, as established frameworks
- Confirmed predictions of the standard cosmological model (these define what needs to be reproduced)

---

*Document status: ACTIVE FIREWALL*
*Any step in any derivation that violates this firewall must be flagged, halted, and redesigned.*
