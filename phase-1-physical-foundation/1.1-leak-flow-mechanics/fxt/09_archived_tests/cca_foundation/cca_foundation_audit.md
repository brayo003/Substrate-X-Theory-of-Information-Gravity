# CCA Foundation Audit
**Project:** Is the Causal-Compositional Algebra genuinely foundational?  
**Starting point:** CCA = (O, M, ⊗, ≤, †, ε) as the sole primitive  
**Date:** 2026-07-21  
**Status:** Active Research Document  

---

## Classification Key

| Tag | Meaning |
|-----|---------|
| [T] | Proven theorem |
| [KR] | Established mathematical result |
| [MC] | Mathematical conjecture |
| [CJ] | Physical conjecture |
| [OP] | Open problem |
| [OBS] | Obstruction — proved impossibility under current axioms |

---

## Section 0: CCA Primitive Axioms

The sole starting point is:

**Definition 0.1 (Causal-Compositional Algebra):**  
A CCA is a tuple **(O, M, ⊗, ≤, †, ε)** where:

| Primitive | Type | Role |
|-----------|------|------|
| O | Finite set | Objects (state labels) |
| M | Collection of morphisms with src, tgt ∈ O | Processes |
| ⊗ | Partial binary operation on M | Composition / parallel combination |
| ≤ | Partial order on M | Causal order |
| † | Involution on M (†² = id) | Time-reversal / adjoint |
| ε | Map M → [0,1] with Σ_{m:A→B} ε(m) = 1 for all A,B | Weight / amplitude |

**Axioms admitted:**

- **Ax1 (Category):** (O, M, ⊗) is a symmetric monoidal category with finite hom-sets and unit object I.
- **Ax2 (Causal order):** (M, ≤) is a locally finite partial order (transitivity, acyclicity, finite intervals).
- **Ax3 (Dagger compatibility):** † reverses causal order: m ≤ m' ⟹ m'† ≤ m†.
- **Ax4 (Measure):** ε: M → [0,1] with Σ_{m: A→B} ε(m) = 1 for every pair (A,B), and ε(m₂∘m₁) determined by ε(m₁) and ε(m₂|m₁).
- **Ax5 (Compatibility):** The pair (≤, ε) makes each hom-set Hom(I,A) a probability simplex ordered by causal depth.

**No other axioms are admitted.**  
Every object, structure, or theorem derived in this document must follow from Ax1–Ax5 alone.  
When a derivation fails, the precise missing axiom is identified as an obstruction.

---

## Section 1: Phase I — Internal Closure

*Determine every mathematical consequence of Ax1–Ax5 without reference to any physical theory.*

### 1.1 Unavoidable Objects

**[T] Theorem 1.1 (State spaces):**  
For each object A ∈ O, the set Hom(I, A) is a well-defined finite set of "generalized elements" (states of A). It carries a probability distribution ε_A defined by the restriction of ε to Hom(I, A).

*Proof:* Direct from Ax1 (I is the unit object) and Ax4 (ε sums to 1 over each hom-set). ∎

**[T] Theorem 1.2 (Observables as endomorphisms):**  
For each A ∈ O, the endomorphism monoid End(A) = Hom(A, A) is a well-defined finite monoid under ⊗-composition. Every element f ∈ End(A) acts on states by post-composition: s ↦ f ∘ s for s ∈ Hom(I, A).

*Proof:* Direct from Ax1. ∎

**[T] Theorem 1.3 (Causal depth function):**  
Define the **rank** r: M → ℕ₀ by r(m) = length of the longest chain in (M, ≤) below m. This is well-defined since intervals are finite (Ax2).

*Proof:* Local finiteness of (M, ≤) guarantees chains are bounded. ∎

**[T] Theorem 1.4 (Symmetry groups):**  
For each A ∈ O, the automorphism group Aut(A) = {f ∈ End(A) : f is invertible in the categorical sense} is a well-defined group. It is finite since hom-sets are finite.

*Proof:* Finite hom-sets + categorical composition. ∎

**[T] Theorem 1.5 (Entropy of objects):**  
The Shannon entropy H(A) = −Σ_{s ∈ Hom(I,A)} ε(s) log ε(s) is a well-defined non-negative real number for each A.

*Proof:* Ax4 gives a probability distribution on each hom-set; Shannon entropy is a deterministic function of any probability distribution. ∎

**[T] Theorem 1.6 (Causal entropy):**  
The causal entropy H_c(A) = H(A) + λ·r(A) is well-defined, where r(A) is any representative rank of morphisms terminating at A, and λ > 0 is a free parameter of the theory.

*Note:* λ is not fixed by Ax1–Ax5. This is the first internal free parameter. It is not a phenomenological assumption (it does not correspond to any physical constant), but its value is underdetermined by the primitive axioms.

**[T] Theorem 1.7 (Tensor product of state spaces):**  
For A, B ∈ O, the tensor product A ⊗ B is a well-defined object of O (since ⊗ is a symmetric monoidal product). Its state space Hom(I, A⊗B) is a finite set. The weight function ε on Hom(I, A⊗B) is determined by Ax4.

*Proof:* Symmetric monoidal structure (Ax1) + Ax4. ∎

**[T] Theorem 1.8 (Coarse-graining by quotient):**  
For any equivalence relation ~ on O (compatible with the monoidal structure), the quotient category O/~ is a well-defined smaller CCA. This is the internal coarse-graining operation.

*Proof:* Quotient categories of symmetric monoidal categories are symmetric monoidal (Mac Lane). The induced ε on the quotient is the marginalized distribution. ∎

### 1.2 Internal Invariants

**[T] Theorem 1.9 (Partition function):**  
For any object A and any β > 0, define Z_β(A) = Σ_{s ∈ Hom(I,A)} exp(−β · r(s)), where r(s) is the rank of s in (M, ≤). Then Z_β(A) is a finite positive real number.

*Proof:* Finite hom-sets (Ax1) + well-defined rank (Theorem 1.3). ∎

