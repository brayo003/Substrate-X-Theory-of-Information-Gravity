# 00_RESEARCH_STATUS.md
## Current Research Status of Substrate X Candidate (Giga)

**Date:** 2026-08-23
**Status:** ONTOLOGICAL INVESTIGATION STAGE
**Mandate:** Determine what mathematical structure can replace arbitrary constitutive freedom in X

**Previous status:** INITIAL FORMALIZATION STAGE (see 01–03 for full record)
**Previous verdict:** FAILS PREDICTIVE TEST (constitutive underdetermination; 5+ free parameters not derived from primitive constraints)
**Key finding from previous stage:** constraint ≠ geometry of constraint. The first was hypothesized; the second was supplied by hand. Field ontology cannot eliminate constitutive freedom. Transition relation ontology (Candidate III) is the primary new track.

---

## 1. Current Candidate Ontology

### Fundamental Hypothesis

Substrate X is an always-existing field whose local state is characterized not merely by a field value, but by the set of physically accessible transitions available to that state. Physical configurations constrain this set. X evolves through neighboring configurations, and a transition cannot simply terminate. When the current continuation becomes impossible, X must reorganize within the remaining allowed configuration space.

### Primitive Elements

**X (Substrate X):** An always-present informational field that represents the physical structure whose possible configurations generate distinguishability. X is not a fluid, not composed of particles, not a hidden material substrate.

**q(x,t):** The local X state - represents the current local configuration of X.

**C_X(x,t):** The locally available configuration space - the set of physically accessible X configurations at (x,t).

**K_X(q,x,t):** The locally admissible directions/transitions of X evolution - the set of allowed changes to q.

**P(x,t):** Physical configuration (mass, energy, force, etc.) that constrains X.

**H(t):** Retained X history - accumulated distinguishable consequences of previous physical configurations.

### Core Architecture

```
PHYSICAL WORLD
      │
      │ constrains
      ▼
┌─────────────────┐
│   X CONFIGURATION│
│     SPACE ΩX     │
└─────────────────┘
      │
  allowed states
      │
      ▼
X STATE EVOLUTION
      │
   ┌──────────┴──────────┐
   │                     │
propagation             memory
   │                     │
   ▼                     ▼
X-flow              persistence
   │
   ▼
effective geometry
   │
   ▼
matter dynamics
   │
   └──────────────┐
                  │
                  ▼
         new physical state
                  │
                  └──────→ X
```

---

## 2. Definitions

### Configuration Space

**Ω_X(x,t):** The set of locally accessible X configurations at point (x,t). This is the space of physically possible states, not the actual state.

### Admissible Transitions

**K_X(q,x,t):** The set of allowed directions in Ω_X that q can evolve through. K_X is a subset of the tangent space to Ω_X at q.

### Continuation Condition

**q̇(x,t) ∈ K_X(q,x,t):** The evolution of X must proceed through admissible transitions only.

### Viability Constraint

**q̇(t) ∈ K(q,t) ∀t:** A physically valid trajectory must satisfy the continuation condition at all times. When the preferred continuation becomes forbidden (q̇_preferred ∉ K), the system must find another admissible direction (q̇_actual ∈ K).

### Dimensional Reduction

**d_eff(x,t) = rank G_ij(x,t):** The number of independent accessible spatial degrees of freedom, where G_ij is a configuration-space metric. A dimensional transition is 3→2 when rank G: 3→2.

### Matter

**M_i = A_i[q]:** Matter is defined as a stable localized configuration of X. A particle would be q_particle(x,t) that persists under X dynamics.

### Information

**Provisional definition:** Information is a physically distinguishable difference in the state of X. X does not create information; physical events establish distinctions in X configuration.

---

## 3. Assumptions

### Primitive Assumptions (Not Derived)

**A1 (Existence):** X exists everywhere, independently of physical matter.

**A2 (Non-fluidity):** X is not a material fluid, not composed of particles, not an ether of tiny objects.

**A3 (Configuration Representation):** X state is characterized by the set of physically accessible transitions, not merely a scalar field value.

**A4 (Physical Constraint):** Physical configurations constrain the locally available X configuration space.

**A5 (Admissible Evolution):** X evolves only through admissible transitions (q̇ ∈ K_X).

