# Reversible Extension Derivation Audit
## Do Reversible Embeddings Derive M1 or M2, or Are They Independent Axioms?

**Date:** 2026-07-21
**Depends on:** substrate_structure_extension.md, reversible_substrate_audit.md
**Objective:** Determine whether any verified reversible embedding of the PRW
already contains mathematical structures that inevitably generate M1 (matrix-valued
fields, M₂(ℝ)) or M2 (Moyal star-product deformation), or whether M1 and M2 are
genuinely independent axioms that must be introduced externally.

Every statement is labelled:
- **[T]** Theorem — proven rigorously in this document
- **[KR]** Known result — established in published mathematical physics literature
- **[MC]** Mathematical consequence — follows directly from a proven theorem
- **[CJ]** Conjecture — plausible but not proven here
- **[OP]** Open problem — not resolvable within current mathematics

---

## Part I — Verified Starting State

### Section 1: Established Facts (Not Re-Derived)

The following are verified results from prior audits in this session.

**FACT A [KR, substrate_structure_audit.md Theorem S8]:**
The observable algebra of the PRW is the commutative ℝ-algebra
𝒜_PRW = C∞(ℝ, ℝ²) under pointwise multiplication.
For any two observables f, g ∈ 𝒜_PRW: f · g = g · f. (Q1 unresolved.)

**FACT B [KR, substrate_structure_audit.md Theorem S7]:**
The PRW state space at each site is the real 1-simplex Δ₁ ≅ [0,1].
The quantum two-level state space is CP¹ ≅ S². The missing degree of freedom
is the U(1) phase φ ∈ [0, 2π). (Q2 unresolved.)

**FACT C [KR, reversible_substrate_audit.md Conclusion C]:**
The following six reversible embeddings of the PRW are mathematically valid:
- R1: Mori-Zwanzig projection from Hamiltonian field theory
- R2: Bateman dual-field conservative embedding
- R3: Caldeira-Leggett oscillator bath
- R4: Reversible lattice gas automaton (RLGA)
- R5: Koopman-von Neumann (KvN) Hilbert-space reformulation
- R6: BBGKY hierarchy / BGK approximation from N-body dynamics

Each embedding resolves Q3 (T-reversal breaking is emergent from projection).
None resolves Q1 or Q2 individually.

**FACT D [KR, substrate_structure_extension.md Section 3]:**
Two minimal extensions survive the full classification:
- M1 = E2: Matrix-valued substrate fields S, J ∈ M₂(ℝ)
- M2 = E3: Moyal star-product deformation of the observable algebra

Both were introduced as additional mathematical assumptions, not derived from
any reversible embedding.

### Section 2: The Audit Question

The question is precise:

> Does any reversible embedding R1–R6 already contain mathematical structures
> that **inevitably generate** M1 or M2, i.e., are M1/M2 **derived** consequences
> of the reversible substrate, or are they **independent axioms**?

The four possible verdicts for each candidate are:

| Verdict | Meaning |
|---------|---------|
| **Derived** | The structure arises necessarily from the embedding's own axioms |
| **Mathematically equivalent** | The embedding can be rewritten to contain the structure, but it need not be |
| **Compatible** | The structure can coexist with the embedding without contradiction |
| **Externally imposed** | The structure requires new assumptions beyond the embedding |

---

## Part II — Embedding-by-Embedding Audit

### Embedding R1: Mori-Zwanzig / Caldeira-Leggett

**Setup:** The PRW is the projected dynamics of the Hamiltonian:

```
H_full = H_particle + H_bath + H_coupling
       = Σᵢ [½pᵢ²] + Σ_k [p_k²/(2m_k) + ½m_k ω_k² q_k²] + Σᵢ Σ_k c_k σᵢ q_k
```

The full phase space is Γ_full = ℝ^(2N) × ℝ^(2M) (particles + bath modes).

#### R1-A: Does R1 generate a noncommutative observable algebra?

**[T] Theorem R1-NC:** The observable algebra of the full Mori-Zwanzig system
is the Poisson algebra (C∞(Γ_full), ·, {·,·}) where · is pointwise multiplication
and {·,·} is the canonical Poisson bracket. This algebra is commutative under ·.