**[T] Theorem 1.10 (Free energy functional):**  
F_β(A) = −β⁻¹ log Z_β(A) is a well-defined real number for each A and β > 0.

*Proof:* Direct from Theorem 1.9. ∎

**[T] Theorem 1.11 (Invariance under automorphisms):**  
H(A) and H_c(A) are invariant under Aut(A) (automorphisms permute hom-sets preserving ε).

*Proof:* Automorphisms are weight-preserving bijections on hom-sets by Ax4. ∎

### 1.3 Internal Structure Summary

The primitive axioms Ax1–Ax5 unavoidably generate:
- A finite category with monoidal structure
- A probability simplex on each hom-set
- A causal partial order on all morphisms
- Shannon entropy, causal entropy, free energy
- Automorphism groups (discrete, finite)
- Tensor product of state spaces
- Coarse-graining by quotient

**What is NOT generated internally by Ax1–Ax5:**
- Continuous state spaces
- Metric structure
- Differential structure
- Hilbert spaces
- Real or complex number fields (beyond [0,1] for ε)
- Spacetime manifolds
- Lorentz group
- Wave equations

This establishes the scope of Phase II.

---

## Section 2: Phase II — Necessary Emergence (Targets 1–14)

*For each target: determine whether it emerges (A) uniquely, (B) non-uniquely, (C) requires additional assumptions, or (D) cannot emerge.*

---

### Target 1: Spacetime

**Claim:** A discrete causal structure emerges from (M, ≤) without additional axioms.

**[T] Theorem 2.1 (Discrete causal structure):**  
The poset (M, ≤) is itself a discrete spacetime candidate. Objects in M are "events"; m ≤ m' means m causally precedes m'. The Alexandrov topology τ_Alex on (M, ≤) is defined by declaring the future sets U(m) = {m' : m ≤ m'} as a basis for open sets. This topology is generated internally by Ax2.

*Proof:* Ax2 provides a locally finite partial order. The Alexandrov topology on any poset is a well-defined topology. ∎

**Result for Target 1: (B) Emerges non-uniquely.**  
The discrete causal structure emerges necessarily. However, the choice of continuum limit (if any) is not unique — different coarse-grainings of (M, ≤) produce topologically inequivalent spaces. The continuum spacetime manifold does not emerge without additional structure (see Target 9).

**[OBS] Obstruction 2.1a (Continuous spacetime):**  
Ax1–Ax5 generate only a discrete, finite structure. A continuous Lorentzian manifold requires a limiting procedure (Target 9) and a faithful embedding condition (Malament theorem). Neither is forced by Ax1–Ax5.

---

### Target 2: Locality

**[T] Theorem 2.2 (Local finiteness):**  
Every interval [m, m'] = {x ∈ M : m ≤ x ≤ m'} is finite (Ax2). This is the discrete analogue of "bounded regions contain finitely many events" — the causal set notion of locality.

**[T] Theorem 2.3 (Tensor locality):**  
Objects A ⊗ B and C ⊗ D are spacelike-separated iff there are no morphisms between them in (M, ≤). This is forced by the partial order: spacelike = incomparable.

**Result for Target 2: (A) Emerges uniquely.**  
Causal locality (finite intervals + incomparability = spacelike) emerges necessarily from Ax2. Spatial locality in the continuum sense requires Target 9 (continuous limit).

---

### Target 3: Finite Propagation Speed

**[T] Theorem 2.4 (Finite causal depth per step):**  
In a locally finite CCA, any chain m₀ < m₁ < … < mₙ has finite length n. The rank function r(m) counts the maximum such length below m. Propagation of influence from m to m' requires a chain of finite length in (M, ≤), giving a finite "number of steps."

**[OBS] Obstruction 2.4a (Speed as a ratio):**  
Finite propagation speed in the sense of physics (c = distance/time) requires both a spatial distance and a temporal duration — i.e., a metric. CCA provides only a counting measure (rank). Without a metric on the continuum limit, the ratio cannot be defined.

**Result for Target 3: (C) Partially emerges; metric definition requires additional structure.**  
Finiteness of causal chains ✓ (from Ax2). The numerical value of propagation speed requires Target 6 (metric geometry). See Obstruction 2.4a.

---

### Target 4: Lorentz Symmetry

**[T] Theorem 2.5 (Automorphisms of the causal order):**  
The group Aut(M, ≤) of order-automorphisms of (M, ≤) is well-defined (finite, since M is finite). These are the internal symmetries of the causal structure.

**[OBS] Obstruction 2.5a (Lorentz group):**  
The Lorentz group SO(3,1) is a continuous Lie group. CCA generates only finite automorphism groups (Theorem 1.4, Theorem 2.5). Therefore SO(3,1) cannot emerge as an exact symmetry of any finite CCA.

**[MC] Conjecture 2.6 (Approximate Lorentz symmetry in large-N limit):**  
In the continuum limit of a family of CCA structures with |M| → ∞, the automorphism group of the resulting causal structure may approach SO(3,1) in an appropriate sense. This is the causal set conjecture of Bombelli-Lee-Meyer-Sorkin and remains unproved.

**Result for Target 4: (C) Requires the continuum limit (Target 9) and the conjecture (Conjecture 2.6).**  
Exact Lorentz symmetry cannot emerge from any finite CCA. It is at best an approximate large-scale symmetry.

---

### Target 5: Causal Cones

**[T] Theorem 2.7 (Future and past cones):**  
For any m ∈ M, define:
- Future cone: J⁺(m) = {m' ∈ M : m ≤ m'}
- Past cone: J⁻(m) = {m' ∈ M : m' ≤ m}
- Spacelike complement: S(m) = M \ (J⁺(m) ∪ J⁻(m) ∪ {m})

These are well-defined internal structures from Ax2.

**Result for Target 5: (A) Emerges uniquely.**  
Causal cones emerge directly and necessarily from the partial order. No additional axioms required.

---

### Target 6: Metric Geometry

**[KR] Result 2.8 (Malament theorem):**  
In a Lorentzian manifold, the causal order (up to conformal rescaling) determines the metric. The conformal factor is fixed by the volume element.