**A6 (Continuation Principle):** X-flow cannot terminate locally. When the current mode of evolution becomes impossible, X must reorganize into another allowed configuration.

**A7 (Matter as Stable Configuration):** Matter is a persistent/stable localized X configuration.

### Provisional Mathematical Assumptions (To Be Tested)

**M1 (Two-Layer Structure):** X has two layers: actual state q(x,t) and admissible transition structure K(x,t).

**M2 (History Dependence):** K may depend on accumulated history: K(t) = K[q(t), H(t)].

**M3 (Metric Representation):** Dimensional reduction can be represented by rank reduction of a configuration-space metric G_ij.

**M4 (Reorganization):** When inward flow becomes impossible, X decomposes into radial + tangential components.

---

## 4. Candidate Primitive Constraints

### Constraint X1: Local Configuration Restriction

**Statement:** A physical interaction restricts the set of X configurations locally available to the system. X cannot evolve through configurations that are incompatible with the current physical state.

**Mathematical form:** P₁ ≠ P₂ ⇒ Ω_X(P₁) ≠ Ω_X(P₂) in general, where P denotes physical configuration.

### Constraint X2: Admissible Evolution

**Statement:** X evolution must proceed through admissible transitions only.

**Mathematical form:** q̇(x,t) ∈ K_X(q,x,t)

### Constraint X3: Continuation Principle

**Statement:** X-flow cannot terminate locally. When the current continuation becomes impossible, X must reorganize into another allowed configuration.

**Mathematical form:** If q̇_preferred ∉ K, then q̇_actual ∈ K (some other admissible direction).

### Constraint X4: Dimensional Incompatibility

**Statement:** When configuration space becomes sufficiently constrained, the number of independently accessible spatial degrees of freedom may reduce.

**Mathematical form:** rank G: 3 → 2 under sufficient constraint.

---

## 5. Mathematical Structures Considered

### Tested/Under Consideration

**Structure A: Manifold of local field states**
- Status: Primary candidate for Ω_X
- Reason: Natural mathematical structure for configuration space

**Structure B: Tangent-space constraint**
- Status: Used for K_X definition
- Reason: Natural representation of allowed directions

**Structure C: Set-valued dynamical system**
- Status: Possible representation for non-deterministic choice
- Reason: K_X may have multiple admissible directions

**Structure D: Constrained phase space**
- Status: Rejected as too specific
- Reason: Implies Hamiltonian structure not yet established

**Structure E: Fiber bundle over physical spacetime**
- Status: Under consideration
- Reason: Could naturally separate configuration space from base space

**Structure F: Graph/network of allowed local transitions**
- Status: Possible discrete representation
- Reason: May be useful for discrete transition structure

**Structure G: Distribution/subbundle defining allowed directions**
- Status: Primary candidate for K_X
- Reason: Natural continuous representation of admissible transitions

**Structure H: Configuration-space metric G_ij**
- Status: Adopted for dimensional reduction analysis
- Reason: Provides mathematical definition of accessible directions

### Rejected Structures

**Tangent-space constraint alone:** Insufficient - does not capture that K itself changes with physical configuration

**Scalar field representation:** Too shallow - C2 limitation, cannot represent transition structure

**Markovian state-only representation:** Insufficient - history dependence may be essential

---

## 6. Structures Rejected and Why

**Rejection 1: Scalar density/current (C2 approach)**
- **Reason:** Too shallow, cannot represent that two states with same q can have different futures
- **Evidence:** The cheki.txt analysis showed this limitation

**Rejection 2: "X wants maximum configuration space"**
- **Reason:** Teleological, introduces unnecessary maximization principle
- **Replacement:** Viability/continuation constraint

**Rejection 3: "Gravity is simply X flowing inward"**
- **Reason:** Interpretation rather than derivation
- **Replacement:** Gravity as emergent from configuration constraint geometry

**Rejection 4: "2D contains no information"**
- **Reason:** Not established physics, unnecessary assumption
- **Replacement:** Dimensional reduction = reduction in independently accessible degrees of freedom

**Rejection 5: "Black holes contain no information"**
- **Reason:** Not something we can assume as axiom
- **Replacement:** At sufficient constraint, accessible configuration space may collapse in dimensionality or distinguishability (prediction to test)

---

## 7. The Minimal Mathematical Model

### Current Minimal Model