**Proof:** The Poisson bracket {f, g} = Σᵢ (∂f/∂qᵢ ∂g/∂pᵢ − ∂f/∂pᵢ ∂g/∂qᵢ)
is antisymmetric: {f,g} = −{g,f}. But the associative product on observables is
pointwise multiplication (f·g)(x) = f(x)g(x), which satisfies f·g = g·f for all
real-valued functions. The Poisson bracket is a Lie bracket, not the associative
product. The commutator of observables under · is identically zero. ∎

**Verdict on R1-A: Commutative [T]. M2 not derived.**

#### R1-B: Does R1 generate a complex Hilbert-space structure?

**[KR]** The Koopman-von Neumann reformulation of H_full acts on L²(Γ_full), a
complex Hilbert space. However this is a reformulation of classical mechanics —
the KvN observables are still real functions, the algebra is still commutative,
and the KvN commutators [f̂, ĝ]_KvN = 0 for all classical observables f, g.
The complex structure of L²(Γ_full) is a computational tool, not a physical
Hilbert space in the quantum sense. **No quantum Hilbert structure is generated.**

**Verdict on R1-B: KvN Hilbert space present but commutative [KR]. M1/M2 not derived.**

#### R1-C: Does R1 generate symplectic or Weyl algebra structures?

**[KR]** The phase space Γ_full is a symplectic manifold with canonical symplectic
form ω = Σᵢ dpᵢ ∧ dqᵢ. The Poisson algebra (C∞(Γ_full), {·,·}) is the classical
limit of the Weyl algebra. The Weyl algebra W(Γ_full, ω) over the same symplectic
space is the quantization of this Poisson algebra — but quantization requires
introducing ℏ externally (Groenewold-van Hove theorem, see Section III).

**[MC]** The symplectic structure of Γ_full is **compatible** with M2 (Moyal
deformation), but does not **derive** M2. The Moyal deformation requires a choice
of θ (= ℏ in quantum mechanics) which is not determined by H_full.

**Verdict on R1-C: Symplectic structure present [KR]; Weyl/Moyal compatible but not derived [MC].**

#### R1-D: Does R1 generate matrix-valued fields?

**[T]** The fields n±(x,t) projected from R1 are real scalar densities. The
projection map π: Γ_full → {n⁺, n⁻} outputs real numbers. No matrix structure
arises from this projection. **M1 not derived.**

**Verdict on R1-D: Scalar real fields only [T]. M1 not derived.**

---

### Embedding R2: Bateman Dual-Field System

**Setup:** The telegrapher equation is embedded in the conservative system:

```
(s, J, s̃, J̃) with Lagrangian density:
ℒ_B = (∂_t s̃)(∂_t s)/c² − (∂_x s̃)(∂_x s) − (1/τ)(s̃ ∂_t s − s ∂_t s̃)/(2c²)
```

The dual system (s̃, J̃) satisfies the time-reversed (anti-damped) equations.

#### R2-A: Does R2 generate a noncommutative algebra?

**[T] Theorem R2-NC:** The Bateman system has canonical coordinates
(s, π_s, s̃, π_{s̃}) where π_s = ∂ℒ_B/∂(∂_t s) = ∂_t s̃/c² − s̃/(2τc²) and
π_{s̃} = ∂ℒ_B/∂(∂_t s̃) = ∂_t s/c² + s/(2τc²). The Poisson brackets are:

```
{s(x), π_s(y)} = δ(x−y)
{s̃(x), π_{s̃}(y)} = δ(x−y)
all other brackets = 0
```

The observable algebra is C∞(Γ_B) where Γ_B is the Bateman phase space. This
algebra is commutative under pointwise multiplication. The Poisson brackets are
antisymmetric Lie brackets, not the associative product. **Q1 is not resolved.**

**Proof:** The Bateman field theory is a classical field theory with a real-valued
Lagrangian. Its observables are real-valued functionals of (s, s̃) and their
derivatives. Real-valued functions on any set commute under multiplication: f·g = g·f.
The Poisson bracket is antisymmetric but it is not the product: {f,g} ≠ f·g − g·f
in the algebraic sense — the Poisson bracket is a derivation, not a commutator in
the observable algebra. ∎

#### R2-B: Does the Bateman symplectic structure generate M2?

**[T] Theorem R2-SYM:** The Bateman phase space Γ_B = {(s, s̃, π_s, π_{s̃})} is
a symplectic manifold with form:

```
ω_B = δπ_s ∧ δs + δπ_{s̃} ∧ δs̃
```