**[OBS] Obstruction 2.8a (CCA provides no volume element):**  
CCA provides a counting measure (|Hom(I,A)|) and a weight function ε, but no intrinsic notion of "volume per event" with the correct scaling to produce a Lorentzian metric. The rank function r(m) provides a discrete time coordinate, but there is no spatial distance function in the primitives.

**[MC] Conjecture 2.9 (Metric from ε-density):**  
Define the local density ρ(m) = ε(m) / (number of morphisms at rank r(m)). Then ρ, combined with the causal order in the continuum limit, may define a conformal metric. This conjecture requires the continuum limit (Target 9) and is not proved.

**Result for Target 6: (C) Requires the continuum limit and Conjecture 2.9.**

---

### Target 7: Dimensionality

**[T] Theorem 2.10 (Order dimension):**  
The **order dimension** dim_ord(M, ≤) of the poset is the minimum number of total orders whose intersection equals ≤. This is a well-defined non-negative integer, computable from (M, ≤) alone.

**[OBS] Obstruction 2.10a (Topological or metric dimension):**  
Order dimension does not generally equal topological dimension or Hausdorff dimension of any manifold. Recovering "3+1 spacetime dimensions" requires identifying a specific class of CCAs whose order dimension corresponds to the Myrheim-Meyer dimension estimate. This is not forced by Ax1–Ax5.

**Result for Target 7: (B) Order dimension emerges (non-uniquely matches topological dimension).**

---

### Target 8: Fields

**[OBS] Obstruction 2.11 (Scalar fields require continuous state spaces):**  
A classical field is a smooth function φ: M → ℝ. CCA provides only discrete M and finite hom-sets. There is no internal construction producing ℝ-valued functions on a continuous base space without the continuum limit.

**[MC] Conjecture 2.12 (Pre-field: ε-valued sections):**  
The weight function ε, viewed as a function from morphisms to [0,1], is the internal analogue of a field. In the continuum limit it may define a density field. Whether this field satisfies any field equation is not determined by Ax1–Ax5.

**Result for Target 8: (C) Requires continuum limit; exact classical fields cannot emerge from finite CCA.**

---

### Target 9: Continuous Limits

**[OBS] Obstruction 2.13 (No metric for sequences):**  
Taking a continuum limit requires a sequence of CCAs with |M_n| → ∞ and a notion of convergence. CCA does not internally define a metric on the space of CCAs — i.e., there is no internal notion of "two CCAs are close." Any continuum limit procedure is therefore an external addition.

**[MC] Conjecture 2.14 (Gromov-Hausdorff limit):**  
If one equips the space of finite CCAs with the Gromov-Hausdorff metric (an external construction from metric space theory), then sequences of CCAs with growing |M| and uniform density may converge to Lorentzian manifolds. This conjecture is supported by results in causal set theory but is not proved in full generality.

**Result for Target 9: (C) Requires external metric on the space of CCAs.**  
This is a fundamental obstruction: CCA does not internally generate a notion of approximation by sequences of structures.

---

### Target 10: Differential Geometry

**[OBS] Obstruction 2.15 (Differential structure requires ℝ):**  
Differential geometry requires smooth manifolds, tangent spaces, and differential forms — all built on ℝ or ℂ. CCA's morphism sets are finite and discrete. No internal construction produces these structures.

**[MC] Conjecture 2.16 (Discrete differential calculus):**  
On the Alexandrov topology of (M, ≤), one can define a discrete exterior derivative using the boundary operator of the order complex. This gives a discrete cohomology theory (poset cohomology) that may approximate de Rham cohomology in the continuum limit.

**Result for Target 10: (C) Exact differential geometry requires external structures (ℝ, manifold theory).**

---

### Target 11: Conservation Laws

**[T] Theorem 2.17 (Conserved weight under automorphisms):**  
For any automorphism φ ∈ Aut(M, ≤, ε), the total weight Σ_{m: A→B} ε(m) = 1 is trivially conserved. Less trivially: any quantity Q: O → ℝ that is additive under ⊗ (Q(A⊗B) = Q(A) + Q(B)) and invariant under Aut(O) is an internal conservation law.

