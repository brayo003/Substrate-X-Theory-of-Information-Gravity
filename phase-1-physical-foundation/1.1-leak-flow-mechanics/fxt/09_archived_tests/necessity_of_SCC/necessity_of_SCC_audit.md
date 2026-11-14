# Necessity of Symmetric Compositional Closure (SCC): A Formal Audit

**Research Question**: Is SCC mathematically and physically necessary, or merely sufficient?

**Date**: 2026-07-21

---

## Executive Summary

This audit determines whether Symmetric Compositional Closure (SCC) is uniquely forced by the minimal unavoidable requirements of reality, and whether SCC uniquely generates observed physical structure.

**Classification Labels**:
- `[T]` — Logical/mathematical theorem (proved here)
- `[KR]` — Known rigorous result (literature)
- `[MC]` — Mathematical conjecture (unproved)
- `[PHY]` — Direct experimental necessity
- `[OP]` — Open problem

---

## Background (Accepted)

Previous audits established:

1. **SCC implies complex structure (O1)** `[KR]`
2. **SCC implies continuum structure (O2)** `[KR]`
3. **SCC reproduces**:
   - Haar probability `[KR]`
   - Interference `[KR]`
   - Born rule `[KR]`
   - Hamiltonian geometry `[KR]`
   - Gibbs statistical mechanics `[KR]`
   - State composition `[KR]`

**Remaining unresolved issues**:
- **PA1**: Why should microscopic reversibility hold?
- **PG**: Why this specific symmetry group (U(1), SU(2), SU(3), Lorentz)?
- Lorentz symmetry origin
- Gauge symmetry origin
- QFT foundations

---

## Phase I: Minimal Unavoidable Physical Requirements

### I.1 Requirement Identification

Each requirement is tagged with its justification class.

---

**R1 — Existence of Distinguishable States** `[PHY]`

Reality presents distinguishable outcomes. Any framework must assign distinct mathematical objects to distinct outcomes. This is not a model assumption; it is a precondition for any empirical statement.

---

**R2 — Composability of Systems** `[PHY]`

Two physical systems can be combined into a joint system. The joint system must be describable within the same framework as each part. This is established by every experiment involving correlated subsystems.

---

**R3 — Reproducibility (Statistical Stability)** `[PHY]`

Repeated preparation of identical conditions yields stable relative frequencies. Without this, no law of physics could be stated. This is the minimal empirical content of science.

---

**R4 — Finite Information per Bounded Region** `[PHY]` `[KR]`

Bekenstein bound and holographic entropy bounds establish that a bounded region of space contains finite information. Formally: the number of distinguishable states accessible to a bounded system is finite or countably infinite.

*Reference*: Bekenstein (1973), Bousso (2002).

---

**R5 — Causal Order** `[PHY]`

There exists a partial order on events consistent with all observed signal propagation. No experiment has violated this. This is the minimal content of special relativity's causal structure.

---

**R6 — No Preferred Observer** `[PHY]` `[KR]`

The laws of physics take the same form in all inertial frames. This is directly established by precision tests of Lorentz invariance (CPT tests, clock comparisons, muon lifetime).

---

**R7 — Unitarity / Conservation of Distinguishability** `[PHY]`

If two preparations are distinguishable at time t, they remain distinguishable at time t' under reversible dynamics. Violated if information is destroyed — no such violation has been confirmed experimentally.

---

### I.2 Dependency Lattice

```
R1 (Distinguishable States)
  |
  +---> R3 (Reproducibility) ---> [Statistical framework required]
  |
  +---> R2 (Composability)   ---> [Composition law required]
              |
              +---> R7 (Unitarity) ---> [Invertible maps required]

R4 (Finite Information) ---> [Discrete or countable state space locally]

R5 (Causal Order) ---------> [Partial order on events]

R6 (No Preferred Observer) -> [Symmetry group on kinematics]
```

### I.3 Independence Analysis

**Claim I.A** `[T]`: R1 is independent of R2–R7.

*Proof*: A universe with distinguishable states but no composition law (solipsistic universe) satisfies R1 but not R2. ∎

**Claim I.B** `[T]`: R3 is independent of R1 alone.

*Proof*: R3 requires a measure on outcomes. R1 only requires distinctness, not measure. ∎

**Claim I.C** `[T]`: R7 is not derivable from R1–R3 alone.