This is a direct product of two standard symplectic planes. The Moyal deformation
of (C∞(Γ_B), ·) to (C∞(Γ_B), ⋆_θ) is **compatible** with the Bateman dynamics
(since the dynamics is linear and M2 leaves linear equations unchanged — Theorem E3b
in substrate_structure_extension.md). However, the value of θ is not determined by
the Bateman Lagrangian ℒ_B or any of its parameters (c, τ). The Bateman system
has two free parameters (c, τ); θ is a third independent parameter.

**[MC]** The Bateman system provides a symplectic scaffold on which a Moyal
deformation **could** be imposed, but does not **generate** it.

**Verdict on R2:** Commutative algebra [T]. Symplectic structure present [KR].
M2 compatible but not derived [MC]. M1 not generated [T].

---

### Embedding R3: Caldeira-Leggett Oscillator Bath

**Setup:** Identical to R1 but with the Ohmic spectral density:

```
J(ω) = 2λ ω / ω_c² · e^{−ω/ω_c}   →   K(t) = 2λδ(t) as ω_c → ∞
```

The bath Hamiltonian is explicitly:

```
H_CL = p²/(2M) + V(q) + Σ_k [p_k²/(2m_k) + ½m_k ω_k²(q_k − c_k q/m_k ω_k²)²]
```

#### R3-A: Does the bath sector generate any noncommutative structure?

**[T] Theorem R3-NC:** Each bath oscillator (q_k, p_k) has Poisson bracket
{q_k, p_k} = 1. The bath sector observable algebra is C∞(ℝ^{2M}) — commutative
under pointwise multiplication. The full C-L Hamiltonian is classical; its
observable algebra is C∞(Γ_CL) — commutative. Projecting out the bath gives
commutative scalar fields n±. **Neither M1 nor M2 arises from R3.**

**Proof:** The Caldeira-Leggett model is a classical Hamiltonian system. All
observables are real-valued functions on phase space; all such functions commute
under multiplication. The bath oscillators provide a mechanism for Markovian
friction (via the Ohmic spectral density) but not for non-commutativity. ∎

**Verdict on R3:** Equivalent to R1 in all algebraic properties.
M1 not derived [T]. M2 not derived [T].

---

### Embedding R4: Reversible Lattice Gas Automaton (RLGA)

**Setup:** A 1D lattice automaton with sites i ∈ ℤ, occupation numbers
n_i^σ ∈ {0,1} for σ ∈ {+1,−1}, and an invertible collision rule Φ:
{0,1}^{2L} → {0,1}^{2L}. The mesoscopic limit gives the PRW.

#### R4-A: Does the Boolean algebra of the RLGA generate noncommutativity?

**[T] Theorem R4-NC:** The state space of the RLGA at each site is
{0,1}² = 𝔽₂². The algebra of observables is the Boolean algebra
𝔅 = (𝔽₂², ∨, ∧, ¬). The Boolean algebra is commutative: a ∧ b = b ∧ a
for all a, b ∈ 𝔽₂. **M1 not generated.**

**Proof:** In 𝔽₂, multiplication (AND) satisfies 0·0=0, 0·1=0, 1·0=0, 1·1=1.
This is identical to ordinary real multiplication restricted to {0,1}: 0×0=0,
0×1=0×1, 1×1=1. In particular ab = ba for all a,b ∈ {0,1}. The Boolean algebra
is a commutative ring. ∎

#### R4-B: Can the RLGA collision rule generate a Clifford algebra?

**[T] Theorem R4-CLIF:** Let Φ be any invertible linear map over 𝔽₂^N.
Then Φ ∈ GL(N, 𝔽₂). The algebra generated by linear maps over 𝔽₂ is the matrix
algebra M_N(𝔽₂). For N=2: M₂(𝔽₂) is non-commutative (matrix multiplication over
𝔽₂ is non-commutative for 2×2 matrices). However, M₂(𝔽₂) is a finite algebra
(|M₂(𝔽₂)| = 2⁴ = 16 elements); it has no continuous structure and no topology.
The Clifford algebra Cl(2,0) ≅ M₂(ℝ) requires the real number field, not 𝔽₂.

**[MC]** M₂(𝔽₂) is structurally analogous to M₂(ℝ) but cannot be continuously
deformed to it: 𝔽₂ has characteristic 2 (1+1=0 in 𝔽₂), while ℝ has characteristic
0. The continuum limit of RLGA averages occupation numbers to real densities
n± ∈ [0,1] ⊂ ℝ — the matrix structure of M₂(𝔽₂) does not survive this limit.