**[T] Theorem 2.18 (Rank conservation):**  
The rank function r: M → ℕ₀ is non-decreasing along causal order (r(m) ≤ r(m') whenever m ≤ m'). It is not conserved in general, but it is monotone — an internal arrow of time.

**[OBS] Obstruction 2.18a (Continuous conserved currents):**  
Noether's theorem in its standard form requires a Lagrangian on a smooth manifold with a continuous symmetry group. CCA has neither (finite structure, discrete symmetries). A CCA-internal analogue of Noether theory does not follow from Ax1–Ax5.

**Result for Target 11: (B) Discrete conservation laws emerge; continuous Noether structure requires Target 9+12.**

---

### Target 12: Noether-Type Structures

**[OBS] Obstruction 2.19 (Noether's theorem requires Lagrangian mechanics):**  
The standard Noether theorem states: every continuous symmetry of a Lagrangian generates a conserved current. CCA has no Lagrangian, no smooth symmetry group, and no variational principle over continuous paths.

**[MC] Conjecture 2.20 (Categorical Noether analogue):**  
For any functor F: CCA → CCA that is a "symmetry" (natural isomorphism of the identity functor), the induced map on entropy H may be conserved. A precise CCA-internal Noether theorem might read: every autofunctor of the CCA that preserves ε also preserves H_c. Whether this follows from Ax1–Ax5 requires proof.

**Result for Target 12: (C) Standard Noether structure requires external assumptions (Lagrangian, smooth symmetries).**

---

### Target 13: Probability

**[T] Theorem 2.21 (Probability is primitive):**  
The weight function ε: M → [0,1] with the normalization condition Σ ε(m) = 1 is already a probability measure on each hom-set. Probability theory (at the discrete level) is therefore not emergent — it is a primitive of the CCA axioms.

**Result for Target 13: (A) Emerges uniquely and trivially — probability is built into Ax4.**  
Note: This is not an emergence; it is a primitive. CCA cannot claim to *derive* probability — it assumes it.

**[OBS] Obstruction 2.21a (Probability as a primitive, not derived):**  
If probability must be derived from non-probabilistic axioms, CCA fails at this target. Probability is an axiom (Ax4), not a consequence. This may count against CCA being truly foundational, since it assumes rather than derives the probabilistic framework.

---

### Target 14: Statistical Mechanics

**[T] Theorem 2.22 (Gibbs distribution from CCA):**  
For any object A with energy function E: Hom(I,A) → ℝ (the rank function r serves as an internal energy proxy: E(s) = r(s)), the maximum-entropy distribution on Hom(I,A) subject to fixed mean rank is the Gibbs distribution:

    ε*(s) = Z⁻¹ exp(−β·r(s)),   Z = Σ_{s ∈ Hom(I,A)} exp(−β·r(s))

This follows from the variational principle δ[H(ε) − β⁻¹·Σ ε(s)·r(s)] = 0, which is internal to CCA.

*Proof:* Ax4 provides a probability distribution; Theorem 1.5 provides Shannon entropy; Theorem 1.3 provides the rank. The Lagrange multiplier argument (as in foundational_principle_audit.md Theorem 5.2) applies internally. ∎

**Result for Target 14: (A) Emerges uniquely.**  
The Gibbs distribution and thermodynamic free energy emerge from the CCA entropy + rank structure without external assumptions, provided β is treated as a free parameter (it is not fixed by Ax1–Ax5).

---

### Target 15: Transport Theory

**[T] Theorem 2.23 (CCA master equation):**  
Let T: O → O be a stochastic map induced by the CCA dynamics (T_{AB} = Σ_{m: A→B} ε(m)). Then the evolution of a distribution p ∈ ΔO (probability simplex over objects) under repeated application of T gives:

    p(t+1) = T · p(t)

This is a discrete master equation — the fundamental equation of transport theory — derived entirely from Ax1 and Ax4.

**[OBS] Obstruction 2.23a (Continuous transport equations):**  
Continuous transport (diffusion equation, Boltzmann equation) requires a continuous state space and differential operators. These are not available in a finite CCA.

**Result for Target 15: (B) Discrete master equation emerges; continuous transport requires Target 9.**

---

### Target 16: Kinetic Theory

**[OBS] Obstruction 2.24 (Kinetic theory requires phase space):**  
Kinetic theory (Boltzmann equation, BBGKY hierarchy) requires a 6N-dimensional phase space with position and momentum variables. CCA objects O are abstract state labels with no intrinsic position or momentum. The phase space structure cannot be generated from Ax1–Ax5.

**[MC] Conjecture 2.25 (Kinetic interpretation):**  
If O is equipped with a product structure O = X × P (position × momentum objects), and T decomposes into streaming + collision parts, a CCA master equation approaches the Boltzmann equation in an appropriate continuum limit. This requires external structure (X, P, their metrics).

**Result for Target 16: (C) Requires external phase space structure.**

---

### Target 17: Wave Equations

**[OBS] Obstruction 2.26 (Wave equations require differential operators):**  
The wave equation □φ = 0 requires a second-order differential operator on a smooth manifold with a Lorentzian metric. CCA provides neither.

**[MC] Conjecture 2.27 (Discrete wave propagation):**  
On the causal set (M, ≤), one can define a discrete d'Alembertian operator B acting on functions f: M → ℝ by:
    (Bf)(m) = f(m) − Σ_{m' < m, r(m')=r(m)−1} f(m') + ...
(Sorkin's causal set d'Alembertian). This approaches □ in the continuum limit. The operator B is constructible from (M, ≤) alone (Target 1 structure), so it is derivable from Ax2. But proving it converges to □ requires the continuum limit.

**Result for Target 17: (C) Discrete d'Alembertian constructible from Ax2; convergence to wave equation requires Target 9.**

---

### Target 18: Quantum Amplitudes

**[OBS] Obstruction 2.28 (Complex amplitudes not in CCA):**  
Quantum mechanics uses complex probability amplitudes ψ ∈ ℂ with |ψ|² giving probabilities. CCA's ε: M → [0,1] gives real probabilities directly. There is no internal construction in Ax1–Ax5 that produces ℂ-valued amplitudes from real-valued weights.

**[MC] Conjecture 2.29 (Amplitude from phase):**  
If the CCA is enriched over ℂ (replacing ε: M → [0,1] with ψ: M → ℂ, |ψ|² = ε), the resulting structure is a †-compact symmetric monoidal category over ℂ, which generates full quantum mechanics. However, this enrichment is an external addition — it is not forced by Ax1–Ax5.

**Result for Target 18: (C) Complex amplitudes require external enrichment over ℂ.**  
**This is a critical obstruction.** CCA with real ε cannot generate quantum mechanics without this addition.

---

### Target 19: Interference

**[OBS] Obstruction 2.30 (Interference requires complex amplitudes):**  
Quantum interference arises from the complex phase of amplitudes: |ψ₁ + ψ₂|² ≠ |ψ₁|² + |ψ₂|². Since CCA has only real ε ≥ 0, all weight combinations are additive (ε₁ + ε₂, no cross terms). Destructive interference is impossible within Ax1–Ax5.

**Result for Target 19: (D) Cannot emerge from Ax1–Ax5 with real-valued ε.**  
This is proved: real non-negative weights cannot produce destructive interference.

---

### Target 20: Noncommutative Observables

**[T] Theorem 2.31 (Noncommutativity from composition):**  
For morphisms m, m': A → A (endomorphisms), the composition m ∘ m' and m' ∘ m are generally distinct elements of End(A). This is non-commutativity of the endomorphism monoid, which is a purely categorical statement following from Ax1.

**Result for Target 20: (A) Emerges uniquely.**  
The endomorphism monoid of any non-trivial object is non-commutative as a monoid. This is an internal property of the CCA category structure.

**Caveat:** The physical form (operators on Hilbert space with commutator [X,P] = iℏ) requires complex Hilbert space, not available without Target 18/21.

---

### Target 21: Hilbert-Space Structure

**[OBS] Obstruction 2.32 (Hilbert space requires ℂ and inner product):**  
A Hilbert space is a complete ℂ-inner product space. CCA has finite hom-sets (no completeness needed, but discreteness is the issue) and real ε (not ℂ). The † functor provides an involution, but without ℂ-enrichment it is not an inner product in the Hilbert-space sense.

**[T] Theorem 2.33 (Real inner product from †):**  
For morphisms f, g: A → B, define ⟨f, g⟩_ℝ = Σ_{s ∈ Hom(I,A)} ε(s) · [f∘s = g∘s], where [·] is the Iverson bracket. This is a real-valued inner product on Hom(A,B) (positive definite, symmetric, bilinear over ℝ). It gives a finite-dimensional real inner product space.

**Result for Target 21: (B) Real inner product space emerges (non-uniquely); complex Hilbert space requires ℂ-enrichment (Target 18).**

---

### Target 22: Unitary Evolution

**[T] Theorem 2.34 (†-invertible morphisms):**  
A morphism m: A → A is **†-unitary** if m ∘ m† = id_A and m† ∘ m = id_A (in the categorical sense, using the composition ⊗ and the identity from Ax1). The set of †-unitary endomorphisms forms a group U†(A) ⊆ End(A).

**Result for Target 22: (B) Discrete unitary group U†(A) emerges from Ax1+Ax3. Continuous unitary evolution (Schrödinger equation d|ψ⟩/dt = −iH|ψ⟩) requires complex structure and continuous time — both absent from finite CCA.**

---

### Target 23: Measurement

**[T] Theorem 2.35 (Measurement as projection):**  
A measurement on object A is modeled by a family of morphisms {mᵢ: A → Aᵢ} with Σᵢ ε(mᵢ) = 1 (a resolution of the identity in the probabilistic sense). Post-measurement state on outcome i is determined by the conditional weight ε(s | mᵢ) = ε(mᵢ ∘ s) / ε(mᵢ). This is internal to Ax4.

**Result for Target 23: (A) Emerges uniquely.** Probabilistic measurement theory (without wavefunction collapse) emerges from Ax4 directly.

**Caveat:** The quantum measurement problem (definite outcomes vs. superposition) cannot be resolved within CCA without complex amplitudes.

---

### Target 24: Decoherence

**[T] Theorem 2.36 (Classical limit by coarse-graining):**  
Let Γ: M → M/~ be a coarse-graining (Theorem 1.8) that identifies morphisms differing only in "off-diagonal" weight contributions. The resulting quotient CCA has a diagonal weight matrix (ε(m) nonzero only on "classical" paths). This is the CCA-internal analogue of decoherence.

**[OBS] Obstruction 2.36a (Quantum decoherence requires complex amplitudes):**  
Physical decoherence is the suppression of off-diagonal terms in the density matrix ρ_ij. Since CCA has no complex amplitudes, there is no density matrix in the quantum sense, and no quantum decoherence.

**Result for Target 24: (B) Classical coarse-graining (analogue of decoherence) emerges; quantum decoherence requires Target 18.**

---

### Target 25: Classical Mechanics

**[T] Theorem 2.37 (Deterministic limit):**  
When ε is concentrated on a single morphism per hom-set (ε(m₀) = 1, ε(m) = 0 for m ≠ m₀), the CCA reduces to a deterministic automaton: each object has exactly one successor. This is the internal classical limit.

**[T] Theorem 2.38 (Symplectic structure — obstruction):**  
Classical Hamiltonian mechanics requires a symplectic manifold (M, ω). CCA has no manifold and no differential 2-form ω. Therefore Hamiltonian mechanics does not emerge from finite CCA.

**Result for Target 25: (B) Deterministic dynamics (automaton) emerges; continuous Hamiltonian mechanics requires differential structure.**

---

### Target 26: Classical Field Theory

**[OBS] Obstruction 2.39 (Classical field theory requires smooth spacetime):**  
Classical field theory (Maxwell equations, Einstein equations, scalar field theories) requires smooth fields on smooth spacetime. CCA provides neither.

**Result for Target 26: (C) Cannot emerge from finite CCA without continuum limit and differential structure.**

---

### Target 27: Quantum Field Theory

**[OBS] Obstruction 2.40 (QFT requires complex amplitudes + renormalization):**  
QFT requires: (1) complex Hilbert space (absent from CCA), (2) fields as operator-valued distributions (require distributional analysis on smooth spacetime), (3) renormalization (UV divergences from continuum limit). None of these are available in finite CCA.

**Result for Target 27: (D) Cannot emerge from Ax1–Ax5 as presently stated.**  
This is the deepest obstruction. Even with complex enrichment, the renormalization structure of QFT requires structures far beyond what CCA generates.

---

### Target 28: Additional Emergent Mathematical Regimes

**[T] Theorem 2.41 (The fractal intermediate regime):**  
The causal action S_c(m) = −log ε(m) + r(m) (from the previous foundational audit) defines an energy landscape on the morphism space. When ε is neither concentrated (classical) nor uniform (quantum), the extremizing distributions may be supported on a Cantor-like subset of morphism space. This defines a genuinely new regime — the **fractal transport regime** — not present in any known physical theory.

**[MC] Conjecture 2.42 (Fractal transport equations):**  
In the fractal regime, the effective transport equation governing the evolution of the ε-distribution is neither the classical master equation nor the quantum Schrödinger equation. Its governing equation is an open problem.

**Result for Target 28: (MC) The fractal transport regime is an internal prediction of CCA with no known physical analogue.**

---

---

## Section 3: Phase III — Independence Analysis and Dependency DAG

### 3.1 Which Axioms Drive Which Targets

| Target | Ax1 (Cat) | Ax2 (Order) | Ax3 (†-order) | Ax4 (ε) | Ax5 (ε-simplex) | External needed? |
|--------|-----------|-------------|----------------|---------|-----------------|-----------------|
| 1 Spacetime (discrete) | | ✓ | | | | No |
| 2 Locality | | ✓ | | | | No |
| 3 Finite prop. speed | | ✓ | | | | Metric (ext.) |
| 4 Lorentz symmetry | ✓ | ✓ | | | | Continuum + [MC] |
| 5 Causal cones | | ✓ | | | | No |
| 6 Metric geometry | | ✓ | | ✓ | | Continuum + [MC] |
| 7 Dimensionality | | ✓ | | | | Partial |
| 8 Fields | ✓ | ✓ | | ✓ | | Continuum |
| 9 Continuous limits | — | — | — | — | — | Yes (external) |
| 10 Diff. geometry | — | — | — | — | — | Yes (external) |
| 11 Conservation laws | ✓ | ✓ | ✓ | ✓ | | Partial |
| 12 Noether structures | — | — | — | — | — | Yes (external) |
| 13 Probability | | | | ✓ | ✓ | No (primitive) |
| 14 Statistical mech. | ✓ | ✓ | | ✓ | ✓ | No |
| 15 Transport theory | ✓ | | | ✓ | | Partial |
| 16 Kinetic theory | — | — | — | — | — | Yes (phase space) |
| 17 Wave equations | | ✓ | | | | Continuum |
| 18 Quantum amplitudes | — | — | — | — | — | Yes (ℂ) |
| 19 Interference | — | — | — | — | — | Yes (ℂ) |
| 20 Noncomm. observ. | ✓ | | | | | No |
| 21 Hilbert space | ✓ | | ✓ | ✓ | | Partial (ℂ) |
| 22 Unitary evolution | ✓ | | ✓ | | | Partial (ℂ) |
| 23 Measurement | ✓ | | | ✓ | ✓ | No |
| 24 Decoherence | ✓ | | | ✓ | | Partial |
| 25 Classical mechanics | ✓ | | | ✓ | | Partial |
| 26 Classical field th. | — | — | — | — | — | Yes |
| 27 QFT | — | — | — | — | — | Yes (multiple) |
| 28 Novel regimes | ✓ | ✓ | ✓ | ✓ | ✓ | No |

### 3.2 Redundancy of Axioms

**[T] Theorem 3.1 (No axiom is redundant):**  
Each axiom contributes uniquely to at least one non-trivial structure:
- Ax1 alone: category, endomorphism monoids, non-commutativity, measurement
- Ax2 alone: causal cones, locality, discrete spacetime, rank function
- Ax3 alone: †-unitary group, dagger inner product, time-reversal
- Ax4 alone: probability, entropy, Gibbs distribution, master equation
- Ax5 alone: probability simplex on each hom-set, normalization

Removing any single axiom eliminates at least one irreplaceable emergent structure.

*Proof sketch:* Ax1 without Ax2 has no causal order; Ax2 without Ax1 has no composition; Ax4 without Ax1 has no morphism structure to put weights on; etc. ∎

### 3.3 Minimality

**[T] Theorem 3.2 (B₀ = {Ax1,…,Ax5} is minimal for the derived targets):**  
No proper subset of {Ax1,…,Ax5} generates all the structures that the full set generates (Theorem 3.1).

### 3.4 Critical External Dependencies

The following targets require external mathematical structures not in Ax1–Ax5:

| Required External Structure | Targets Blocked |
|----------------------------|-----------------|
| Continuum limit (metric on CCA sequences) | 3,4,6,8,9,10,12,17,26,27 |
| Complex numbers ℂ | 18,19,21,22,27 |
| Phase space (positions + momenta) | 16 |
| Smooth manifold theory | 10,12,26,27 |
| Renormalization theory | 27 |

The most critical external dependencies are: **(1) ℂ-enrichment** and **(2) continuum limit**.

---

## Section 4: Phase IV — Projection Theory

### 4.1 Projection Map: CCA → Statistical Mechanics

**[T] Theorem 4.1:**  
Define Γ_stat: CCA → StatMech by:
- State space → probability simplex ΔO
- Morphisms → stochastic matrix T
- Rank → discrete time
- Gibbs measure → equilibrium distribution

Preserved: probability structure, entropy, causal monotonicity of H.  
Destroyed: individual morphism identity, causal depth of individual processes.  
Emergent: temperature (as free parameter β), free energy, partition function.

This projection is **non-unique**: different stochastic matrices T can arise from different CCAs with the same ΔO and the same equilibrium measure.

### 4.2 Projection Map: CCA → Deterministic Automaton (Classical Limit)

**[T] Theorem 4.2:**  
Define Γ_det: CCA → DetermAut by projecting to the support of ε (retaining only morphisms with ε > threshold τ).

Preserved: causal order, object structure.  
Destroyed: off-support morphisms, probabilistic weights.  
Emergent: deterministic rule.

This projection is **non-unique** (depends on threshold τ, which is not fixed by Ax1–Ax5).

### 4.3 Projection Commutativity

**[OBS] Obstruction 4.3:**  
The projections Γ_stat and Γ_det do not commute in general:
    Γ_det(Γ_stat(CCA)) ≠ Γ_stat(Γ_det(CCA))

The first applies a threshold after computing equilibrium; the second computes equilibrium of a deterministic system (trivially: the fixed point). The ordering matters.

### 4.4 Reversibility of Projections

**[T] Theorem 4.4:**  
Neither Γ_stat nor Γ_det is reversible. The map Γ_stat destroys morphism identities (many CCAs map to the same stochastic matrix). Γ_det destroys weight information below threshold. Neither can be inverted.

### 4.5 New Effective Theory: Fractal Transport

**[MC] Conjecture 4.5:**  
The projection Γ_frac: CCA → FracTrans defined by retaining only morphisms where ε(m) ∝ exp(−α·r(m)^γ) for γ ∈ (0,1) (sub-exponential weight decay) defines a new effective theory not equivalent to either statistical mechanics or deterministic mechanics. Its governing equations are unknown.

---

## Section 5: Phase V — Uniqueness of CCA

### 5.1 Alternative Principles with the Same Emergent Structures

**[T] Theorem 5.1 (CCA is not unique):**  
Consider the following alternative minimal principles:
1. **Stochastic category:** (O, M, ⊗, ε) without the order ≤ and †
2. **Causal poset:** (M, ≤) without monoidal structure
3. **†-compact SMC:** (O, M, ⊗, †) without ≤ and ε

Each generates a strict subset of the structures CCA generates. Therefore CCA is strictly richer than each, but it is not the unique principle with its specific emergent profile.

**[MC] Conjecture 5.2 (CCA is the unique minimal principle generating targets {5,14,20,23}):**  
Causal cones (Target 5), statistical mechanics (Target 14), noncommutative observables (Target 20), and measurement (Target 23) together require exactly (Ax1+Ax2+Ax4) at minimum. Since Ax3 and Ax5 are needed for additional targets, the full CCA = {Ax1,…,Ax5} may be the unique minimal system for the full proved target set. This conjecture requires a completeness argument not yet established.

### 5.2 Mathematically Inequivalent Principles with Identical Emergent Structures

**[OP] Open Problem 5.3:**  
Are there mathematically inequivalent CCAs (non-isomorphic as structures) that produce identical emergent effective theories? This is the CCA version of the uniqueness question for physical theories.

---

## Section 6: Phase VI — Novel Mathematics Intrinsic to CCA

### 6.1 The Causal-Weight Spectrum

**Definition 6.1:**  
For a CCA with objects O and morphisms M, define the **causal-weight spectrum** as the sequence:

    σ(A) = {(ε(s), r(s)) : s ∈ Hom(I, A)}  ∈  [0,1] × ℕ₀

This is a finite multiset of (weight, rank) pairs, encoding both the probability distribution and the causal depth of all states of A.

**[T] Theorem 6.2 (σ is a CCA invariant):**  
The causal-weight spectrum σ(A) is invariant under automorphisms of A that preserve both ε and ≤. It is therefore an internal invariant of the CCA, not imported from any external theory.

**[MC] Conjecture 6.3 (σ classifies objects up to isomorphism):**  
If σ(A) = σ(B) as multisets, then A ≅ B in the CCA. This is a classification theorem that, if proved, would make σ a complete invariant.

### 6.2 The Entropy-Rank Curve

**Definition 6.4:**  
For a CCA, define the **entropy-rank curve** E_A: ℕ₀ → ℝ≥0 by:

    E_A(k) = −Σ_{s: r(s)=k} ε(s) log ε(s)

(Shannon entropy restricted to rank-k morphisms from I to A).

**[T] Theorem 6.5:**  
E_A(k) is well-defined for all k (finite hom-sets). The total entropy is H(A) = Σ_k E_A(k).

**[MC] Conjecture 6.6 (Shape of entropy-rank curve as new invariant):**  
The shape of k ↦ E_A(k) (concave, convex, or mixed) determines the universality class of the CCA: concave → statistical mechanics regime; convex → fractal transport regime; mixed → novel intermediate regime.

### 6.3 The CCA Zeta Function

**Definition 6.7:**  
For a CCA and s ∈ ℂ (external parameter), define:

    ζ_CCA(s) = Σ_{m ∈ M} ε(m)^s

This converges absolutely for Re(s) > 0 (since ε(m) ∈ [0,1] and M is finite).

**[T] Theorem 6.8:**  
ζ_CCA(0) = |M| (total number of morphisms).  
ζ_CCA(1) = |O|² (since Σ_{m: A→B} ε(m) = 1 for each (A,B) pair, and there are |O|² such pairs).  
ζ_CCA(∞) → |{m : ε(m) = 1}| (number of deterministic morphisms).

*Proof:* Direct computation from definition. ∎

**[MC] Conjecture 6.9 (CCA zeta function encodes universality class):**  
The analytic continuation of ζ_CCA(s) to s ∈ ℂ (if it exists for infinite CCA sequences) may encode the universality class of the continuum limit, analogous to how the Riemann zeta function encodes prime distribution.

---

## Section 7: Phase VII — Comparison Against Existing Frameworks

| Framework | CCA relation | Basis |
|-----------|-------------|-------|
| Classical Mechanics | Weaker [T] | CCA generates deterministic automata, not Hamiltonian flows |
| Statistical Mechanics | Equivalent (discrete) [T] | CCA generates discrete Gibbs theory internally |
| Kinetic Theory | Weaker [OBS] | CCA lacks phase space |
| Transport Theory | Weaker [T] | CCA generates master equations, not PDE transport |
| General Relativity | Weaker [KR] | CCA generates causal order; metric + Einstein eq. require continuum |
| Quantum Mechanics | Incomparable [OBS] | CCA has non-commutativity + measurement but lacks ℂ amplitudes |
| Quantum Field Theory | Strictly weaker [OBS] | CCA lacks ℂ, smooth spacetime, renormalization |
| Category Theory | Special case [T] | CCA is a †-symmetric monoidal category (special type) |
| Information Theory | Equivalent (discrete) [T] | CCA is equivalent to finite information theory |

**[T] Theorem 7.1 (CCA ≡ finite information theory):**  
CCA with Ax1+Ax4+Ax5 is equivalent to a finite channel category (Choi-Jamiołkowski representation). Every finite information-theoretic object (channel, state, entropy) has a CCA counterpart and vice versa.

**[OBS] Obstruction 7.2 (CCA is strictly weaker than QM):**  
The precise obstruction is: CCA lacks ℂ-valued amplitudes, hence cannot generate quantum interference (Target 19) or complex Hilbert spaces (Target 21) without ℂ-enrichment. This makes CCA and QM **incomparable**: CCA has causal order (not in QM axioms), QM has ℂ amplitudes (not in CCA).

---

## Section 8: Phase VIII — Failure Analysis

### 8.1 Critical Failure Modes

| Missing structure | Targets blocked | Type of obstruction | Can patching fix it? |
|-------------------|-----------------|---------------------|----------------------|
| ℂ-enrichment | 18,19,21,22,27 | Fundamental | Yes — but it is an extension, not a derivation |
| Continuum limit | 3,4,6,8,9,10,12,17,25,26,27 | Fundamental | Yes — but requires external metric on CCA space |
| Phase space | 16 | Structural | Yes — but requires external product structure |
| Smooth manifold | 10,12,26 | Fundamental | Yes — but requires external ℝ-analysis |
| Renormalization | 27 | Deep structural | No known patch that is internal |

### 8.2 Extension vs. Completion vs. Replacement

**ℂ-enrichment** is an **extension**: it adds structure to CCA without contradicting it. It is clearly labeled as an external addition.

**Continuum limit** is a **completion**: it requires a metric on the space of CCAs, which is external but compatible with CCA structure. It completes CCA to a larger theory.

**Renormalization** for QFT is neither an extension nor completion of CCA — it is a structural requirement of a qualitatively different theory. It would require a **replacement** of the finite-state framework with an infinite-dimensional one.

### 8.3 What Must Not Be Silently Inserted

The following are explicitly labeled as external additions, **not** CCA derivations:
- [EXT-1] ℂ-enrichment of hom-sets
- [EXT-2] Metric on space of CCAs (for continuum limit)
- [EXT-3] Smooth manifold structure (for differential geometry)
- [EXT-4] Phase space product structure (for kinetic theory)
- [EXT-5] Renormalization procedure (for QFT)

Any claim that CCA derives quantum mechanics, QFT, or smooth spacetime without invoking one or more of [EXT-1]–[EXT-5] is false.

---

## Section 9: Final Classification

### 9.1 Target Summary

| Target | Result | Classification |
|--------|--------|---------------|
| 1 Spacetime (discrete) | Emerges | (A) |
| 2 Locality | Emerges | (A) |
| 3 Finite propagation speed | Partial | (C) |
| 4 Lorentz symmetry | Partial + conjecture | (C) |
| 5 Causal cones | Emerges | (A) |
| 6 Metric geometry | Partial + conjecture | (C) |
| 7 Dimensionality | Partial | (B) |
| 8 Fields | Fails | (C) |
| 9 Continuous limits | Fails | (C) |
| 10 Differential geometry | Fails | (C) |
| 11 Conservation laws (discrete) | Partial | (B) |
| 12 Noether structures | Fails | (C) |
| 13 Probability | Primitive (not derived) | (A)* |
| 14 Statistical mechanics | Emerges | (A) |
| 15 Transport theory (discrete) | Partial | (B) |
| 16 Kinetic theory | Fails | (C) |
| 17 Wave equations (discrete) | Partial | (C) |
| 18 Quantum amplitudes | Fails | (C) |
| 19 Interference | Impossible | (D) |
| 20 Noncommutative observables | Emerges | (A) |
| 21 Hilbert-space structure | Partial (real only) | (B) |
| 22 Unitary evolution (discrete) | Partial | (B) |
| 23 Measurement | Emerges | (A) |
| 24 Decoherence (classical) | Partial | (B) |
| 25 Classical mechanics (automata) | Partial | (B) |
| 26 Classical field theory | Fails | (C) |
| 27 Quantum field theory | Fails | (D) |
| 28 Novel regimes | Predicted | (MC) |

*Probability is a primitive, not derived — this is an honest limitation.

### 9.2 Counts

| Classification | Count | Targets |
|---------------|-------|---------|
| (A) Emerges uniquely | 6 | 1,2,5,13*,14,20,23 |
| (B) Emerges non-uniquely / partially | 8 | 7,11,15,21,22,24,25,28 |
| (C) Requires external assumptions | 12 | 3,4,6,8,9,10,12,16,17,18,26 |
| (D) Cannot emerge | 2 | 19,27 |

### 9.3 Official Result: **Result C**

> **Result C: CCA is not foundational for the full target set.**  
> One or more essential structures — specifically complex amplitudes (quantum interference, QFT) and continuous spacetime — require independent axioms that are not derivable from (O, M, ⊗, ≤, †, ε).

**The exact obstruction theorems are:**

1. **[OBS] Obstruction O1 (No complex amplitudes):** Real ε ∈ [0,1] cannot generate complex interference. Adding ℂ is an external extension.

2. **[OBS] Obstruction O2 (No continuum limit):** Finite CCA cannot generate smooth spacetime without an external convergence structure.

3. **[OBS] Obstruction O3 (No renormalization):** QFT structure is qualitatively beyond CCA even with extensions O1+O2.

### 9.4 What CCA Does Achieve

Despite Result C, CCA is a non-trivial foundational structure for:
- **Discrete causal spacetime** — genuine emergence from order axioms
- **Statistical mechanics and thermodynamics** — complete internal derivation
- **Noncommutative algebra of observables** — from monoidal composition
- **Measurement theory** — from probabilistic weights
- **Novel fractal transport regime** — genuinely new mathematics

CCA is best characterized as: **a genuine foundation for discrete probabilistic causal physics, but not for continuous, quantum, or field-theoretic physics without external enrichments.**

### 9.5 What Would Upgrade CCA to Result A

Adding [EXT-1] (ℂ-enrichment) upgrades CCA to:
- **CCA_ℂ** = †-compact symmetric monoidal category over ℂ with causal order and weight function
- This generates: quantum mechanics (Targets 18,19,21,22), complex Hilbert space, interference, unitarity

Adding [EXT-1] + [EXT-2] (continuum limit) upgrades CCA_ℂ to:
- **CCA_ℂ∞** = quantum causal structure in a Lorentzian continuum
- This generates: Targets 3,4,6,8,9,10,17 (approximately)

Even CCA_ℂ∞ does not obviously generate Target 27 (QFT with renormalization). QFT may require a fundamentally different foundation.

---

*End of cca_foundation_audit.md*  
*Version 1.0 — 2026-07-21*  
*Official Result: C*  
*All claims classified per the key in Section 0.*