*Proof sketch*: One can construct a model satisfying R1, R2, R3 in which the time-evolution map is not invertible (e.g., a classical dissipative system with multiple states mapping to one). Such a model satisfies reproducibility (the forward map is well-defined and stable) but violates unitarity. Hence R7 is an independent requirement. This is exactly problem PA1. ∎

**Claim I.D** `[T]`: R5 is independent of R1–R4.

*Proof*: Aristotelian physics satisfies R1–R4 but has no finite signal speed and hence no non-trivial causal order. ∎

---

## Phase II: Derivation of SCC from Minimal Requirements

### II.1 Definition of SCC

**Definition (SCC)**: A framework satisfies Symmetric Compositional Closure if:

1. **(C) Closure**: The state space S is closed under a binary composition operation ⊗: S × S → S.
2. **(S) Symmetry**: There exists a group G acting on S such that composition is equivariant: g·(s₁ ⊗ s₂) = (g·s₁) ⊗ (g·s₂).
3. **(I) Invertibility**: The action of G on S is by invertible maps.
4. **(N) Normalization**: S carries a G-invariant probability measure.

### II.2 Derivation Attempt

**Step II.A**: From R1, the state space S is a set of distinguishable objects.

**Step II.B**: From R3, S must carry a probability measure μ. By R3 alone, μ need not be unique or canonical. `[T]`

**Step II.C**: From R2, there is a composition map ⊗: S × S → S. This gives (C).

**Step II.D** `[T]`: *If* R6 holds and the symmetry group G of R6 acts on S, *and* G acts by invertible maps (R7), *then* (S) and (I) hold.

*Proof*: R6 states laws are frame-independent, hence G acts on S. R7 states distinguishability is preserved, hence the action is by injections. Finite information (R4) on a finite or countable space implies injections are bijections. ∎

**Step II.E** `[T]`: From R3 + G-action, if G is compact, there exists a unique G-invariant probability measure on S (Haar measure). This gives (N).

*Proof*: Standard result — compact groups admit unique normalized Haar measure. `[KR]`

**Step II.F** (Critical Gap): Steps II.A–II.E derive SCC **only if** the symmetry group G from R6 is compact and acts transitively on S.

**Additional Assumption Required** — **AA1** `[PHY]`:

> The kinematic symmetry group G is compact (or at minimum, locally compact unimodular).

*Classification*: AA1 is **physical**, not logical. Lorentz group SO(1,3) is **not** compact. The rotation subgroup SO(3) is compact. Whether the full relativistic symmetry group is compact depends on the physical setting.

*Consequence*: Over non-compact G, Haar measure is not normalizable, and (N) fails unless restricted to compact subgroups or bounded regions.

**Conclusion of Phase II** `[T]`:

SCC is derivable from {R1, R2, R3, R4, R6, R7} **plus AA1** (compactness of G). Without AA1, the derivation is blocked at step II.E. The obstruction is precisely the non-compactness of the full relativistic symmetry group.

---

## Phase III: Derivability of Microscopic Reversibility (PA1)

### III.1 The Problem

**PA1**: Why must the dynamical evolution map be invertible (microscopically reversible)?

The accepted SCC framework assumes invertibility. This phase determines whether invertibility is derivable from R1–R7 or is an independent assumption.

### III.2 Candidate Derivation Routes

**Route A — Composition**

*Argument*: If two states s₁ ≠ s₂ compose with a reference state r to give s₁ ⊗ r and s₂ ⊗ r, and these composite states must remain distinguishable (R1), then the evolution of the composite must preserve this distinction. If evolution φ maps both s₁ and s₂ to the same state, then φ(s₁ ⊗ r) = φ(s₂ ⊗ r), violating distinguishability of the composite.

*Assessment*: `[T]` This argument works **if** composition commutes with evolution, i.e., φ(s ⊗ r) = φ(s) ⊗ φ(r). This commutativity is an additional assumption — call it **AA2**.

**Route B — Reproducibility**

*Argument*: If φ is not invertible, then some state σ has no pre-image. An experimenter who prepares σ by some method cannot reconstruct what the earlier state was. This does not contradict R3, which only requires forward stability.

*Assessment*: Reproducibility (R3) is a forward condition. It does not force invertibility. **Route B fails.** `[T]`

**Route C — Finite Information**

*Argument*: On a finite state space (R4), an injective map is automatically bijective. If distinguishability-preservation (R7) requires φ to be injective, and the state space is finite, then φ is bijective and hence invertible.