**State Space:**
- q(x,t) ∈ R^n (local X state, n to be determined)
- Ω_X(x,t) ⊆ R^n (locally accessible configuration space)
- K_X(q,x,t) ⊆ T_qΩ_X (admissible transition directions)

**Dynamics:**
```
q̇(x,t) ∈ K_X(q,x,t)
P(x,t) → Ω_X(x,t) [physical constraint]
K_X = K_X[q, P, H] [transition structure depends on state, physics, history]
```

**Continuation:**
- If q̇_preferred ∉ K_X, find q̇_actual ∈ K_X
- Simplest decomposition: q̇_actual = q̇_radial + q̇_tangential

**Dimensional Reduction:**
- G_ij(x,t) configuration-space metric
- d_eff(x,t) = rank G_ij(x,t)
- Transition: d_eff: 3 → 2 under sufficient constraint

**Matter:**
- M = A[q] where A represents stable localized configuration
- Stability mechanism to be determined (attractor, topological, nonlinear solution, etc.)

---

## 8. Exact Unresolved Variables

### Mathematical Quantities

**q(x,t):** Exact mathematical form and dimension n not yet determined

**Ω_X(x,t):** Exact mathematical structure not yet determined (manifold? fiber bundle?)

**K_X(q,x,t):** Exact functional form not yet determined

**G_ij(x,t):** Exact relation to q, P, H not yet determined

**H(t):** Exact representation of history not yet determined (kernel? geometric encoding?)

**A[q]:** Exact mapping from X state to matter configuration not yet determined

### Physical Quantities

**Relation between P (physical configuration) and Ω_X:** Constraint law not yet derived

**Relation between constraint strength and spatial range:** Not yet derived

**Mechanism for dimensional reduction:** Not yet derived beyond rank reduction

**Reorganization mechanism:** When continuation becomes impossible, exact rule for choosing new direction not yet determined

---

## 9. Exact Derivation Targets

### Target 1: Configuration Space Formalism

**Goal:** Develop rigorous mathematical formalism for q, C_X, K_X and continuation condition

**Success criteria:**
- Precise mathematical definitions of all objects
- Well-posed continuation condition
- Clear distinction between state and admissible transitions

### Target 2: Spherical Static Solution

**Goal:** Construct minimal isolated spherical X configuration

**Success criteria:**
- Stationary condition derived
- Radial behavior derived without assuming 1/r²
- Asymptotic behavior derived
- Effective force/acceleration if it emerges (not assumed)
- Attraction mechanism identified (if it exists)

### Target 3: Dimensional Reduction Mechanism

**Goal:** Derive dimensional reduction from microscopic rule

**Success criteria:**
- Mathematical mechanism for rank G: 3 → 2
- Condition under which this occurs
- Physical interpretation of threshold

### Target 4: Matter Stability Mechanism

**Goal:** Derive stable localized X configuration

**Success criteria:**
- Mathematical definition of "stable"
- Existence condition for stable localized solution
- Mechanism for persistence

### Target 5: Inverse-Square Behavior

**Goal:** Determine whether 1/r² emerges from microscopic rule

**Success criteria:**
- Either: derive 1/r² from microscopic constraint
- Or: show what radial law emerges instead
- Or: show that arbitrary constitutive freedom remains

---

## 10. Falsification Criteria

### Kill Test 1: Mathematical Inconsistency

**Criterion:** The primitive constraints lead to mathematical contradiction

**How to test:** Attempt to construct well-posed initial value problem; check for ill-posedness

### Kill Test 2: No Nontrivial Stable Localized Solution

**Criterion:** No stable localized solution exists under any parameter values

**How to test:** Solve for stationary solutions; analyze stability

### Kill Test 3: No Attractive Behavior

**Criterion:** No attractive force/acceleration emerges from spherical configuration

**How to test:** Compute effective force from radial solution; check sign

### Kill Test 4: Attraction Requires Inserted Newtonian Structure

**Criterion:** Attraction only appears if 1/r² or equivalent is manually inserted

**How to test:** Derive radial solution without any assumed force law

### Kill Test 5: Infinite Arbitrary Constitutive Freedom

**Criterion:** Infinitely many radial laws remain possible without additional constraints

**How to test:** Count degrees of freedom in radial solution

### Kill Test 6: No Natural Propagation Limit