**[T] Theorem R4-LIM:** In the mesoscopic limit of the RLGA:

```
n±(x,t) = lim_{ε→0} (1/ε) Σ_{|i-x/ε|<1} n_i^±
```

the resulting fields n± are real-valued (in ℝ) and their algebra under pointwise
multiplication is commutative. The matrix structure of the microscopic Boolean
algebra is washed out by the averaging.

**Proof:** The continuum limit involves a linear averaging operation (convolution
with a mollifier). Linear averages of commuting quantities (real numbers) are
real numbers. The averaged algebra is real and commutative. ∎

**Verdict on R4:** Microscopic Boolean algebra is commutative [T]. Any
matrix structure over 𝔽₂ does not survive the continuum limit [T].
M1 and M2 are not derived from R4.

---

### Embedding R5: Koopman-von Neumann (KvN)

**Setup:** The classical Hamiltonian H_full (from R1) is reformulated on the
Hilbert space ℋ_KvN = L²(Γ_full, dμ_Liouville) with unitary evolution
U(t) = e^{−iLt} where L = {H_full, ·} is the Liouville operator.

#### R5-A: Does the KvN Hilbert space generate quantum noncommutativity?

**[KR] (Mauro 2002, Bondar et al. 2012):** In the KvN formulation of a classical
system, the operators q̂ and p̂ act on L²(Γ) as:

```
q̂ ψ(q,p) = q · ψ(q,p)       (multiplication by coordinate)
p̂ ψ(q,p) = p · ψ(q,p)       (multiplication by momentum)
```

Both act as **multiplication operators** on the full phase space function.
Their commutator is:

```
[q̂, p̂]_KvN ψ = q·p·ψ − p·q·ψ = 0
```

since q and p are real numbers (phase-space coordinates) and real numbers commute.

**[T] Theorem R5-NC:** The KvN reformulation of any classical Hamiltonian system
produces a commutative observable algebra. The KvN commutator [q̂, p̂]_KvN = 0
identically.

**Proof:** The KvN operators are multiplication operators on L²(Γ_full). For any
two observables f, g ∈ C∞(Γ_full): [f̂, ĝ]_KvN = f̂ĝ − ĝf̂ = (fg − gf)̂ = 0
since fg = gf pointwise (real-valued functions commute under multiplication). ∎

#### R5-B: Does the KvN Hilbert space structure constitute a Hilbert-space quantum theory?

**[KR]** The KvN Hilbert space L²(Γ_full) carries a complex structure (functions
are complex-valued). The evolution is unitary. However:

1. The physical observables are **real multiplication operators** — their spectrum
   is the set of values taken by f on phase space, which is a real set.
2. The state space is positive normalized measures on Γ_full (classical probability
   distributions), not rays in the Hilbert space (quantum pure states).
3. There is no superposition of classically distinct states: a pure classical state
   is a delta measure δ(q−q₀, p−p₀), and the KvN Hilbert space contains their
   complex linear combinations, but these have no classical or quantum interpretation
   unless additional postulates are added.

**[MC]** The KvN formulation is mathematically complex-Hilbert-space-valued but
physically classical. The complex structure does not produce quantum interference,
entanglement, or non-commutativity without additional assumptions.

**Verdict on R5:** KvN provides a Hilbert space but with commutative observable
algebra [T, KR]. Neither M1 nor M2 is generated. The complex structure of KvN
is **compatible** with M2 but does not derive it.

---

### Embedding R6: BBGKY / BGK

**Setup:** N-body Hamiltonian H_N projected via BBGKY to the one-particle
distribution f₁(x, σ, t); BGK approximation gives the PRW directly.

#### R6-A: Algebra of the BBGKY projected system

**[T] Theorem R6-NC:** The one-particle distribution function f₁(x,σ,t) ∈ ℝ for
each (x,σ,t). The observable algebra on the projected system is C∞(ℝ×{±1}×ℝ⁺, ℝ)
— commutative. The N-body Hamiltonian H_N has a commutative Poisson algebra
(by the same argument as R1). The BGK collision approximation replaces the
two-particle collision integral with a relaxation term — this is a scalar operation
on real-valued densities and does not introduce matrix structure or non-commutativity.

**Verdict on R6:** Commutative algebra throughout [T]. M1 and M2 not generated.

---

## Part III — The Central Obstruction Theorems