*Assessment*: `[T]` This works on finite state spaces. For infinite-dimensional state spaces (e.g., quantum fields), R4 is only local — the global space may be infinite-dimensional. The argument fails globally.

**Route C (local version)**: Within any bounded region, R4 gives a finite-dimensional local state space. On this restricted space, injectivity implies bijectivity. **This is a partial derivation.** `[T]`

**Route D — Symmetry**

*Argument*: If G acts on S by automorphisms (from R6), and time-evolution is an element of G (or generated by the Lie algebra of G), then it is invertible by the group axioms.

*Assessment*: This requires time-translation to be part of the symmetry group G. This is true in Hamiltonian mechanics (time-translation ∈ symplectomorphisms) and in unitary quantum mechanics. But this **assumes** that dynamics is generated by the symmetry group — it does not derive it. **Route D is circular** unless G is independently determined to include time-translation.

**Route E — Conservation Laws / Noether**

*Argument*: By Noether's theorem `[KR]`, continuous symmetries imply conservation laws. Time-translation symmetry implies energy conservation. If energy is bounded below (stable vacuum), the time-evolution operator must be unitary (Stone's theorem `[KR]`).

*Assessment*: Stone's theorem derives unitarity from a self-adjoint generator on a Hilbert space. **This requires**:
  (a) The state space is a Hilbert space — not yet established at this stage.
  (b) Time-translation is a strongly continuous one-parameter group — requires R6.
  (c) The generator is self-adjoint — requires energy bounded below.

This is a valid derivation **conditional on Hilbert space structure**, which is itself the output of SCC. **Circular if used to derive SCC.** `[T]`

### III.3 Conclusion on PA1

**Theorem III.1** `[T]`:

Microscopic reversibility (PA1) is **not derivable** from {R1, R2, R3, R5, R6} alone on general state spaces.

It **is derivable** from {R1, R2, R4, R7} on **finite or locally finite state spaces** via injectivity-bijectivity (Route C).

For infinite-dimensional state spaces, reversibility requires either:
- AA2 (evolution commutes with composition), or
- Hilbert space structure (which presupposes SCC), or
- Time-translation ∈ G (which must be separately justified).

**PA1 classification**: **Physical assumption** on general spaces; derivable as a theorem on locally finite spaces.

---

## Phase IV: Does SCC Uniquely Determine the Symmetry Group?

### IV.1 The Problem (PG)

SCC requires a group G acting on the state space. The question is whether the axioms of SCC, together with R1–R7, uniquely select G = U(1) × SU(2) × SU(3) × SO(1,3) (the Standard Model gauge × Lorentz group).

### IV.2 What SCC Constrains

**Lemma IV.A** `[T]`: SCC with a finite-dimensional irreducible state space requires G to be a compact Lie group.

*Proof*: Closure (C) and invariant measure (N) on a finite-dimensional space with a group action: by Peter–Weyl theorem `[KR]`, G must be compact to admit a normalized invariant measure. ∎

**Lemma IV.B** `[T]`: SCC does not select a unique compact Lie group.

*Proof*: Let G₁ = U(1) and G₂ = SU(2). Both are compact Lie groups. Both can act on appropriate state spaces satisfying all four SCC axioms (C, S, I, N). SCC axioms are satisfied by both. Hence SCC does not distinguish G₁ from G₂. ∎

### IV.3 Selection Theorems (Literature Search)

**Result IV.C** `[KR]`: Wigner's theorem classifies symmetries of a quantum Hilbert space as unitary or antiunitary operators. This constrains G ⊆ U(H), the unitary group of the Hilbert space, but does not select a specific subgroup.

**Result IV.D** `[KR]`: Coleman–Mandula theorem states that, under assumptions of (i) Poincaré invariance, (ii) mass gap, (iii) analyticity of S-matrix, the most general symmetry group of the S-matrix is (Poincaré) × (internal compact group). This **assumes** Poincaré invariance as input, and does not derive the internal group.

**Result IV.E** `[KR]`: Haag–Lopuszanski–Sohnius theorem extends Coleman–Mandula to include supersymmetry. Again, Poincaré is an input.

**Result IV.F** `[KR]`: Classification of simple compact Lie groups: A_n (SU(n+1)), B_n (SO(2n+1)), C_n (Sp(2n)), D_n (SO(2n)), G₂, F₄, E₆, E₇, E₈. SCC selects "compact Lie group" but cannot select among these without further input.

