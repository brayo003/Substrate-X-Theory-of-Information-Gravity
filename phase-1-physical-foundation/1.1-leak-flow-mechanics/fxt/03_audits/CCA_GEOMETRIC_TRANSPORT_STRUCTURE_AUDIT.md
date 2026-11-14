# CCA_GEOMETRIC_TRANSPORT_STRUCTURE_AUDIT.md
## What Geometric and Transport Structure Is Uniquely Determined by CCA Axioms Ax1–Ax5?

**Date:** 2026-10-10
**Status:** COMPLETE with CORRIGENDUM (see §0 below)
**Validation:** `04_validations/cca_geometric_transport_verification.py` (V1–V14, all PASS)
**Stress test:** `04_validations/theorem_cut_stress_test.py` (Q1 FAIL — theorem too strong)
**Outputs:**
  `04_validations/outputs/cca_geometric_transport_verification.json`
  `04_validations/outputs/theorem_cut_stress_test.json`
**Sources:** `09_archived_tests/cca_foundation/cca_foundation_audit.md`,
  `01_foundations/C2_FOUNDATIONS.md` Subsystem 6, prior obstruction audits.

---

## 0. Corrigendum — Theorem CUT

> **Issued:** 2026-10-10, following independent challenge to the sufficiency claim.

The original statement of **Theorem CUT** in §5.2 of this document claimed that
SE1–SE4 are *necessary and sufficient* for a unique numerical propagation speed c.
That claim is **too strong**. The corrected analysis is below.

**The error:** Test V14 in the original verification script fixed specific numerical
values of `a` and `dt` inside the test code itself. This implicitly added a fifth
condition (SE5, scale anchoring). The test passed because SE5 was present — not
because SE1–SE4 alone suffice.

**The counterexample:** For any k > 0, the rescaling φ → kφ (equivalently a → ka)
satisfies SE1 (still a valid metric embedding), SE2 (ka is still equal in all
directions), SE3 (dt is unchanged), SE4 (single branch unchanged), but gives
c → k·c. Therefore SE1–SE4 admit a one-parameter family of distinct speeds.
Similarly, rescaling dt → dt/k satisfies SE1–SE4 but gives c → k·c.
The full freedom is a 2-parameter group: (a, dt) → (k_a·a, k_t·dt), giving
c → (k_a/k_t)·c. `[Q1 confirmed — status: FAIL for sufficiency claim]`

**Corrected Theorem CUT:**

> Let C be a CCA satisfying Ax1–Ax5, equipped with axioms SE1–SE4. Then for
> any choice of spatial step a₀ > 0 and time step dt₀ > 0, the propagation
> speed is uniquely c = a₀/dt₀. However, a₀ and dt₀ themselves are free
> parameters of the embedding — not determined by Ax1–Ax5 or SE1–SE4. A
> fifth condition **SE5** must supply the numerical values of a₀ or dt₀ (or
> their ratio c directly). **SE5 is always empirical.**

**What SE1–SE4 do fix (correctly):**
- The *form* c = a/dt (ratio of step length to step time): yes.
- The *uniqueness of c* given a fixed unit system: yes.
- The *numerical value* of c in m/s without external input: **no**.

**What SE5 looks like:** Any of the following constitute SE5:
- Identifying a with the qubit size r_q (empirical)
- Identifying dt with 1/ω_qubit (empirical)
- Identifying c with the acoustic phonon speed (empirical — this is the Gap 7
  identification the theory has been trying to derive)
- Measuring c directly via the P3 ratio ξ_c/(2τ_B) (empirical)

**SE5 cannot be derived** from Ax1–Ax5 or from SE1–SE4. It is always a
constitutive relation between the abstract CCA and the physical world.

**Implication for Gap 7:** Gap 7 requires not just SE1–SE4 but also SE5.
Since SE5 is always empirical, c will always be a *calibrated parameter* in
the theory unless a new principle derives the physical scale of the CCA
lattice (e.g., from the large-N conjecture or from a natural information-
theoretic length unit). The corrected Gap 7 question is:

> *Can SE5 — the scale-anchoring condition — be derived from a deeper
> principle within the theory, or is it always an external empirical input?*

**On the two senses of Theorem NU:**

1. *Representation-level non-uniqueness* (proved): the same abstract CCA admits
   embeddings with any positive real speed. This is Theorem NU + Q1 confirmed.

2. *Physical non-identifiability* (supported but not fully proved here): no
   physical prediction of the theory can select c without empirical calibration.
   This is supported by V13 (temporal PSD cannot distinguish c values) but
   requires additional argument for the spatial observable ξ_c: while ξ_c
   depends on c, measuring ξ_c requires an independent length scale, which
   itself needs SE5. The full physical non-identifiability claim is therefore
   consistent with the current results but not formally closed.

**The four-axiom SE1–SE4 results that survive the corrigendum:**
- Each of SE1–SE4 is individually necessary for uniqueness-of-ratio c = a/dt
  given a fixed unit system. `[Q2 confirmed]`
- SE1–SE4 together are sufficient for uniqueness-of-ratio given fixed units. `[Q3 confirmed]`
- All four are strictly necessary: removing any one breaks even ratio-uniqueness. `[Q2 confirmed]`

**The correction does not change the impossibility results** (V4, V5, V9, V12):
these are established on dimensional and algebraic grounds independent of scale.

---

**Outcome labels used throughout:**
- **(A) Uniquely determined** — follows from Ax1–Ax5 for every CCA satisfying the axioms
- **(B) Non-uniquely determined** — present in every CCA but can take multiple distinct values
- **(C) Requires additional input** — not available from Ax1–Ax5; minimal extra axiom identified
- **(D) Impossible** — logically incompatible with Ax1–Ax5

A rigorous non-uniqueness or impossibility result is not a failure; it establishes which
derivations are worth pursuing and which are provably blocked.

---

## 1. The Mathematical Object

A CCA is the tuple **(O, M, ⊗, ≤, †, ε)** with:

| Primitive | Type | Governing axiom |
|-----------|------|----------------|
| O | Finite set of objects | Ax1 |
| M | Morphisms, src/tgt ∈ O; **finite** hom-sets | Ax1 |
| ⊗ | Symmetric monoidal product on M | Ax1 |
| ≤ | Locally finite partial order on M | Ax2 |
| † | Involution M→M with m≤m' ⟹ m'†≤m† | Ax3 |
| ε | Map M→[0,1]; Σ_{m:A→B} ε(m) = 1 for each (A,B) | Ax4, Ax5 |

**What is structurally absent from the primitives:**
- No metric, distance function, or norm
- No spatial dimension or direction vectors
- No speed or time rate
- No real line ℝ (ε maps into [0,1] ⊂ ℝ, but ℝ itself is not a CCA object)
- No complex numbers ℂ

The rank function r(m) = length of the longest chain below m in (M,≤) is well-defined
(Ax2, locally finite), dimensionless, and integer-valued. It is the CCA's only internal
"clock." It is not a physical time.

---

## 2. Master Classification Table