### Section 1: The Commutativity Preservation Theorem

**[T] Theorem OBS-1 (Commutativity is preserved under projection):**
Let 𝒮_full be any classical dynamical system (Hamiltonian, automaton, or stochastic)
whose observable algebra 𝒜_full is commutative. Let π: States(𝒮_full) → States(𝒮_sub)
be any surjective projection (coarse-graining, marginalization, or conditional
expectation). Then the observable algebra 𝒜_sub of the projected system is commutative.

**Proof:**
Let f, g ∈ 𝒜_sub be observables of the projected system. They are functions of
π(state), i.e., f = F∘π and g = G∘π for some functions F, G on States(𝒮_sub).
The product of observables in 𝒜_sub is (fg)(state) = f(state)·g(state) = F(π(state))·G(π(state)).
Since · is commutative (pointwise multiplication of real numbers):
fg = F(π(·)) · G(π(·)) = G(π(·)) · F(π(·)) = gf.
Thus 𝒜_sub is commutative. ∎

**[MC] Corollary OBS-1a:** Since every reversible embedding R1–R6 has a commutative
observable algebra 𝒜_full (proven individually above), and the PRW is obtained by
projection π from each embedding, the projected PRW observable algebra is commutative.
This confirms FACT A and provides a structural explanation: commutativity propagates
downward through projections.

**[MC] Corollary OBS-1b:** No coarse-graining, marginalization, or projection of
any system in R1–R6 can produce a non-commutative algebra. Therefore:
- **M1 (non-commutative matrix algebra M₂(ℝ)) cannot be derived from R1–R6.**
- **M2 (non-commutative Moyal algebra) cannot be derived from R1–R6.**

---

### Section 2: The Groenewold-van Hove Obstruction

**[KR] Theorem OBS-2 (Groenewold-van Hove, 1946/1951):**
There is no map Q: C∞(ℝ²ⁿ) → operators on a Hilbert space that simultaneously:
1. Satisfies Q(f·g) = Q(f)Q(g) (algebra homomorphism),
2. Satisfies Q({f,g}) = (i/ℏ)[Q(f), Q(g)] (quantization of Poisson bracket),
3. Is irreducible (acts irreducibly on the Hilbert space),
4. Holds for all polynomials of degree > 2.

**[MC] Corollary OBS-2a:** The classical Poisson algebra of any embedding in R1–R6
cannot be fully and consistently mapped to a non-commutative operator algebra
(quantum observable algebra) by any quantization procedure that is simultaneously
an algebra homomorphism and a Poisson-bracket-to-commutator map. The
Groenewold-van Hove theorem implies that quantization always requires a choice
— specifically, an ordering prescription — that goes beyond the classical data.

**[MC] Corollary OBS-2b:** Even if one attempts to "derive" M2 from the symplectic
structure of a reversible embedding, the Moyal parameter θ is a free parameter not
determined by the classical system. The classical Poisson algebra is the θ → 0 limit
of the Moyal algebra for any θ. The value of θ is genuinely new information.

---

### Section 3: The Stone-von Neumann Uniqueness Theorem

**[KR] Theorem OBS-3 (Stone-von Neumann, 1931/1932):**
Let (q̂ᵢ, p̂ᵢ) be self-adjoint operators on a Hilbert space ℋ satisfying the
Weyl form of the canonical commutation relations:
    e^{isq̂} e^{itp̂} = e^{−ist} e^{itp̂} e^{isq̂}   for all s, t ∈ ℝ.
Then ℋ ≅ L²(ℝⁿ) and (q̂ᵢ, p̂ᵢ) are unitarily equivalent to the Schrödinger
representation: q̂ᵢ = multiplication by xᵢ, p̂ᵢ = −iθ ∂/∂xᵢ.

**[MC] Corollary OBS-3a:** Any non-commutative algebra generated on a Hilbert space
from the reversible substrate must satisfy the CCR. But the CCR require introducing
ℏ (or θ) explicitly as a new constant — it is not determined by the classical
Hamiltonian H_full, the coupling constants c_k, or the collision rates λ.

**[MC] Corollary OBS-3b:** The KvN Hilbert space L²(Γ_full) is not a representation
of the CCR algebra (since KvN commutators vanish). The Stone-von Neumann theorem
applies to the quantum CCR, not to the classical KvN algebra. The gap between KvN
and quantum mechanics is precisely the step from [q̂, p̂]_KvN = 0 to [q̂, p̂]_QM = iθ,
which requires the external introduction of θ.