### IV.4 Obstruction Theorem

**Theorem IV.1** `[T]`: SCC + {R1–R7} does not uniquely determine the internal symmetry group.

*Proof*: By Lemma IV.B, any compact Lie group G can serve as the symmetry group in an SCC-satisfying framework. The SCC axioms are group-agnostic: they require a group action with invariant measure, but any compact G provides this. No axiom in {R1–R7} distinguishes U(1) from SU(2) from SU(5). ∎

**Corollary IV.2** `[T]`: Selecting G = U(1) × SU(2) × SU(3) requires at minimum one of:
- Specifying the representation content (matter content) — **empirical** `[PHY]`
- A principle selecting minimality among anomaly-free gauge theories — **[MC]**
- A principle from quantum gravity or string landscape — **[OP]**

### IV.5 Lorentz Group Selection

**Theorem IV.3** `[T]`: The Lorentz group SO(1,3) is not selected by SCC alone.

*Proof*: SCC requires compact G for normalized Haar measure. SO(1,3) is **non-compact**. Hence:
- If SCC is applied with G = SO(1,3), axiom (N) fails (no normalizable Haar measure on SO(1,3)).
- SCC naturally selects compact subgroups, e.g., SO(3) ⊂ SO(1,3).
- Recovering the full Lorentz group requires additional input (e.g., special relativistic kinematics from R5 + R6). ∎

**Conclusion of Phase IV**: SCC determines that G must be a compact Lie group. It does **not** select a unique compact Lie group, and it cannot directly produce the non-compact Lorentz group without additional relativistic axioms. The symmetry group problem **PG remains open** — it is an obstruction to Result A.

---

## Phase V: Does Spacetime Follow from SCC?

### V.1 Spacetime Requirements

SCC operates on an abstract state space S with a group action. Spacetime structure means:
1. A manifold M with metric g of Lorentzian signature (−,+,+,+)
2. Dimension d = 4
3. Causal cones consistent with c = finite
4. Locality: fields are defined at points of M

### V.2 What SCC Produces

**Step V.A** `[T]`: From SCC with G compact and the state space carrying an irreducible unitary representation, the state space is a complex Hilbert space (by Peter–Weyl + Stone–von Neumann `[KR]`). This gives complex linear structure but **not** a spacetime manifold.

**Step V.B** `[T]`: Locality (field at a point) requires an additional structure: a map from spacetime points x ∈ M to operators on the Hilbert space. SCC does not produce this map. An additional axiom is required — call it **AA3**:

> **AA3** `[PHY]`: Observables are associated to bounded regions of a background spacetime manifold (Haag–Kastler axioms `[KR]`).

**Step V.C** (Dimension): Why d = 4?

- Kaluza–Klein arguments require d = 4 + compact extra dimensions — **not** derivable from SCC `[MC]`
- Anthropic/landscape arguments — **phenomenological** `[PHY]`
- Conformal bootstrap / CFT arguments constrain but do not fix d `[KR]`
- **Conclusion**: Dimension d = 4 is not derivable from SCC. `[T]`

**Step V.D** (Lorentzian signature):

- Euclidean signature (+ + + +) is compatible with SCC (compact rotation group SO(4))
- Lorentzian signature (− + + +) introduces a non-compact boost factor
- Selection of Lorentzian vs Euclidean requires causal order R5 plus additional assumptions about the nature of time `[PHY]`
- **Conclusion**: Lorentzian signature is partially motivated by R5 but not uniquely derived. `[T]`

**Step V.E** (Causal Cones):

From R5, a partial causal order exists. From R6, this order must be Lorentz-invariant. Together these constrain the causal cone structure to be that of Minkowski space or a curved generalization. **This is the strongest partial derivation**:

**Theorem V.1** `[T]`: R5 + R6 + finite signal speed (from R4 applied to information transfer) imply the existence of Lorentz-covariant light cones. The metric signature (−,+,+,+) follows if one additionally assumes d = 4 and no preferred spatial direction.

*Proof sketch*: R6 (no preferred observer) + finite signal speed → Lorentz transformation as the unique (up to scaling) linear map preserving the speed of signal propagation (standard derivation of special relativity `[KR]`). The invariant interval ds² = −c²dt² + dx² follows. ∎

### V.3 Where Additional Assumptions First Appear