| # | Target | Outcome | Verified by | Key reason |
|---|--------|---------|------------|-----------|
| 1 | Discrete causal order type | **(B)** | V1 | Multiple non-isomorphic CCAs all satisfy Ax1–Ax5 |
| 2 | Causal locality (finite intervals) | **(A)** | Ax2 direct | Local finiteness is Ax2 itself |
| 3 | Rank / causal depth | **(A)** | Th. 1.3 | Uniquely defined from (M,≤) |
| 4 | Propagation speed (m/s) | **(D→C)** | V5, V4, V14 | Rank dimensionless; speed requires metric; unique only under 4 extra axioms |
| 5 | Causal cones J⁺(m), J⁻(m) | **(A)** | V2 | Uniquely computed from partial order |
| 6 | Metric geometry | **(C)** | V4 | Infinitely many metrics consistent with any CCA |
| 7 | Topological / order dimension | **(B)** | Audit §7 | Order dimension defined but ≠ topological dim in general |
| 8 | Classical fields φ: M→ℝ | **(C)** | CCA-IMP-1 | Requires continuous M; M is finite |
| 9 | Continuum spacetime manifold | **(C)** | V6 | Same abstract poset → different limiting manifolds |
| 10 | Differential geometry | **(C)** | CCA-IMP-1 | Tangent spaces require ℝ^n locally |
| 11 | Discrete conservation laws | **(B)** | Th. 2.17 | Rank monotone + ε-normalization; multiple forms possible |
| 12 | Continuous Noether currents | **(C)** | Obst. 2.19 | Requires Lagrangian on smooth manifold |
| 13 | Probability | **(A—primitive)** | Ax4 | ε is an axiom, not derived; see caveat |
| 14 | Gibbs distribution | **(A)** | V3 | Unique given rank + β; β is free |
| 15 | Discrete master equation | **(A/B)** | V8 | Form unique per CCA; content varies across CCAs |
| 16 | Kinetic theory / phase space | **(C)** | Obst. 2.24 | Requires position × momentum structure |
| 17 | Discrete d'Alembertian | **(B)** | Conjecture 2.27 | Constructible from Ax2; convergence to □ unproved |
| 18 | Complex quantum amplitudes | **(C)** | Obst. 2.28 | ε ∈ [0,1] real; ℂ requires external enrichment |
| 19 | Quantum interference | **(D)** | V12 | Real ε ≥ 0 → destructive interference algebraically impossible |

---

## 3. Structures Uniquely Determined by Ax1–Ax5

### 3.1 Causal Locality

**Outcome: (A)**

From Ax2: every interval [m,m'] = {x: m≤x≤m'} is finite (local finiteness). Spacelike
separation is incomparability in (M,≤). No additional axiom needed.

### 3.2 Rank Function

**Outcome: (A)**

r(m) = max chain length below m in (M,≤) is well-defined by Ax2 (bounded chains).
It is a dimensionless non-negative integer. It is the unique internal "clock" of the CCA.

### 3.3 Causal Cones

**Outcome: (A)** — `V2 confirmed`

J⁺(m) = {m': m≤m'}, J⁻(m) = {m': m'≤m} are uniquely determined by (M,≤). No
additional axiom needed. This is the strongest positive result for spatial structure:
causal cones are present for free.

### 3.4 Shannon Entropy

**Outcome: (A)** — `V10 confirmed`

H(A) = −Σ_{s∈Hom(I,A)} ε(s) log ε(s) is a deterministic function of ε (Ax4). Uniquely
defined for every object A in every CCA.

### 3.5 Gibbs Distribution (form)

**Outcome: (A) with free parameter β** — `V3 confirmed`

The maximum-entropy distribution on Hom(I,A) subject to fixed mean rank is uniquely:
ε*(s) = Z⁻¹ exp(−β·r(s)). The proof uses only the Lagrange multiplier argument
applied to H(A) (Ax4) and r (Ax2) — fully internal to CCA.

**Caveat:** β is NOT fixed by Ax1–Ax5. The form is unique; its single free parameter β
(inverse temperature) is undetermined. Statistical mechanics in this sense is uniquely
generated, but without a temperature scale.

### 3.6 Discrete Master Equation (form)

**Outcome: (A) for a given CCA; (B) across CCAs** — `V8 confirmed`

