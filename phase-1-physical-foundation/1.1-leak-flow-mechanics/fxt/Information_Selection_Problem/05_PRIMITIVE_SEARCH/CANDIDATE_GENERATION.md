# CANDIDATE_GENERATION
## Gate 5 — Generating Primitive Candidates

---

### Purpose

Generate candidate primitives that could close residual R1. Each candidate is stated in terms of its mathematical properties, not its presumed physical interpretation. Names are provisional and descriptive.

This document is strictly governed by ONTOLOGY_PROHIBITION.md and ASSUMPTION_FIREWALL.md. No candidate may assume what it is supposed to derive.

---

## Section 1: The Requirement

A candidate primitive must:
1. Be definable without assuming FLRW, homogeneity, isotropy, or low Weyl curvature
2. Restrict physically realizable configurations to a subset that includes the observed early universe
3. Be consistent with all established physics
4. Pass the adversarial substitution test: a wildly inhomogeneous spacetime must NOT satisfy the primitive unless independently justified
5. Be the minimum necessary structure — no larger than required

---

## Section 2: Candidate Class A — Constraint on State-Space Dimension

**Provisional name:** The D-constraint

**Mathematical description:** A condition that restricts the effective dimensionality of the physically accessible initial-data space. Instead of the full infinite-dimensional space of GR initial data, only initial data in a finite-dimensional (or measure-zero) subspace is physically realizable.

**Motivation:** The observed universe is extraordinarily well-described by ~6 ΛCDM parameters. This suggests the physical initial state lives in a vastly compressed subspace of all possible initial data.

**Adversarial test:** Can an inhomogeneous state lie in a low-dimensional subspace? In principle yes — one can define a low-dimensional manifold in configuration space that contains both smooth and inhomogeneous states. The constraint must specify WHICH low-dimensional subspace, and that specification must not encode smoothness.

**Status:** Candidate — requires mathematical development of which constraint defines the subspace.

---

## Section 3: Candidate Class B — Information-Geometric Bound on Initial Data

**Provisional name:** The Q-bound

**Mathematical description:** A bound on the Fisher information metric (or some information-geometric quantity) of the probability distribution over initial-data space. States with high information content (complex, inhomogeneous geometry) are excluded by the bound; states with low information content (smooth, compressible geometry) satisfy it.

**Motivation:** Fisher information is a well-defined mathematical object. An upper bound on it would restrict the space of realizable states. The smooth FLRW initial state has low Fisher information (it is highly compressible/regular).

**Adversarial test:** Does a wildly inhomogeneous state have high Fisher information? The answer depends on how Fisher information is defined for a spacetime geometry. This requires careful specification. The Cramér-Rao bound and the relation to quantum estimation theory may be relevant.

**Key danger:** The bound must not be defined in terms of FLRW quantities. It must be covariant and background-independent.

**Status:** Candidate — requires specification of what probability distribution Fisher information is computed over.

---

## Section 4: Candidate Class C — Realizability Constraint from Quantum Gravity

**Provisional name:** The R-condition

**Mathematical description:** A condition derived from the requirement that the initial state be quantum-mechanically realizable in a theory of quantum gravity — i.e., it must lie in the support of the quantum gravity wave function, whatever that is.

**Motivation:** If quantum gravity restricts which classical initial states are "semi-classical" (have large quantum probability), then the low-Weyl initial state may be selected because it corresponds to a saddle point or dominant contribution in the quantum gravity path integral.

**Relationship to existing proposals:** This is the line of thinking behind the no-boundary proposal. The R-condition is a generalized version that does not commit to Hartle-Hawking's specific path integral or boundary condition.

**Adversarial test:** The condition must be derivable without assuming FLRW. The no-boundary proposal fails this if its Euclidean saddle points are identified with FLRW geometries by construction.

**Status:** Candidate — overlaps significantly with the no-boundary program. Independent derivation required.

---

## Section 5: Candidate Class D — Channel Capacity Constraint on Gravity

**Provisional name:** The C-constraint

**Mathematical description:** A constraint derived from the quantum channel capacity of the gravitational interaction in the early universe. If the gravitational interaction can only support quantum information transfer up to a certain capacity, then the initial geometric complexity is bounded.

**Motivation:** The 2025–2026 quantum information/gravity literature establishes that the gravitational interaction has a specific channel capacity. If this capacity constrains the complexity of quantum states that can be produced by gravitational evolution, it may restrict the realizable initial states.

**Connection to second branch:** This is where the two research branches might naturally connect — but CHARTER rule applies: they must not be merged until a mathematical derivation shows they are related.

**Adversarial test:** Does a high-complexity (high-Weyl) initial state violate the channel capacity constraint? This requires deriving the channel capacity in terms of geometric quantities, which is not yet done.

**Status:** Speculative candidate — the connection between gravitational channel capacity and initial-state geometry is not established.

---

## Section 6: Candidate Class E — Covariant Entropy Bound Applied to Initial Data

**Provisional name:** The B-condition

**Mathematical description:** Apply the Bousso covariant entropy bound (S ≤ A/4G on null surfaces) to the initial state. Require that the initial state be consistent with entropy bounds on all null surfaces in the past of the observable universe.

**Motivation:** The holographic bound is an established result. If applied strictly to the initial state, it may constrain the information content of that state.

**Problem:** The Bousso bound is a bound on entropy, not a selection principle. It constrains what is physically allowed but does not select a unique initial state within the allowed region. It would need to be sharpened into a selection principle.

**Status:** Foundation for a candidate — requires extension from bound to selection.

---

## Section 7: Kill Conditions for Candidates

Each candidate is killed if:

| Kill condition | Applies to |
|---|---|
| The constraint encodes FLRW in its definition | All candidates |
| An adversarial inhomogeneous spacetime satisfies the constraint | All candidates |
| The constraint is equivalent to an existing proposal (no-boundary, Bousso bound) | All candidates |
| The constraint cannot be stated in background-independent language | A, B, C, D, E |
| The constraint is not derivable from permitted inputs | All candidates |

---

## Section 8: Status and Next Steps

All five candidate classes are at the stage of characterization, not derivation. Each requires:
1. A precise mathematical definition
2. Verification that the definition is covariant and background-independent
3. Adversarial substitution test
4. Proof (or disproof) that it closes R1

These are Gate 5 tasks. The surviving candidate(s) are the input to SURVIVING_PRIMITIVE.md.

---

*Document status: WORKING — candidate generation phase; derivations pending*