| Structure | Status | First Additional Assumption |
|---|---|---|
| Complex Hilbert space | Derived from SCC | SCC itself |
| Group action on Hilbert space | Derived from SCC + R6 | R6 |
| Light cones / causal structure | Partially derived | R5 + R6 + finite c |
| Lorentzian metric | Partially derived | R5 + R6 + d=4 + isotropy |
| Dimension d = 4 | Not derived | AA4: d=4 empirical `[PHY]` |
| Spacetime manifold | Not derived | AA3: locality axiom `[PHY]` |
| Curvature / GR | Not derived | AA5: equivalence principle `[PHY]` |

**Conclusion of Phase V**: Causal light-cone structure is derivable. The Lorentzian metric is nearly derivable given dimension. Spacetime as a 4-dimensional manifold requires empirical inputs AA3, AA4 that are not logical consequences of SCC.

---

## Phase VI: Does SCC Subsume All Known Successful Physical Frameworks?

### VI.1 Classification Key

- **D** — Derived: follows as a theorem from SCC + {R1–R7}
- **PD** — Partially Derived: follows with at most one labeled additional assumption
- **RE** — Requires Extension: needs substantial additional structure
- **IM** — Impossible: contradicts SCC or is logically independent

---

### VI.2 Classical Mechanics

**Hamilton's equations**: `[PD]`

*Route*: SCC on a classical phase space (S = T*Q, symplectic manifold) with G = symplectomorphism group. The composition law is the product of symplectic manifolds. The Haar measure is the Liouville measure. Hamilton's equations follow from the requirement that time evolution preserves the symplectic form (Liouville's theorem `[KR]`).

*Additional assumption*: Phase space is a cotangent bundle (configuration space exists) — **AA6** `[PHY]`.

**Newton's second law**: `[PD]`

Follows from Hamilton's equations plus AA6 + the identification F = −∇V. The force concept requires a potential, which is an empirical input.

---

### VI.3 Hamiltonian Mechanics

**Status**: `[D]`

*Route*: SCC directly produces Hamiltonian structure. The state space S with G-invariant symplectic form and Noether's theorem `[KR]` gives conserved Hamiltonians for each continuous symmetry. Time evolution as a one-parameter subgroup of G gives Hamilton's equations exactly.

*No additional assumptions beyond SCC + R6 (time-translation symmetry).*

---

### VI.4 Statistical Mechanics

**Gibbs ensemble**: `[D]`

*Route*: The G-invariant Haar measure on state space = microcanonical ensemble. Maximum entropy subject to energy constraint = canonical ensemble (standard derivation `[KR]`). SCC gives the measure; thermodynamics follows.

**Boltzmann H-theorem**: `[PD]`

Requires molecular chaos hypothesis (Stosszahlansatz) — an additional statistical assumption `[PHY]`.

---

### VI.5 Transport Theory

**Status**: `[PD]`

Boltzmann transport equation follows from SCC + molecular chaos + locality. The collision integral requires a specific scattering cross-section — empirical. The general structure (continuity equation, entropy production) is derivable.

---

### VI.6 Quantum Mechanics

**Status**: `[D]`