**Criterion:** No finite propagation speed emerges from continuation principle

**How to test:** Analyze characteristic speeds in evolution equations

### Kill Test 7: No Coherent Dimensional-Reduction Mechanism

**Criterion:** Dimensional reduction requires additional ad hoc assumptions

**How to test:** Derive rank reduction from primitive constraints alone

### Kill Test 8: X Mathematically Redundant with Existing Theory

**Criterion:** X construction is mathematically equivalent to constrained field theory, nonlinear field theory, or other established framework

**How to test:** Compare structure with known theories (constrained dynamical systems, gauge fields, etc.)

### Kill Test 9: Matter and Gravity Require Unrelated Mechanisms

**Criterion:** Stable localized configurations and attractive geometry require different independent assumptions

**How to test:** Derive both from same primitive constraints

### Kill Test 10: Continuation Principle Does Not Actually Constrain Dynamics

**Criterion:** Continuation principle is either always satisfied or can be satisfied trivially

**How to test:** Analyze whether K_X constraint actually restricts q̇

---

## 11. Known Analogues in Established Physics

### Constrained Dynamical Systems

**Analogue:** Viability constraints in optimal control and biological systems

**Difference:** Our K_X is physically determined by P, not an optimization principle

### Fiber Bundles

**Analogue:** Gauge theories use fiber bundles over spacetime

**Difference:** Our fiber is configuration space, not internal symmetry space

### Phase-Space Reduction

**Analogue:** Symmetry reduction reduces phase space dimension

**Difference:** Our reduction is driven by physical constraint, not symmetry

### Non-Markovian Systems

**Analogue:** Memory kernels in generalized Langevin equations

**Difference:** Our memory is encoded in transition structure K, not force correlation

### Effective Geometry

**Analogue:** Induced metric in effective field theories

**Difference:** Our geometry emerges from configuration accessibility, not renormalization group flow

---

## 12. Explicit Separation

### Hypothesis

**H1:** X exists as an always-present field
**H2:** Physical configurations constrain X's locally available configuration space
**H3:** X evolves only through admissible transitions
**H4:** X-flow cannot terminate locally; must reorganize when continuation impossible
**H5:** Matter is a stable localized X configuration
**H6:** Strong gravitational configurations reduce accessible configuration space
**H7:** Dimensional reduction occurs under sufficient constraint

### Mathematical Consequence

**MC1:** q̇ ∈ K_X (continuation condition)
**MC2:** rank G reduction under constraint (dimensional reduction formalism)
**MC3:** Matter = A[q] (stable configuration representation)

### Empirical Constraint

**EC1:** Must reproduce Newtonian gravity at least approximately (or predict deviation)
**EC2:** Must allow stable matter configurations
**EC3:** Must have finite propagation speed
**EC4:** Must not contradict established physics

### Analogy

**A1:** Similar to constrained dynamical systems (viability constraints)
**A2:** Similar to fiber bundles (configuration space over spacetime)
**A3:** Similar to non-Markovian systems (history dependence)

### Speculation

**S1:** Black holes as phase transition in X (distinguishable → non-distinguishable)
**S2:** Outward expansion as reorganization response
**S3:** Quantum mechanics as emergent from X structure (not yet addressed)

---

## 13. Current Status

**Status:** INVESTIGATION COMPLETE — CANDIDATE III FORMALLY CLOSED

**Date of closure:** 2026-08-23

**All Giga documents:**
| Document | Finding |
|----------|---------|
| 01 | Field ontology: q(x,t), K_X formalism defined |
| 02 | Spherical static: a(r) ∝ r^{-(α/2+1)}, α free, 5+ free functions |
| 03 | Kill tests: candidate (field ontology) fails predictive criterion |
| 04 | Four ontological candidates: transition relation is primary track |
| 05 | 1D transition: composition + scale invariance → (r₁/r₂)^C, C free |
| 06 | 3D transition: dimension does not force C; conditional C=1 via flatness = known geometric gravity |
| 07 | Matter coupling: geodesic/parallel-transport structure in test-particle limit; all novel effects optional; no derived prediction |

---

## 14. Giga 07 Completed — Final Verdict

### Final Classification

    EQUIVALENT TO KNOWN PHYSICS

### Kill Test Summary (from 07_MATTER_COUPLING.md Section 14.4)