---

### Section 4: The Algebra-Generation Impossibility Theorem

**[T] Theorem OBS-4 (Main Result):**
Neither M1 nor M2 can be derived from any of the verified reversible embeddings
R1–R6 of the PRW. Both M1 and M2 are genuinely independent axioms.

**Proof:**

Let 𝒮 ∈ {R1, R2, R3, R4, R5, R6} be any reversible embedding. We show that
neither M1 nor M2 can arise as a derived consequence.

**Step 1: All embeddings have commutative observable algebras.**
- R1 (Mori-Zwanzig): 𝒜 = C∞(Γ_full) — commutative [Theorem R1-NC].
- R2 (Bateman): 𝒜 = C∞(Γ_B) — commutative [Theorem R2-NC].
- R3 (Caldeira-Leggett): 𝒜 = C∞(Γ_CL) — commutative [Theorem R3-NC].
- R4 (RLGA): 𝒜 = Boolean algebra 𝔅 — commutative [Theorem R4-NC]; continuum
  limit is commutative [Theorem R4-LIM].
- R5 (KvN): 𝒜 = multiplication operators on L²(Γ_full) — commutative [Theorem R5-NC].
- R6 (BBGKY): 𝒜 = C∞(ℝ×{±1}×ℝ⁺) — commutative [Theorem R6-NC].

**Step 2: Non-commutativity cannot arise by projection.**
By Theorem OBS-1, any projection of a commutative algebra is commutative.
The PRW is a projection of each embedding. Any further structure built on the
PRW starting from a commutative algebra remains commutative.

**Step 3: M1 requires a new assumption.**
M1 states that the substrate fields S, J take values in M₂(ℝ) (non-commutative).
No embedding in R1–R6 has matrix-valued fields in its state space. The projection
maps π: Γ → {n⁺, n⁻} output real scalars. Introducing M₂(ℝ)-valued fields
requires explicitly changing the value type of the substrate fields — a new axiom
not entailed by R1–R6.

**Step 4: M2 requires a new free parameter.**
M2 states that the observable algebra is deformed to the Moyal algebra 𝒜_θ.
The deformation parameter θ is not present in any embedding: neither the
Mori-Zwanzig memory kernel K(t), nor the Bateman dual Lagrangian ℒ_B, nor the
Caldeira-Leggett coupling constants c_k, nor the RLGA collision rule Φ, nor the
BBGKY hierarchy, determines a value of θ. By Corollary OBS-2b, the classical
Poisson algebra is the θ → 0 limit of 𝒜_θ for any θ, so no classical substrate
singles out a particular θ > 0. Introducing θ ≠ 0 requires a new assumption.

**Conclusion:** M1 and M2 are both genuinely independent axioms relative to the
reversible substrate R1–R6. ∎

---

### Section 5: Are M1 and M2 Related to Each Other?

**[KR] Theorem OBS-5 (M1 and M2 are independent but compatible):**
M1 (matrix-valued fields M₂(ℝ)) and M2 (Moyal deformation) are logically
independent extensions: neither implies the other, but they are compatible
(can coexist without contradiction).

**Proof of independence:**
- M1 does not imply M2: one can have matrix-valued transport fields S,J ∈ M₂(ℝ)
  with ordinary matrix multiplication (not Moyal). The Moyal product requires
  a symplectic plane and a deformation parameter θ — neither is supplied by
  matrix-valued transport fields alone.
- M2 does not imply M1: the Moyal deformation acts on the (s,J) phase space
  algebra (functions of two real variables). It does not introduce matrix-valued
  fields; the "fields" s(x) and J(x) remain scalar-valued even in 𝒜_θ.

**Proof of compatibility:**
One can simultaneously deform the matrix-valued field algebra (M1) with a Moyal
product (M2) to obtain a noncommutative geometry on M₂(ℝ)-valued functions —
this is the framework of noncommutative field theory (Connes 1994). The result
contains both M1 and M2 as sub-structures. ∎

**[MC] Corollary OBS-5a:** The minimal extension that resolves both Q1 and Q2
requires at least one of M1 or M2. They are both minimal in the sense of
Theorem MIN (substrate_structure_extension.md Section 4). Neither is derivable
from the other or from the classical reversible substrate.

---

## Part IV — Weakest Assumptions for Each Extension

### Section 1: Weakest Assumptions to Force M1