*Route*: SCC on a complex Hilbert space (derived in Phase II + V.A):
- Superposition principle: linearity of H `[D]`
- Born rule: Haar measure = |ψ|² `[D]` (Gleason's theorem `[KR]`)
- Schrödinger equation: Stone's theorem applied to unitary time evolution `[D]`
- Heisenberg uncertainty: Fourier analysis on the group `[D]`
- Measurement: von Neumann projection postulate `[PD]` (requires decoherence mechanism)

*No additional assumptions beyond SCC + R6.*

---

### VI.7 Gauge Theory

**Status**: `[RE]`

*Route*: SCC produces a compact internal symmetry group G_int (Phase IV). Gauging G_int (promoting global to local symmetry) requires:
- A connection on a principal G_int-bundle over spacetime
- This requires spacetime M to exist (AA3, AA4 — not derived)
- The Yang–Mills action is then the unique gauge-invariant, local, dimension-4 action `[KR]`

*Obstruction*: Gauging requires spacetime. Spacetime is not derived from SCC. **Gauge theory is derivable conditional on spacetime structure.**

*Additional assumptions*: AA3 (locality), AA4 (d=4), AA7: G_int = U(1)×SU(2)×SU(3) (empirical).

---

### VI.8 General Relativity

**Status**: `[RE]`

*Route*: SCC + R5 + R6 gives special relativistic kinematics. GR requires additionally:
- Equivalence principle **AA5** `[PHY]`
- Spacetime manifold AA3 `[PHY]`
- Einstein field equations follow from AA5 + diffeomorphism invariance as unique second-order field equations for the metric (Lovelock's theorem `[KR]`)

*Einstein equations are derivable from AA3 + AA5 + diffeomorphism invariance.* They are **not** derivable from SCC alone.

---

### VI.9 Quantum Field Theory

**Status**: `[RE]`

*Route*: QFT = quantum mechanics (D) + special relativity (PD) + locality (RE) + specific field content (PHY).

- Free quantum fields: Wightman axioms follow from SCC + Poincaré group + locality `[KR]`
- Interactions: require specific Lagrangian — empirical
- Renormalizability: constrains interactions but does not uniquely select them `[KR]`
- Standard Model: requires empirical matter content `[PHY]`

*QFT structure is derivable; specific theories require empirical input.*

---

### VI.10 Summary Table

| Framework | Status | Key Gap |
|---|---|---|
| Hamiltonian mechanics | D | None |
| Classical mechanics | PD | Config space structure |
| Statistical mechanics (Gibbs) | D | None |
| Transport (Boltzmann) | PD | Molecular chaos |
| Quantum mechanics | D | None |
| Gauge theory (structure) | RE | Spacetime required |
| General relativity | RE | Equivalence principle |
| QFT (structure) | RE | Spacetime + locality |
| Standard Model | RE | Empirical matter content |

---

## Phase VII: Experimentally Distinguishable Consequences of SCC

### VII.1 Approach

SCC makes structural predictions that go beyond any single physical theory. We search for consequences that are:
1. Derivable from SCC without additional empirical input, and
2. Either confirmed, falsifiable, or distinguishable from alternative frameworks.

---

### VII.2 Prediction 1 — Universal Interference Structure

**Claim** `[T]`: Any system satisfying SCC must exhibit interference in the sense that probability amplitudes combine linearly before squaring.

*Derivation*: SCC → complex Hilbert space → superposition → |ψ₁ + ψ₂|² ≠ |ψ₁|² + |ψ₂|² in general.

*Experimental status*: Confirmed for electrons, photons, neutrons, molecules up to ~2000 atoms `[PHY]`.

*Distinguishability*: A theory without complex Hilbert space structure (e.g., real Hilbert space QM) would fail SCC's composition axiom at the level of entangled states. **Real Hilbert space QM is falsified by Bell inequality violations** `[KR]` (Renou et al., 2021). SCC predicts complex structure and hence predicts violation of real-QM Bell inequalities. **This is an experimentally confirmed distinguishing prediction.** ✓

---

### VII.3 Prediction 2 — Exact Born Rule

**Claim** `[T]`: SCC uniquely selects the Born rule p = |ψ|² as the probability measure.

*Derivation*: Gleason's theorem `[KR]` — the unique probability measure on a Hilbert space (dim ≥ 3) consistent with the frame independence condition (which follows from G-invariance in SCC) is the Born rule.

*Distinguishability*: Any deviation from Born rule (e.g., p = |ψ|^α, α ≠ 2) violates G-invariance and hence violates SCC. Experimental tests of Born rule: no deviations found at 10⁻⁵ level `[PHY]`.

---

### VII.4 Prediction 3 — Compositional Scaling of Entropy

**Claim** `[T]`: For a composite system A⊗B in SCC, the maximum entropy satisfies S(A⊗B) = S(A) + S(B) (additivity) when A and B are uncorrelated.

*Derivation*: Haar measure on product group → product measure → additive entropy.

*Distinguishability*: Non-additive entropy (Tsallis q≠1) would require a non-product composition law, violating SCC axiom (C). Experimental tests of entropy additivity: consistent with additivity in all thermodynamic systems tested `[PHY]`.

---

### VII.5 Prediction 4 — No Higher-Order Interference

**Claim** `[T]`: SCC predicts strictly second-order (two-slit) interference. Third-order and higher interference terms must vanish.

*Derivation*: This is Sorkin's result `[KR]` (Sorkin 1994): standard quantum mechanics (derivable from SCC) predicts that the third-order interference term κ₃ = 0 exactly. This is a consequence of the Born rule being quadratic in amplitudes.

*Experimental status*: Third-order interference tested and found consistent with zero: |κ₃/κ₂| < 10⁻² `[PHY]` (Sinha et al., 2010; Kauten et al., 2017).

*Distinguishability*: Any framework with non-quadratic probability rule would predict κ₃ ≠ 0. SCC uniquely predicts κ₃ = 0. **This is a sharp, confirmed, distinguishing prediction.** ✓

---

### VII.6 Prediction 5 — Symmetry Group Constraints (Partial)

**Claim** `[T]`: SCC requires the internal symmetry group to be compact. Any observed non-compact internal symmetry would falsify SCC.

*Experimental status*: All observed internal symmetries (U(1), SU(2), SU(3)) are compact `[PHY]`. No non-compact internal symmetry has been observed.

*Note*: This is consistent with SCC but does not uniquely confirm it — other frameworks also predict compact internal symmetries.

---

### VII.7 New Predictions Not Yet Tested

**Prediction P1** `[MC]`: If SCC is extended to curved spacetime, the composition law for states across causally disconnected regions should still be associative. This constrains the entanglement structure near horizons and may predict specific corrections to Hawking radiation entropy.

**Prediction P2** `[MC]`: In any SCC-derived statistical mechanics, the fluctuation theorem takes a universal form depending only on the group structure of G. Different choices of G predict different fluctuation theorem coefficients — potentially distinguishable in precision thermodynamics experiments.

**Prediction P3** `[OP]`: If SCC can be extended to include gravity (non-compact diffeomorphism group), the compositional structure of quantum gravity amplitudes would be constrained. Whether this leads to measurable predictions is an open problem.

### VII.8 Observational Equivalence Assessment

For the domain of non-relativistic quantum mechanics and thermodynamics: **SCC is observationally equivalent to standard quantum mechanics.** No experiment in this domain can distinguish "SCC-derived QM" from "axiomatically postulated QM" because they produce identical predictions.

For relativistic QFT and gravity: SCC is **not yet complete** (requires AA3–AA5), so comparison is premature.

---

## Final Classification

### Evidence Summary

**Forward direction (Reality → SCC)**:

| Requirement | Status |
|---|---|
| R1–R4, R7 → SCC on finite spaces | ✓ Derived (with AA1 compactness) |
| R5, R6 → Lorentz kinematics | ✓ Partially derived |
| AA1 (compactness) | Independent physical assumption |
| Unique G | ✗ Not derived — obstruction confirmed |
| Spacetime manifold | ✗ Not derived — requires AA3, AA4 |

**Backward direction (SCC → Physics)**:

| Framework | Status |
|---|---|
| QM (non-relativistic) | ✓ Fully derived |
| Hamiltonian mechanics | ✓ Fully derived |
| Statistical mechanics | ✓ Fully derived |
| Special relativity (kinematics) | ✓ Partially derived |
| Gauge theory (structure) | Conditional on spacetime |
| GR | Requires equivalence principle |
| Standard Model (specific) | Requires empirical matter content |

### Classification

**Result B**:

> Reality uniquely forces SCC **conditional on AA1** (compactness of kinematic symmetry group), but further principles are required for complete physics.

Specifically:
- SCC is **uniquely forced** from {R1, R2, R3, R4, R6, R7} + AA1 on locally finite state spaces. `[T]`
- SCC **cannot be uniquely forced** without AA1, because the full Lorentz group is non-compact. `[T]`
- SCC **does not uniquely determine** the symmetry group G. `[T]` — Obstruction: Phase IV
- SCC **does not produce spacetime structure** without AA3, AA4. `[T]` — Obstruction: Phase V
- The converse (SCC → observed physics) is **complete for QM and mechanics**, partial for relativity, and requires empirical extension for gauge theory and gravity.

### Open Problems

**OP1** `[OP]`: Find a principle that selects a unique compact Lie group from the SCC axioms. Candidates: anomaly cancellation, consistency of composition algebra, categorical uniqueness.

**OP2** `[OP]`: Determine whether AA1 (compactness) can be derived from a more primitive axiom (e.g., finite observation time, finite accessible energy).

**OP3** `[OP]`: Determine whether the equivalence principle (AA5) is a consequence of SCC applied to a curved composition law.

**OP4** `[OP]`: Extend SCC to the non-compact case and determine what replaces Haar measure (Plancherel measure on non-compact groups). Determine whether this extension is consistent and physically interpretable.

---

*End of Audit Document*

*Symbolic verifications: see necessity_of_SCC_sympy.py*

*Numerical validations: see necessity_of_SCC_validation.py*