| Test | Description | Result |
|------|-------------|--------|
| K1 | Matter motion genuinely derived | CONDITIONAL (test-particle limit only; = geodesic) |
| K2 | WEP genuinely derived | CONDITIONAL (requires EP-equivalent axiom) |
| K3 | Mass genuinely derived | FAIL |
| K4 | Inertia genuinely derived | FAIL |
| K5 | Coupling contains irreducible X content | FAIL |
| K6 | Composition dependence forced | FAIL |
| K7 | Memory forced | FAIL |
| K8 | Memory cannot be absorbed into Markovian state | UNRESOLVED |
| K9 | Novel observable exists | FAIL |
| K10 | Novel observable survives removal of free parameters | FAIL |
| K11 | Collapse scale emerges internally | FAIL |
| K12 | Candidate not merely differential geometry | FAIL |

**PASS: 0 / CONDITIONAL: 2 / UNRESOLVED: 1 / FAIL: 9**

### Surviving Free Parameters

All of the following remain free — unconstrained by X primitives:

| Parameter | Status |
|-----------|--------|
| Radial exponent α | Free (conditional on path-independence axiom for α=1) |
| Mass coupling A(M) | Free |
| Definition / value of mass | Free (definition only) |
| Inertia | Free (or forced = Q[M] by EP analog) |
| Propagation speed | Free |
| Collapse scale | Free (requires G, c from outside) |
| Memory timescale τ_X | Free (not derived; not required) |
| Composition-dependent coupling | Free (not derived; not required) |

### Novel Observables

**None.** No experimentally distinguishable prediction has been derived that is
absent from standard Newtonian/relativistic gravitational physics.

### WEP Violation Status

**PERMITTED, NOT DERIVED.** WEP violations would follow if the parallel-transport
axiom is rejected AND if ΔR for distinct matter types is specified. Neither condition
is forced by X primitives. The violation magnitude is not calculable. The mechanism
has a structural equivalent in scalar-tensor gravity (Brans-Dicke type).

### Memory Correction Status

**PERMITTED, NOT DERIVED.** Non-Markovian corrections to geodesic motion would follow
if τ_X ≠ 0. τ_X is a free parameter. Setting τ_X = 0 recovers standard GR exactly.
The mechanism has a structural equivalent in non-local gravity theories. Whether the
specific X memory structure H(t) is irreducible with respect to Markovian enlargement
is UNRESOLVED but does not affect the novelty verdict (K7 already established memory
is not required).

### Candidate III Status

**FORMALLY CLOSED.**

Grounds: The full weak-matter transition structure of X is a principal SO(3) bundle
connection (standard differential geometry). Test-particle motion is geodesic motion.
WEP is the equivalence principle under a different name. No novel observable has
been derived. Both candidate novel effects are optional free parameters. The pattern
across Giga 01–07 demonstrates systematic convergence to standard differential
geometry because the primitive set (composition law = parallel transport rule) was
structurally identical to a bundle connection from the outset.

### Meta-Analysis Conclusion

The sequence Giga 01–07 demonstrates interpretation (ii): **systematic convergence
toward standard differential geometry because the chosen primitives contain
insufficient information to generate anything beyond it.**

The composition law R(x,z) = R(y,z)·R(x,y) is the definition of a connection.
Any theory built on this composition law will reproduce connection geometry. The
X formalism adds notation and motivation but not mathematical content beyond what
is already in the theory of principal bundles and their associated geodesic dynamics.

### What X Currently Explains or Predicts That Established Physics Does Not

**At present, nothing experimentally distinguishable has been derived.**

### Next Step

**No Giga 08 is required for Candidate III.** The candidate is closed.

If the X program is to continue, it requires a **new ontology** — one whose
primitives are not structurally equivalent to a connection on a bundle. Specifically:
any new candidate must have a primitive set that, when its mathematical consequences
are fully unpacked, produces structure that differential geometry does not contain.

Identifying such a primitive set is not a matter of further calculation within
the current framework. It requires a foundational reassessment of what X's
core intuition — the "continuation principle," the "configuration space," the
"distinguishability" concept — demands mathematically that goes beyond standard
geometric structure.

That reassessment, if undertaken, would be the subject of a new phase document
outside the Giga series.

---

*End of 00_RESEARCH_STATUS.md*