**[T] Theorem WEAK-M1:** The weakest additional assumption that forces M1 is:

> **Assumption A-M1:** The substrate density field s(x,t) and flux field J(x,t)
> are valued in a non-commutative associative unital real algebra 𝒜 such that
> the trace map Tr: 𝒜 → ℝ recovers the PRW scalar fields.

Under this assumption alone, M₂(ℝ) is the minimal choice of 𝒜 (by the
Artin-Wedderburn theorem: the smallest non-commutative semisimple real associative
algebra has dimension 4, and M₂(ℝ) is the unique such algebra up to isomorphism).

**Proof of minimality:**
- ℝ (dim 1 over ℝ): commutative. Excluded.
- ℂ (dim 2 over ℝ): commutative field. Excluded.
- ℝ⊕ℂ (dim 3 over ℝ): reducible — not simple. Excluded.
- M₂(ℝ) (dim 4 over ℝ): non-commutative, simple. **Minimal.**
  (Proof: [ab, ba] ≠ 0 for generic a,b ∈ M₂(ℝ); e.g., a=[[0,1],[0,0]], b=[[0,0],[1,0]]
   gives ab=[[1,0],[0,0]] ≠ ba=[[0,0],[0,1]].)
- ℍ (dim 4 over ℝ): non-commutative, but as large as M₂(ℝ) — not smaller. ∎

**[MC]** A-M1 is a single assumption (non-commutativity + trace recovery).
No assumption about quantum mechanics, Hilbert spaces, or operators is needed.

---

### Section 2: Weakest Assumptions to Force M2

**[T] Theorem WEAK-M2:** The weakest additional assumption that forces M2 is:

> **Assumption A-M2:** The observable algebra of the substrate is a deformation
> of C∞(ℝ², ℝ) (the (s,J) phase-space algebra) by a constant antisymmetric
> bivector θ^{ij} = θ ε^{ij} with θ ≠ 0, where the deformation is required to
> be a *-algebra with associative star-product.

Under this assumption alone, the unique (up to isomorphism) formal deformation
of C∞(ℝ²) by a constant symplectic structure is the Moyal algebra 𝒜_θ
(Kontsevich 1997, applied to the flat symplectic case).

**Proof of minimality:**
- θ = 0: commutative. Excluded.
- θ ≠ 0 constant: uniquely (up to equivalence) gives the Moyal product
  [KR] (Kontsevich's formality theorem for constant Poisson structures reduces
  to the Moyal-Weyl product). Any other associative deformation with the same
  leading term is equivalent. M2 is the unique minimal deformation. ∎

**[MC]** A-M2 introduces one free parameter θ ∈ ℝ\{0}. No assumption about ℏ,
Hilbert spaces, or quantum observables is needed.

---

### Section 3: Can Any Structural Feature of R1–R6 Motivate A-M1 or A-M2?

**[CJ] Conjecture MOTIV-1:** The symplectic structure of the reversible embeddings
R1, R2, R3 (Hamiltonian systems on symplectic manifolds) is **necessary** for
M2 to be well-defined (a Moyal deformation requires a symplectic form ω to define
the antisymmetric bivector θ^{ij}), but it is not **sufficient** to fix θ ≠ 0.

**[T] Theorem MOTIV-2:** The symplectic structure of R1–R3 is necessary but not
sufficient for M2.

**Proof:**
- Necessary: The Moyal product on ℝ^{2n} requires a symplectic form ω to define
  the bivector θ^{ij} = θ (ω⁻¹)^{ij}. Without a symplectic structure, the Moyal
  product is not well-defined. The reversible embeddings R1, R2, R3 all have
  symplectic structures (Hamiltonian systems). ✓ (Necessary condition met.)
- Not sufficient: The symplectic form determines the **direction** of the
  star-commutator but not the **magnitude** θ. The classical Poisson bracket
  corresponds to θ → 0; for any θ > 0 the Moyal algebra is a valid deformation.
  The classical data (H_full, coupling constants c_k, λ) do not determine which
  θ ∈ (0,∞) to choose. ∎

**[CJ] Conjecture MOTIV-3:** There may exist a **dimensional analysis** argument
relating θ to the parameters of the reversible substrate (specifically, the
lattice spacing ε of R4 or the minimum bath frequency ω_min of R1/R3). If θ ~ ε
or θ ~ ℏ_eff = some combination of (c, λ, ε), this would provide a physical
motivation for a specific value of θ. However, dimensional analysis alone does
not constitute a derivation — it is a consistency check, not a theorem.