For any CCA, T_{AB} = Σ_{m:A→B} ε(m) defines a stochastic matrix, and the evolution
p(t+1) = T·p(t) is a well-defined discrete master equation. The form is universal;
the content (T's eigenvalues, stationary distribution) varies with ε.

### 3.7 Automorphism Groups

**Outcome: (A)** — `V9 confirmed`

Aut(A) is a well-defined finite group with |Aut(A)| ≤ |Hom(I,A)|!. This is a direct
consequence of Ax1 (finite hom-sets).

**Critical consequence:** The Lorentz group SO(3,1) is an infinite Lie group. It cannot
equal Aut(A) for any finite CCA. This is CCA-IMP-2 confirmed by V9.

### 3.8 T-Parity of Net Transition Flux

**Outcome: (A) conditional**

Define the net flux from A to B: N(A→B) = Σ_{m:A→B} ε(m) − Σ_{m:B→A} ε(m).
From Ax3 (dagger reverses order): if ε(m) contributes positively to the A→B net flux,
then ε(m†) contributes positively to the B→A net flux. Therefore N(A→B) is odd under
the dagger involution.

This is the categorical-level precursor to J being T-odd. It is a statement about
net morphism counts, not about a spatial current field. The spatial current J(x,t)
requires additional structure (see §5.4).

### 3.9 Probability (as primitive, not derived)

**Outcome: (A) — but note: probability is assumed, not derived**

ε: M→[0,1] is Ax4. Discrete probability theory is thus available in every CCA.
This is not an "emergence" result — it is an axiom. A truly foundational theory
would need to derive probabilistic structure, not assume it. CCA does not achieve this.

---

## 4. Structures Present But Non-Unique

### 4.1 Discrete Causal Order Type

**Outcome: (B)** — `V1: explicit non-isomorphic examples`

Any locally finite partial order satisfies Ax2. The theory selects no particular
isomorphism class. Linear chains, diamonds, trees, and arbitrary finite Hasse diagrams
are all valid CCA causal orders. Multiple examples satisfying all five axioms
with non-isomorphic causal structures were constructed in V1.

The spacetime topology is not fixed by the axioms.

### 4.2 Order Dimension

**Outcome: (B)**

The order dimension dim_ord(M,≤) — minimum number of linear extensions whose
intersection equals ≤ — is well-defined from (M,≤). But CCAs with any order
dimension ≥ 1 satisfy Ax1–Ax5. The axioms do not select 3+1 dimensions.

### 4.3 Discrete Conservation Laws

**Outcome: (B)**

Rank is monotone along causal chains (non-decreasing) — an internal arrow of time.
The total weight per hom-set is conserved (Ax4). But different CCAs have different
conservation law structures. Multiple conserved quantities can be defined (any additive
automorphism-invariant quantity on O). The axioms do not uniquely select one.

---

## 5. Structures Requiring Additional Input

### 5.1 Metric Geometry

**Outcome: (C)** — `V4: explicit counterexample family`

**Proposition (metric non-uniqueness):** For any abstract CCA (O, M, ⊗, ≤, †, ε)
and any two distinct metrics d, d' on a set of positions {φ(A): A∈O} ⊂ ℝ^d,
both (CCA, d) and (CCA, d') satisfy Ax1–Ax5. Therefore the metric is not an
invariant of the CCA structure.

*Proof:* V4 constructs three distinct embeddings of the same 3-element linear chain
A < B < C, all satisfying Ax1–Ax5, with d(A,B)/d(A,C) taking different values.
The CCA axioms contain no distance-fixing clause. ∎

**Minimum additional axiom:** SE1 — a spatial embedding φ: O→ℝ^d. SE1 makes the metric
well-defined (as the Euclidean metric on the image of φ), but does not make it unique
(different φ give different metrics).

### 5.2 Propagation Speed

**Outcome: (D) from Ax1–Ax5 alone; (C) under additional axioms** — `V5 confirmed`

**Theorem NU (Non-Uniqueness of Speed):** For any CCA C satisfying Ax1–Ax5 and
any c > 0, there exists a metric embedding φ of C with lattice spacing a and
time step dt = a/c, making the propagation speed equal to c.

*Proof:* Choose any a > 0 and set dt = a/c. The map φ assigning positions at
multiples of a satisfies SE1. The CCA (O, M, ⊗, ≤, †, ε) is unchanged. ∎

This means every positive real number is a valid speed for any CCA — a complete
non-uniqueness result. The core reason is dimensional: the rank r(m) is a
dimensionless integer, and no combination of dimensionless integers produces
units of m/s without external length and time scales. `[V5: dimensional argument]`

**Theorem CUT (Conditional Uniqueness — CORRECTED; see §0 for corrigendum):**
Let C be a CCA satisfying Ax1–Ax5 and additionally SE1–SE4. Given specific numerical
values a₀ > 0 [m] and dt₀ > 0 [s], the propagation speed c = a₀/dt₀ is uniquely
computed from those values. However, a₀ and dt₀ are **free parameters** — not
determined by Ax1–Ax5 or SE1–SE4 alone. Rescaling (a, dt) → (k_a·a, k_t·dt) for
any k_a, k_t > 0 satisfies all four conditions while giving c → (k_a/k_t)·c.
A **fifth condition SE5** (scale anchoring) is required to fix the numerical value
of c in physical units. SE5 is always empirical.
`[T2, T3 in se_uniqueness_resolution.py: 9 distinct c values all satisfy SE1–SE4]`

*What SE1–SE4 do fix:* the form c = a/dt and uniqueness of c given a fixed unit
system. *What they do not fix:* the numerical value of a, dt, or c in SI units.

**None of SE1–SE4 follows from Ax1–Ax5. SE5 does not either.**

**What Theorem CUT establishes about Gap 7:** Gap 7 requires SE1–SE4 *plus* SE5.
SE5 is always a constitutive identification (e.g. a = r_qubit, dt = 1/ω_qubit,
or c = v_acoustic) — all empirical. Gap 7 is therefore not closable from within
the axioms. The question is whether SE5 can be derived from a deeper principle
(large-N conjecture, information-theoretic scale) or must be accepted as empirical.

### 5.3 Continuum Spacetime Manifold

**Outcome: (C)** — `V6: two explicit limiting manifolds from one poset`

The same 1D chain of n abstract CCA objects can be embedded with uniform spacing
(→ compact interval [0,1]) or with exponentially growing spacing (→ non-compact
interval [0,∞)), or as a fractal Cantor-like set. All embeddings give the same
abstract partial order; the continuum limit depends entirely on the chosen embedding
and limiting procedure, neither of which is in Ax1–Ax5.

**Minimum additional input:** An external convergence criterion (e.g., Gromov-Hausdorff
distance on the space of metric spaces, plus a density condition). These require metric
space theory as external input — they cannot be generated within CCA.

### 5.4 Transport Direction / Current J in >1D

**Outcome: (C)** — `V11: explicit 2D non-uniqueness`

For a 2D CCA with objects at grid positions and symmetric ε, the net directional
current can point in any direction consistent with boundary conditions. V11 shows
explicitly that the same (O, M, ≤, ε) on a 2×2 grid admits horizontal, vertical,
and diagonal net flux — all consistent with Ax1–Ax5.

**What this means:**

The scalar J = c(n⁺−n⁻) in 1D becomes the vector sum J = Σ_b c_b(n⁺_b−n⁻_b)ê_b in
higher dimensions. The direction set {ê_b} is a new model input not determined by
Ax1–Ax5. Specifying it requires either:
(i) an explicit list of allowed propagation directions (a new axiom), or
(ii) a symmetry argument deriving the direction set from the lattice geometry
(but the CCA has no lattice geometry until SE1 is added).

Furthermore, H_int = g·J·σ_z requires J to be a scalar at the qubit location.
In >1D, this requires choosing a projection direction n̂ — a second new parameter
not determined by any existing CCA axiom.

### 5.5 Complex Quantum Amplitudes

**Outcome: (C)**

ε: M→[0,1] is real. The replacement ε → ψ: M→ℂ (with |ψ|² = ε) is an external
enrichment. Once added, full finite-dimensional QM follows from the †-compact SMC
structure (Coecke-Abramsky, referenced in C2_FOUNDATIONS.md Theorem CCA-9). The
enrichment is the price — it is not forced by Ax1–Ax5.

### 5.6 Continuous Noether Currents

**Outcome: (C)**

Standard Noether's theorem requires (a) a Lagrangian on a smooth manifold, (b) a
continuous symmetry group. CCA has neither. Therefore exact continuous Noether currents
cannot emerge from Ax1–Ax5. A discrete CCA-internal analogue might be provable (every
ε-preserving autofunctor preserves H_c), but would produce a discrete conservation law
(outcome B), not a Noether current.

---

## 6. Impossible from Ax1–Ax5

### 6.1 Quantum Interference

**Outcome: (D)** — `V12 confirmed`

**Proof:** Destructive interference requires |ψ₁ + ψ₂|² < |ψ₁|² + |ψ₂|²,
i.e., 2Re(ψ₁ψ₂*) < 0. This requires complex amplitudes with a relative phase.
For real ε ∈ [0,1], all combination weights are non-negative sums; no cross term
can be negative. Destructive interference is algebraically impossible within Ax1–Ax5.

This is a hard impossibility. No additional real-valued axiom can produce it.
The only path to interference is ℂ-enrichment (outcome C for Target 18).

### 6.2 Exact Lorentz Symmetry

**Outcome: (D)**

The Lorentz group SO(3,1) is an infinite Lie group (uncountably many elements). By
Theorem 1.4 (Ax1 → finite automorphism groups, confirmed in V9), Aut(A) is finite
for every object A in every finite CCA. Therefore SO(3,1) ≠ Aut(A) for any A in any
finite CCA. Exact Lorentz symmetry is impossible.

Approximate Lorentz symmetry in an N→∞ limit remains a conjecture (Bombelli-Lee-Meyer-
Sorkin). That is an outcome (C) question, not (A).

---

## 7. Detailed Analysis: Speed and Transport

### 7.1 Why Rank Cannot Produce Speed

The rank r: M→ℕ₀ satisfies:
- Units: dimensionless (pure integer count)
- Physical interpretation: number of causal steps, not physical time

Speed c has units m/s. Any formula of the form c = f(r₁, r₂, ...) where f depends
only on integer ranks produces a dimensionless quantity — not m/s. To produce units
of m/s from integer ranks requires introducing two new scales: a length scale a [m]
and a time scale dt [s]. This is precisely SE1 + SE3. `[V5]`

### 7.2 The Four-Axiom Minimum (Theorem CUT)

The four axioms SE1–SE4 are individually necessary and jointly sufficient for unique c:

| Axiom | If removed | What fails |
|-------|-----------|-----------|
| SE1 removed | No spatial scale a; c = a/dt undefined | Non-uniqueness (V4, V5) |
| SE2 removed | a varies by direction; c_x ≠ c_y ≠ c_z | Transport anisotropy (V7) |
| SE3 removed | dt varies per morphism; c varies along chain | Non-uniform speed |
| SE4 removed | Multiple branch lengths a_b; multiple c_b | Multi-branch Drude equivalence (V13) |

V14 explicitly verifies: with all four, c is unique; removing any one breaks uniqueness.

### 7.3 Correspondence with Existing Postulates

The existing PRW postulates A-PRW1–3 implicitly substitute for SE1–SE4:

| Existing postulate | Equivalent SE axiom(s) |
|-------------------|----------------------|
| A-PRW1: v and λ constant | SE2 (isotropy) + SE3 (uniform dt) |
| A-PRW2: fixed step Δx, Δt | SE1 (spacing a) + SE3 (time step dt) |
| A-PRW3: Markovian | Auxiliary condition (not in SE1–SE4) |

The A-PRW postulates were adopted without deriving them from CCA. Theorem CUT now
makes explicit what they were doing: substituting for the metric embedding axioms.

### 7.4 Transport Direction Non-Uniqueness in >1D

In 1D, the solenoidal ambiguity is absent (in 1D, any divergence-free current K must
be constant; if K = 0 at boundary, K = 0 everywhere). J is unique.

In d ≥ 2 dimensions: J' = J + K with ∇·K = 0 satisfies continuity for any K. The
CCA axioms, even with SE1 added, do not specify K — the direction set {ê_b} of
propagation branches must be given explicitly. This is a new degree of freedom
that does not appear in 1D and is not generated by any combination of Ax1–Ax5 with SE1.

This is the precise categorical statement of why multi-dimensional transport is more
underdetermined than 1D transport, and why the open problem in C2_FOUNDATIONS.md
("multi-dimensional generalization of the PRW") cannot be resolved without additional
axioms.

---

## 8. Implications for the Project

### 8.1 Gap 0 (Operational definition of J_C2)

| Sub-question | Outcome | Basis |
|-------------|---------|-------|
| Is J T-odd? | (A) conditional | Ax3 + net-flux interpretation |
| Is J unique in 1D? | (A) given SE1–SE4 | No solenoidal ambiguity in 1D |
| Is J unique in >1D? | (C) | Direction set {ê_b} is new input |
| What projection couples to H_int? | (C) | n̂ is a new free parameter |

The core residual gap in J_C2 is not T-parity (that is free). It is the direction
structure in higher dimensions: what is the geometry of the CCA embedding, and does
that geometry select a unique set of propagation directions?

### 8.2 Gap 7 (Unique propagation speed c)

Theorem NU proves the gap cannot be closed from within Ax1–Ax5.
Theorem CUT identifies the minimal closure: exactly 4 additional axioms (SE1–SE4).

Three paths forward:

1. **Accept SE1–SE4 as physical postulates.** This closes the gap pragmatically but acknowledges the speed is phenomenological, not derived. The theory is then self-consistent but not foundational at this level.

2. **Derive SE1 or SE2 from a deeper principle.** This is the genuine research question. A natural candidate: does some property of the information-theoretic structure of large CCAs (N→∞) force a preferred embedding? This connects to the large-N universality conjecture (OBS-C1 in C2_FOUNDATIONS.md Subsystem 8).

3. **Abandon the speed as a fundamental parameter.** The observables ξ_c = 2cτ_B and τ_B are independently measurable. If c is not derivable, the theory might be reformulated with {ξ_c, τ_B} as primitives instead of {c, λ}. The P3 discriminator c_eff = ξ_c/(2τ_B) then tests whether this ratio is orientation-independent — which is a genuine experimental question even if c is not derivable theoretically.

### 8.3 What Is Not Worth Pursuing

Given the impossibility results:
- Searching for c from rank alone: blocked by dimensional argument (V5)
- Deriving Lorentz symmetry from a finite CCA: blocked by finite automorphism groups (V9)
- Deriving quantum interference from real ε: blocked algebraically (V12)
- Proving J_C2 is uniquely fixed by continuity in >1D: blocked by solenoidal freedom (V11)

These derivations should not be attempted. The impossibility results are proofs, not
open problems.

---

## 9. Validation Summary

```
Command: python 04_validations/cca_geometric_transport_verification.py

V1  PASS  Non-isomorphic CCAs both satisfy Ax1–Ax5
V2  PASS  Future/past cones unique from partial order
V3  PASS  Gibbs unique given rank+β; β free
V4  PASS  Same CCA consistent with infinitely many metrics
V5  PASS  Rank (integer) cannot produce speed (m/s) — dimensional
V6  PASS  Same poset → different continuum limits (two explicit)
V7  PASS  SE1 gives speed definition; anisotropy breaks uniqueness
V8  PASS  Master equation unique per CCA; non-unique across CCAs
V9  PASS  |Aut(A)| finite; SO(3,1) excluded
V10 PASS  H(A) uniquely determined by ε
V11 PASS  2D CCA admits three distinct current directions
V12 PASS  Real ε ≥ 0 → destructive interference algebraically impossible
V13 PASS  Different v, same λ → identical S_JJ(ω) (GAP-7 structure)
V14 PASS  SE1+SE2+SE3+SE4 → unique c; removing any one breaks uniqueness
```

All 14 tests PASS. Each test verifies the tested mathematical property of the
explicit model implemented in the script. The PASS results establish properties
of those models, not the physical truth of any CCA interpretation. Inspection of
the script is required to confirm the constructions faithfully represent the claims.

---

## 10. Reproducible Commands

```bash
cd /home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/\
phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt

python 04_validations/cca_geometric_transport_verification.py
# Output: 04_validations/outputs/cca_geometric_transport_verification.json
# Dependencies: numpy, math, json (all standard)
```