---

## Part V — Summary and Final Verdict

### Section 1: Embedding × Structure Matrix

| Embedding | Noncomm. algebra | Complex Hilbert | Clifford | Symplectic | Weyl | Moyal | Matrix fields |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| R1 (Mori-Zwanzig) | No [T] | KvN only [KR] | No | **Yes** [KR] | Compatible [MC] | Compatible [MC] | No [T] |
| R2 (Bateman) | No [T] | No | No | **Yes** [T] | Compatible [MC] | Compatible [MC] | No [T] |
| R3 (Caldeira-Leggett) | No [T] | No | No | **Yes** [KR] | Compatible [MC] | Compatible [MC] | No [T] |
| R4 (RLGA) | No [T] | No | No | No | No | No | No [T] |
| R5 (KvN) | No [T] | **Yes** (classical) [KR] | No | Yes [KR] | Compatible [MC] | Compatible [MC] | No [T] |
| R6 (BBGKY) | No [T] | No | No | Yes [KR] | Compatible [MC] | Compatible [MC] | No [T] |

### Section 2: Final Audit Verdict

**[T] Main Theorem (Theorem OBS-4):** Neither M1 nor M2 is derivable from any
reversible embedding R1–R6 of the PRW. Both are genuinely independent axioms.

**Detailed status of each embedding:**

| Embedding | M1 status | M2 status | Obstruction |
|-----------|-----------|-----------|-------------|
| R1 | Externally imposed | Externally imposed | Commutative Poisson algebra [T R1-NC]; θ undetermined [OBS-2b] |
| R2 | Externally imposed | Externally imposed | Commutative field algebra [T R2-NC]; θ undetermined [OBS-2b] |
| R3 | Externally imposed | Externally imposed | Identical to R1 [T R3-NC] |
| R4 | Externally imposed | Externally imposed | Boolean algebra commutative [T R4-NC]; no continuous phase [T R4-LIM] |
| R5 | Externally imposed | Externally imposed | KvN commutators zero [T R5-NC, KR]; θ undetermined |
| R6 | Externally imposed | Externally imposed | Commutative one-particle algebra [T R6-NC] |

**The precise location of the obstruction (same for all embeddings):**

1. Every reversible embedding has a classical commutative observable algebra
   (pointwise multiplication of real-valued functions on phase space or state space).
2. Commutativity is preserved under projection and coarse-graining (Theorem OBS-1).
3. Non-commutativity (required for both M1 and M2) cannot be generated by any
   sequence of classical operations on a commutative algebra (Theorem OBS-1).
4. The Groenewold-van Hove theorem (OBS-2) implies that even if one attempts to
   "quantize" the symplectic structure of R1–R3, the deformation parameter θ
   (Moyal) or the matrix type (M1) must be specified externally.
5. The Stone-von Neumann theorem (OBS-3) confirms that any non-commutative
   Hilbert-space structure requires the CCR with an externally given θ = ℏ.

**[T] Theorem AXIOM-STATUS:**
M1 and M2 are axioms in the precise logical sense: they are statements that are:
- Consistent with all reversible embeddings R1–R6 (no contradiction).
- Not provable from the axioms of R1–R6 (by Theorem OBS-4).
- Independent of each other (by Theorem OBS-5).
- Each individually sufficient to resolve Q1 and Q2 (from substrate_structure_extension.md).

---

## Appendix: Label Index

| Label | Statement |
|-------|-----------|
| [T] OBS-1 | Commutativity preserved under projection |
| [KR] OBS-2 | Groenewold-van Hove obstruction |
| [KR] OBS-3 | Stone-von Neumann uniqueness |
| [T] OBS-4 | M1 and M2 cannot be derived from R1–R6 |
| [KR] OBS-5 | M1 and M2 are independent but compatible |
| [T] WEAK-M1 | Weakest assumption forcing M1 = A-M1 |
| [T] WEAK-M2 | Weakest assumption forcing M2 = A-M2 |
| [T] MOTIV-2 | Symplectic structure necessary but not sufficient for M2 |
| [T] AXIOM-STATUS | M1 and M2 are independent axioms |
| [T] R1-NC through R6-NC | Each embedding has commutative algebra |
| [T] R4-LIM | RLGA matrix structure washed out by continuum limit |
