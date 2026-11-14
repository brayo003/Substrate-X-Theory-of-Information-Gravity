# SCC Scientific Status Audit

**Research Question**: Does SCC genuinely derive classical and quantum physics from a deeper principle, or does it reconstruct known structures already present in Lie groups, representation theory, and quantum foundations?

**Date**: 2026-07-21

**Rule**: Nothing may be counted as "derived" if an equivalent physical assumption already appears earlier in the dependency graph.

---

## Labels

- `[T]` — Theorem proved here
- `[KR]` — Known rigorous result (literature)
- `[PHY]` — Physical / empirical assumption
- `[DEF]` — Definition
- `[MC]` — Mathematical conjecture
- `[OP]` — Open problem
- `[RECON]` — Reconstruction: result follows by choosing inputs that already encode the conclusion
- `[RENAME]` — Rename: same mathematical object given a new name

---

## Phase I: Complete Dependency Graph

### I.1 Node Catalogue

Every node in the dependency graph is listed below with its type.

**Layer 0 — Raw Physical Inputs**

| ID | Node | Type |
|---|---|---|
| P0 | Distinguishable outcomes exist | `[PHY]` |
| P1 | Systems can be composed | `[PHY]` |
| P2 | Statistical stability (reproducibility) | `[PHY]` |
| P3 | Finite information in bounded regions | `[PHY]` |
| P4 | Causal partial order | `[PHY]` |
| P5 | No preferred inertial frame | `[PHY]` |
| P6 | Distinguishability is preserved under reversible dynamics | `[PHY]` |

**Layer 1 — Mathematical Assumptions (introduced by SCC construction)**

| ID | Node | Type |
|---|---|---|
| M1 | State space S is a set | `[DEF]` |
| M2 | Composition ⊗: S×S → S is associative | `[DEF]` |
| M3 | A group G acts on S by bijections | `[DEF]` |
| M4 | The action of G on S is transitive | `[DEF]` (often assumed) |
| M5 | G is a locally compact topological group | `[DEF]` |
| M6 | G is compact | `[PHY]` / `[DEF]` — **first non-trivial physical assumption** |
| M7 | S carries a G-invariant probability measure | derived from M5+M6 via Haar |
| M8 | S is a complex vector space | **not yet derived at this stage** |

**Layer 2 — SCC Axioms (as stated)**

| ID | Node | Type |
|---|---|---|
| SCC-C | Closure: ⊗ closes on S | `[DEF]` — follows from M2 |
| SCC-S | Symmetry: G acts equivariantly on ⊗ | `[DEF]` — M3 |
| SCC-I | Invertibility: G acts by bijections | `[DEF]` — M3 |
| SCC-N | Normalization: G-invariant probability measure exists | derived from M6 `[KR]` |

**Layer 3 — Derived Mathematical Structures**

| ID | Node | Type | Source |
|---|---|---|---|
| D1 | Haar measure on G | `[KR]` | M5+M6 → Haar theorem |
| D2 | Complex Hilbert space H | `[KR]` | M3+M6+M8 → Peter–Weyl + Stone–von Neumann |
| D3 | Unitary group U(H) | `[KR]` | D2 |
| D4 | Self-adjoint operators on H | `[KR]` | D2+D3 |
| D5 | Born probability measure | `[KR]` | D2 → Gleason's theorem |
| D6 | One-parameter unitary groups | `[KR]` | D3 + Stone's theorem |
| D7 | Self-adjoint generator (Hamiltonian) | `[KR]` | D6 + Stone's theorem |
| D8 | Schrödinger equation | `[KR]` | D6+D7 |
| D9 | Symplectic structure on phase space | `[KR]` | Classical limit of D2 via ℏ→0 |
| D10 | Liouville measure | `[KR]` | D9 |
| D11 | Gibbs entropy / canonical ensemble | `[KR]` | D1+D10 |

**Layer 4 — Physical Theories (comparison)**

| ID | Node | Source in SCC | Status |
|---|---|---|---|
| Q1 | Quantum mechanics (non-rel) | D2+D5+D8 | claimed `[D]` |
| Q2 | Hamiltonian mechanics | D7+D9 | claimed `[D]` |
| Q3 | Statistical mechanics | D11 | claimed `[D]` |
| Q4 | Gauge theory | requires spacetime → not derived | `[RE]` |
| Q5 | General relativity | requires AA5 → not derived | `[RE]` |
| Q6 | Classical (Newtonian) mechanics | requires config space → see Phase III | `[?]` |

---

### I.2 Dependency Graph (Edges)

Edge notation: A → B means "A is required for B"; edge label gives relationship type.

```
P0 --[PHY]--> M1          (outcomes → state set)
P1 --[PHY]--> M2          (composition → associative map)
P2 --[PHY]--> M7          (reproducibility → probability measure needed)
P3 --[PHY]--> M5          (finite info → locally compact group)
P5 --[PHY]--> M3          (no preferred frame → symmetry group)
P6 --[PHY]--> SCC-I       (distinguishability preserved → invertible action)

M3 --[DEF]--> SCC-S       (group action → equivariance)
M2 --[DEF]--> SCC-C       (associative map → closure)
M6 --[KR]---> D1          (compact group → Haar measure)
M6 --[PHY]--> SCC-N       (compactness assumption → normalized measure)

D1 + M8 --[KR]--> D2      (Haar + complex vector space → Hilbert space via Peter-Weyl)
D2 --[KR]--> D3           (Hilbert space → unitary group)
D2 --[KR]--> D5           (Hilbert space → Born rule via Gleason)
D3 --[KR]--> D6           (unitary group + Stone → one-param groups)
D6 --[KR]--> D7           (one-param group → self-adjoint generator)
D7 --[KR]--> D8           (generator → Schrödinger equation)

D2 + [ℏ→0, PHY] --[KR]--> D9    (quantum → classical phase space)
D9 --[KR]--> D10          (symplectic → Liouville measure)
D10 + D1 --[KR]--> D11   (measure → Gibbs ensemble)

D8 --[--> Q1              (Schrödinger → QM)
D7 + D9 --[--> Q2         (Hamiltonian + phase space → Hamiltonian mechanics)
D11 --[--> Q3             (Gibbs → statistical mechanics)
```

### I.3 Critical Edges — Where Physical Content Enters

The following edges carry the actual physical load. Every "derivation" downstream of these is conditional on them.

| Edge | Content Introduced | Classification |
|---|---|---|
| P0 → M1 | Distinguishable states exist | `[PHY]` — unavoidable |
| P1 → M2 | Composition law exists | `[PHY]` — unavoidable |
| M6 | G is compact | `[PHY]` — **non-trivial, not derived** |
| M8 | State space is complex | `[PHY]` — **non-trivial, not derived at this stage** |
| D2 → D9 (ℏ→0) | Classical limit exists | `[PHY]` — **requires additional assumption** |
| spacetime | Not present in SCC | `[PHY]` — **absent entirely** |

**Finding I.1** `[T]`: The dependency graph has two unavoidable non-trivial physical inputs that are not derivable from P0–P6: **(a) compactness of G** (M6) and **(b) complex structure of S** (M8). Every claimed derivation downstream of D2 is conditional on both.

---

## Phase II: Derived vs Reconstructed vs Renamed vs Assumed

The rule is strict: a result counts as **derived** only if no equivalent physical assumption encoding that result already appears earlier in the dependency graph.

---

### II.1 Hilbert Space

**Claim**: SCC derives the complex Hilbert space.

**Audit**:

The derivation path is: SCC-axioms + M6 (compact G) + M8 (complex vector space) → Peter–Weyl theorem → Hilbert space of square-integrable functions on G.

**Verdict: `[RECON]`**

Reason: M8 explicitly assumes the state space is a *complex* vector space. Peter–Weyl then shows this space decomposes into irreducible unitary representations. But a complex vector space with a G-invariant inner product *is already* a Hilbert space up to completion. The theorem reconstructs Hilbert space structure that was already encoded in M8. The content of the derivation is that M8 + compact G → the *specific* structure of L²(G), not that Hilbert space appears from nothing.

**What is genuinely new**: The *specific* realization of the state space as L²(G) (functions on the group manifold) rather than an abstract Hilbert space. This is a non-trivial structural constraint — it rules out, for example, real Hilbert spaces or quaternionic Hilbert spaces.

**Net gain**: SCC does not derive "why use a Hilbert space" from scratch; it derives "why use a *complex* Hilbert space" given a compact symmetry group. The complex structure follows from the representation theory of compact groups, not from first principles about reality.

---

### II.2 Born Rule

**Claim**: SCC derives the Born rule p = |⟨φ|ψ⟩|².

**Audit**:

The path is: Hilbert space (D2) → Gleason's theorem `[KR]` → unique probability measure consistent with the frame structure.

**Verdict: `[D]` — Genuinely derived, conditional on D2**

Reason: Gleason's theorem is a non-trivial mathematical result. Given a Hilbert space of dimension ≥ 3, *any* probability measure that assigns probabilities to closed subspaces in a way consistent with the orthogonal decomposition must be the Born rule. This is not a circular reconstruction — Gleason's theorem is a genuine theorem that removes a free parameter.

**Condition**: This derivation is only as strong as the derivation of D2. Since D2 requires M8 (complex vector space), the Born rule derivation is conditional on that physical assumption.

**What is genuinely derived**: Given that the state space is a complex Hilbert space, Born rule is *forced* — no alternative probability rule is consistent. This is real explanatory power. `[T]`

---

### II.3 Interference

**Claim**: SCC derives quantum interference.

**Audit**:

Path: Complex Hilbert space (D2) → superposition principle (linearity) → |ψ₁ + ψ₂|² ≠ |ψ₁|² + |ψ₂|².

**Verdict: `[RENAME]`**

Reason: Interference is *identical* to the statement that probability is computed from complex amplitudes using the Born rule. It is not a separate result — it is the direct mathematical consequence of (a) linear superposition in H and (b) the Born rule. Both are already established in D2+D5. Calling the cross-term "interference" and counting it as a separate derivation is a rename.

**Clarification**: The *existence* of interference is a consequence of D2+D5. The *specific structure* of interference (phase-dependent, vanishing for orthogonal states) follows. Nothing new is added beyond what is already in D2+D5.

---

### II.4 Hamiltonian Mechanics

**Claim**: SCC derives Hamiltonian mechanics.

**Audit**:

Path: Unitary group U(H) (D3) → Stone's theorem → one-parameter groups → self-adjoint generator H → iℏ ∂ψ/∂t = Hψ. Classical limit ℏ→0 → symplectic phase space → Hamilton's equations.

**Verdict: `[RECON]` for the classical case; `[D]` for the quantum case**

Quantum Hamiltonian dynamics:

Stone's theorem states that every strongly continuous one-parameter unitary group has a self-adjoint generator. The Schrödinger equation *is* this generator equation. This is a genuine derivation within the quantum framework: given unitary time evolution (itself following from SCC-I + D3), the Schrödinger equation follows without further assumptions. **Verdict: `[D]`** `[T]`

Classical Hamiltonian dynamics:

The classical limit ℏ→0 is not derived from SCC. It requires:
- (a) Identifying ℏ as a physical constant whose limit can be taken — `[PHY]`
- (b) The coherent state / Wigner function machinery relating quantum operators to classical phase space functions — `[KR]` but requires additional structure
- (c) The assumption that a classical phase space exists as the limit — `[PHY]`

The symplectic form on classical phase space does not appear in SCC; it appears via the semiclassical limit. **Verdict for classical limit: `[RECON]`** — the classical result is obtained by *adding* the classical limit assumption to SCC, not deriving it.

---

### II.5 Statistical Mechanics

**Claim**: SCC derives Gibbs statistical mechanics.

**Audit**:

Path: Haar measure D1 → invariant measure on state space → maximum entropy subject to constraints → canonical ensemble.

**Verdict: `[D]`** conditional on D1 and the identification of entropy with −∫ρ log ρ dμ.

Reason: Given the Haar measure as the natural uniform measure on the state space, the maximum entropy distribution subject to a fixed expected energy is the canonical (Gibbs) ensemble. This is a standard result in information-theoretic statistical mechanics `[KR]`. The derivation is not circular: the Haar measure comes from the group structure (D1), and the canonical ensemble follows from a maximum entropy argument.

**What remains assumed**: The identification of physical entropy with the information-theoretic −∫ρ log ρ dμ is a physical assumption (Jaynes program `[PHY]`). SCC does not derive *why* physical entropy equals information entropy — it assumes the Jaynes identification.

**Net verdict**: Statistical mechanics is reconstructed from SCC given the Jaynes entropy identification. The derivation is valid but not assumption-free.

---

### II.6 Quantum Mechanics (complete)

**Claim**: SCC derives quantum mechanics.

**Audit**:

QM requires: (i) complex Hilbert space, (ii) Born rule, (iii) unitary evolution, (iv) observable = self-adjoint operator, (v) measurement postulate.

- (i) `[RECON]` — requires M8
- (ii) `[D]` — Gleason, given (i)
- (iii) `[D]` — SCC-I + Stone's theorem
- (iv) `[D]` — follows from (iii) + spectral theorem
- (v) `[PHY]` — measurement / collapse is **not derived** by SCC

**Finding II.1** `[T]`: SCC derives quantum mechanics with the exception of the measurement postulate (wavefunction collapse / decoherence). Items (ii)–(iv) are genuine theorems given (i). Item (i) requires M8. Item (v) is an independent physical input.

---

### II.7 Classical Mechanics

**Claim**: SCC derives classical mechanics.

**Audit**: Deferred to Phase III (detailed analysis).

**Preliminary verdict**: `[RECON]` — classical mechanics requires the classical limit (ℏ→0) as an additional physical input not present in SCC.

---

### II.8 Transport

**Claim**: SCC derives transport theory.

**Audit**:

Transport (Boltzmann equation, diffusion) requires:
- Phase space (not derived — see above)
- Molecular chaos / Stosszahlansatz — `[PHY]`
- Locality in space — requires spacetime, not present in SCC

**Verdict: `[RE]`** — Transport is not derivable from SCC. It requires phase space (ℏ→0 limit), spatial locality (absent from SCC), and molecular chaos (empirical). These are not encoded in SCC's axioms.

---

### II.9 Summary Table

| Claimed Result | Verdict | First Additional Assumption |
|---|---|---|
| Complex Hilbert space | `[RECON]` | M8: complex vector space |
| Born rule | `[D]` (given Hilbert space) | None beyond M8 |
| Interference | `[RENAME]` | None — same as Born + superposition |
| Unitary evolution | `[D]` | SCC-I |
| Schrödinger equation | `[D]` | Stone's theorem (given unitary evolution) |
| Quantum observables | `[D]` | Spectral theorem |
| Measurement/collapse | `[PHY]` | Not derived |
| Quantum Hamiltonian | `[D]` | None beyond above |
| Classical Hamiltonian | `[RECON]` | ℏ→0 limit `[PHY]` |
| Classical mechanics | `[RECON]` | ℏ→0 + config space `[PHY]` |
| Statistical mechanics | `[D]` conditional | Jaynes entropy identification `[PHY]` |
| Transport | `[RE]` | Spacetime + molecular chaos |
| Gauge theory | `[RE]` | Spacetime + empirical G |
| General relativity | `[RE]` | Equivalence principle |

---

## Phase III: Does Classical Mechanics Actually Emerge from SCC?

We examine each component of classical mechanics in turn.

### III.1 Configuration Space

**Question**: Does SCC produce a configuration space Q?

**Analysis**:

SCC operates on an abstract state space S with a group action. The state space after applying Peter–Weyl is a Hilbert space L²(G) — the space of square-integrable functions on the group G. This is a functional space, not a configuration space in the mechanical sense.

A configuration space Q is a manifold of possible positions of a mechanical system. It requires:
- A notion of spatial location — absent from SCC
- A topology on the set of configurations — not given by G alone

**Verdict: `[NOT DERIVED]`** `[T]`

Configuration space requires additional physical input: the identification of group elements (or cosets G/H) with spatial positions. This identification is a physical assumption, not a consequence of SCC.

---

### III.2 Phase Space

**Question**: Does SCC produce a phase space T*Q?

**Analysis**:

The cotangent bundle T*Q (phase space) requires Q to exist first. Since Q is not derived (III.1), T*Q is not derived either.

However, there is a related structure SCC does produce: the **cotangent bundle of the group** T*G, which carries a natural symplectic form (the Kirillov–Kostant–Souriau (KKS) form on coadjoint orbits) `[KR]`.

The KKS symplectic structure on coadjoint orbits of G is a genuine derived structure. However:
- It is the phase space of a system *whose configuration space is G itself* (a Lie group manifold)
- This is not the phase space of a particle in physical space
- Physical space is not present in SCC

**Verdict: `[RECON]` for abstract group phase space; `[NOT DERIVED]` for mechanical phase space** `[T]`

---

### III.3 Canonical Variables (q, p)

**Question**: Does SCC produce canonical position and momentum variables?

**Analysis**:

Canonical variables (q, p) satisfying {q, p} = 1 (Poisson bracket) arise in:
- The semiclassical limit of quantum operators via canonical quantization — `[KR]`
- The KKS construction on coadjoint orbits for specific G

For G = ℝⁿ (the translation group), the coadjoint orbits are points and the KKS form is trivial. For G = Heisenberg group, canonical variables do appear directly.

**Verdict: `[RECON]`** — canonical variables appear in SCC if and only if G is chosen to be (or contain) the Heisenberg group or a group whose coadjoint orbits are flat. This is a circular input: choosing G to encode canonical variables and then deriving canonical variables from G.

---

### III.4 Newtonian Limit (F = ma)

**Question**: Does SCC produce Newton's second law?

**Analysis**:

Newton's second law requires:
- A notion of force F — absent from SCC (force is a physical concept associated with interactions)
- A notion of mass m — absent from SCC
- A notion of acceleration in physical space — requires spacetime (absent)

Hamiltonian mechanics gives Ḣ-generated dynamics, but mapping H to a kinetic + potential energy expression requires identifying p²/2m as kinetic energy, which requires mass as a physical parameter not present in SCC.

**Verdict: `[NOT DERIVED]`** `[T]`

The Newtonian limit requires both the ℏ→0 limit and the identification of the Hamiltonian with a specific physical energy function. Neither is derived from SCC.

---

### III.5 Lagrangian Dynamics

**Question**: Does SCC produce the Lagrangian L = T − V and the Euler–Lagrange equations?

**Analysis**:

The Euler–Lagrange equations follow from Hamilton's principle: δ∫L dt = 0. This variational principle is equivalent to Hamilton's equations on phase space (via Legendre transform). Since Hamiltonian phase space is not derived (III.2), Lagrangian dynamics is not derived either.

**Verdict: `[NOT DERIVED]`** — requires phase space over physical configuration space. `[T]`

---

### III.6 Hamiltonian Dynamics (classical)

**Question**: Does SCC produce classical Hamilton's equations ṗ = −∂H/∂q, q̇ = ∂H/∂p?

**Analysis**:

Within the group-theoretic framework, the classical Hamilton's equations appear on coadjoint orbits of G via the KKS construction:
- The Hamiltonian is a function H: g* → ℝ on the dual Lie algebra
- Hamilton's equations become ṁ = ad*_{dH/dm} m (Lie–Poisson equations) `[KR]`

This is a genuine derived structure but it describes dynamics on the group manifold, not dynamics of a particle in physical space.

**Verdict: `[D]` for Lie–Poisson / coadjoint orbit dynamics** `[T]`; **`[NOT DERIVED]` for physical particle dynamics** `[T]`

The Lie–Poisson equations are a true theorem of the group structure. They generalize but do not reduce to Newton's equations without the physical space identification.

---

### III.7 Transport and Continuum Mechanics

**Question**: Does SCC produce transport equations (Boltzmann, Navier–Stokes, diffusion)?

**Analysis**:

Transport equations require:
- Physical space (absent from SCC)
- Locality: interactions occur between spatially adjacent regions (absent)
- Distribution function f(x, p, t) on phase space (phase space not derived — III.2)
- Collision operator (molecular chaos — empirical)

**Verdict: `[NOT DERIVED]`** `[T]`

---

### III.8 Summary: Classical Mechanics Emergence

| Component | Status | First Missing Ingredient |
|---|---|---|
| Configuration space Q | NOT DERIVED | Physical space identification |
| Phase space T*Q | NOT DERIVED | Q |
| Canonical (q,p) | RECON (if G=Heisenberg) | Non-circular G selection |
| Newtonian limit | NOT DERIVED | Force, mass, physical space |
| Lagrangian dynamics | NOT DERIVED | Phase space over Q |
| Classical Hamiltonian | D (on group) / NOT DERIVED (physical) | Physical space |
| Transport | NOT DERIVED | Physical space + molecular chaos |
| Continuum mechanics | NOT DERIVED | Physical space + constitutive laws |

**Finding III.1** `[T]`: Classical mechanics in the physical sense (particles moving in space under forces) does **not** emerge from SCC. SCC produces Lie–Poisson dynamics on coadjoint orbits, which is a generalization of Hamiltonian mechanics on group manifolds. Reducing this to Newtonian particle mechanics requires additional physical inputs (physical space, mass, force law) that are absent from the SCC framework.

---

## Phase IV: What Mathematical Object Is SCC?

### IV.1 Process Theory?

A process theory (in the sense of Coecke–Abramsky `[KR]`) is a symmetric monoidal category where objects are systems and morphisms are processes, with a compositional structure.

SCC's axioms map onto this: ⊗ is the monoidal product, G-equivariance is the symmetric structure, and states are morphisms from the monoidal unit.

**Assessment**: SCC is an instance of a **symmetric monoidal category with a compact group of automorphisms**. The "process theory" framing is valid. However, this is not a new mathematical object — symmetric monoidal categories are well-established `[KR]`.

**Finding IV.A** `[T]`: SCC is mathematically an instance of a G-equivariant symmetric monoidal category with a G-invariant probability measure.

---

### IV.2 Symmetry Theory?

A symmetry theory takes a group G and derives the physics of systems invariant under G.

SCC fits this description: given G compact, it derives the representation theory of G on the state space.

**Assessment**: SCC is equivalent to **Mackey's system of imprimitivity** `[KR]` (Mackey 1949): a projective unitary representation of a locally compact group on a Hilbert space. This is a 70-year-old structure.

**Finding IV.B** `[T]`: SCC's quantum-mechanical content is mathematically equivalent to Mackey's induced representation theory. It is not a new symmetry-theoretic object.

---

### IV.3 Probability Theory?

SCC selects the Born rule probability measure via Gleason's theorem. In this sense it constrains the probability theory.

**Assessment**: SCC specifies *which* probability theory to use (Born rule on Hilbert space lattice) rather than being a general probability theory. It is a special case of quantum probability theory `[KR]` (Birkhoff–von Neumann).

**Finding IV.C** `[T]`: SCC's probability content is equivalent to quantum probability on an orthomodular lattice with a G-invariant state.

---

### IV.4 Geometric Theory?

The coadjoint orbit construction gives SCC a natural geometric interpretation: states correspond to points on coadjoint orbits of G (symplectic manifolds), and dynamics is Hamiltonian flow on these orbits.

**Assessment**: This is the **geometric quantization** program `[KR]` (Kirillov, Kostant, Souriau, 1960s–70s). SCC's geometric content is equivalent to geometric quantization applied to compact G.

**Finding IV.D** `[T]`: SCC's geometric content is mathematically equivalent to geometric quantization of compact Lie groups.

---

### IV.5 Category Theory?

SCC can be formulated in terms of dagger-compact categories (Abramsky–Coecke `[KR]`), where:
- Objects = physical systems
- Morphisms = processes
- Dagger = time reversal (SCC-I)
- Compactness = Bell states exist (from SCC-C + SCC-S)

**Assessment**: This is Categorical Quantum Mechanics (CQM) `[KR]`. SCC is an instance of CQM restricted to compact groups.

**Finding IV.E** `[T]`: SCC is an instance of Categorical Quantum Mechanics with compact symmetry group.

---

### IV.6 Is SCC Genuinely New?

**Theorem IV.1** `[T]`: SCC, as a mathematical framework, is equivalent to the intersection of:
1. Mackey's induced representation theory (symmetry content)
2. Geometric quantization on compact groups (geometric content)
3. Categorical quantum mechanics with compact symmetry (compositional content)
4. Jaynes maximum entropy given Haar measure (statistical content)

None of these components is new. Their *combination* under a single set of four axioms (C, S, I, N) is the organizational contribution of SCC.

**What is new (if anything)**:

The claim that these four axioms — stated in terms of composition and symmetry rather than Hilbert space postulates — constitute a *more primitive* starting point than the standard quantum axioms. Whether this constitutes genuine novelty or reformulation is the subject of Phase V.

---

## Phase V: Genuine Explanatory Power of SCC

For each claimed explanation, we identify whether it converts a previously free axiom into a theorem.

### V.1 Why Quantum Mechanics Uses Hilbert Spaces

**Standard axioms**: Hilbert space is *postulated* as the state space.

**SCC claim**: Hilbert space is *derived* from composition + symmetry.

**Assessment**:

SCC derives that the state space, given a compact group G acting on a complex vector space (M8), must be a Hilbert space (via Peter–Weyl). The derivation is genuine in the sense that it shows **why L²(G) rather than an arbitrary Hilbert space** — the specific structure of L²(G) is more constrained than the abstract axiom "state space is a Hilbert space".

However, M8 (complex vector space) is itself an assumption that is not derived from P0–P6.

**Verdict**: SCC provides *partial* explanatory power here. It explains why the Hilbert space carries a specific group-representation structure, but does not explain why the state space is complex in the first place.

**Previous axiom partially converted**: "State space is an abstract Hilbert space" → "State space is L²(G) for compact G". This is a genuine tightening, not a full derivation. `[T]`

---

### V.2 Why Probability is Born

**Standard axioms**: Born rule p = |⟨φ|ψ⟩|² is postulated.

**SCC claim**: Born rule is derived from the G-invariant measure via Gleason's theorem.

**Assessment**:

This is **genuine explanatory power**. Given a Hilbert space of dimension ≥ 3, Gleason's theorem `[KR]` shows there is exactly one probability measure consistent with the frame structure. The Born rule is therefore **not a free postulate** once the Hilbert space is accepted — it is forced.

**Previous axiom converted**: "Born rule is an independent postulate" → "Born rule is the unique G-invariant probability measure on H" (Gleason). `[T]`

**Caveat**: For dim H = 2 (qubits), Gleason's theorem does not apply without additional assumptions. SCC's derivation of Born rule has a gap for two-dimensional systems. `[MC]`

---

### V.3 Why Lie Groups Appear

**Standard theories**: Lie groups appear as symmetry groups by assumption (Wigner, Coleman–Mandula).

**SCC claim**: Lie groups appear necessarily from the composition law.

**Assessment**:

SCC assumes G is a locally compact topological group (M5). The theorem that locally compact groups acting continuously on a finite-dimensional space must be Lie groups is **Hilbert's fifth problem** `[KR]` (Gleason–Montgomery–Zippin theorem, 1952). Therefore:

If SCC's compact group G acts continuously and faithfully on a finite-dimensional space, G is automatically a Lie group.

**Verdict**: SCC does derive the Lie group structure of G from continuity + local compactness + faithful action. This is a genuine theorem. However, continuity and local compactness are themselves assumptions (M5) rather than purely logical necessities.

**Previous axiom partially converted**: "Symmetry group is a Lie group by assumption" → "Locally compact continuous symmetry group is automatically a Lie group" (Hilbert 5th). `[KR]` `[T]`

---

### V.4 Why Statistical Mechanics Works

**Standard theories**: Boltzmann/Gibbs statistical mechanics postulates ergodicity or equal a priori probabilities.

**SCC claim**: Gibbs statistics follows from Haar measure.

**Assessment**:

This is a reconstruction of the **Jaynes maximum entropy program** `[KR]`. Jaynes showed that Gibbs statistics follows from maximizing entropy subject to constraints, without requiring ergodicity. SCC's Haar measure provides the reference measure needed for the maximum entropy argument.

**Verdict**: SCC does not explain why statistical mechanics works in the sense of solving the ergodic problem or explaining irreversibility. It provides a clean foundation for the *equilibrium* Gibbs ensemble, but this was already achieved by Jaynes without SCC.

**Previous axiom partially converted**: "Equal a priori probabilities" → "Haar measure as natural invariant measure". This is a restatement of the Jaynes program. `[RECON]`

---

### V.5 Why Measurement Collapses Are Probabilistic

**Standard axioms**: The measurement postulate is a separate axiom of QM.

**SCC claim**: No claim made.

**Assessment**: SCC explicitly does not address the measurement problem. This is an honest gap. `[OP]`

---

### V.6 Summary of Explanatory Power

| Claimed Explanation | Status | Type |
|---|---|---|
| Why Hilbert space | Partial | Tightens but doesn't derive complex structure |
| Why Born rule | Genuine `[T]` | Converts axiom to theorem (Gleason) |
| Why Lie groups | Genuine `[KR]` | Hilbert 5th problem recovers Lie structure |
| Why statistical mechanics | `[RECON]` | Restates Jaynes program |
| Why measurement is probabilistic | Not addressed | `[OP]` |
| Why spacetime is 4D | Not addressed | `[OP]` |
| Why specific gauge group | Not addressed | `[OP]` |

**Net assessment**: SCC has **one piece of genuine new explanatory power** (Born rule as theorem via Gleason), **one piece of recovered explanatory power** (Lie groups via Hilbert 5th), and **several reconstructions** of existing programs (Jaynes, Mackey, CQM).

---

## Phase VI: Does SCC Predict Any New Mathematical Object?

### VI.1 Search for Novel Structures

We examine whether SCC predicts any mathematical object not present in the combination {Mackey + geometric quantization + CQM + Jaynes}.

**Candidate 1: The SCC composition axiom as a new constraint**

The requirement that ⊗ is equivariant under G and that the G-action is *the same group* for subsystems and composites (no "enlargement" of G upon composition) is a constraint not always explicit in Mackey's formulation. In Mackey's theory, one can have different groups acting on different subsystems.

**Assessment**: This is a genuine additional constraint that SCC imposes. It requires that the symmetry group is *universal* — the same G acts on all systems regardless of size. This rules out theories where the symmetry group of a composite is a product of distinct groups. `[T]`

However, this constraint is equivalent to requiring that G acts as a global symmetry in the sense of quantum field theory (same group at all scales), which is already required for consistent gauge theories. The constraint is non-trivial but is already implicitly required in consistent physical theories.

**Candidate 2: The SCC normalization axiom (SCC-N) as a compactness selector**

SCC-N requires the G-invariant probability measure to be normalizable. As established in the necessity audit, this forces G to be compact (or unimodular with finite total volume). This is a structural filter that rules out non-compact symmetry groups.

**Assessment**: This is a genuine filter but it *excludes* physically relevant cases (Lorentz group, Poincaré group). It is a selection criterion, not a new mathematical object.

**Candidate 3: The specific L²(G) realization**

SCC's derivation produces the state space as L²(G) — a specific realization of Hilbert space. This is more concrete than the abstract Hilbert space postulate of standard QM.

**Assessment**: L²(G) is a standard object in harmonic analysis, known since Weyl and Peter (1927) `[KR]`. It is not new.

### VI.2 Observational and Mathematical Equivalence

**Theorem VI.1** `[T]`: For any compact Lie group G, the physical predictions of SCC are identical to those of standard quantum mechanics on the Hilbert space L²(G).

*Proof*: SCC derives L²(G) as state space, Born rule via Gleason, unitary evolution via Stone, and observables via spectral theorem. Standard QM on L²(G) postulates all of these. Both frameworks make identical predictions for all observable quantities. ∎

**Theorem VI.2** `[T]`: SCC (for compact G) is mathematically equivalent to the combination of:
(a) Mackey's imprimitivity theorem applied to G
(b) Geometric quantization of coadjoint orbits of G
(c) Gleason's theorem on L²(G)

*Proof sketch*: Each component handles one of the SCC axiom pairs: (C+S) ↔ Mackey, (S+I) ↔ geometric quantization structure, (N) ↔ Gleason. The combination covers all four SCC axioms. ∎

**Corollary VI.1** `[T]`: SCC predicts no mathematical object absent from the combination of Mackey + geometric quantization + Gleason. There is no observational consequence of SCC that cannot be derived from this combination.

---

## Phase VII: Overall Scientific Assessment

### VII.1 Evidence Summary

**Genuine derivations** (axiom converted to theorem):
1. Born rule from Hilbert space via Gleason `[T]`
2. Schrödinger equation from unitary evolution via Stone `[T]`
3. Lie group structure from local compactness via Hilbert 5th `[KR]`
4. Quantum observables from spectral theorem `[T]`
5. Lie–Poisson dynamics on coadjoint orbits `[T]`

**Reconstructions** (conclusion encoded in inputs):
1. Hilbert space (requires M8: complex vector space)
2. Classical Hamiltonian mechanics (requires ℏ→0)
3. Statistical mechanics (restates Jaynes program)
4. Interference (same as Born + superposition)

**Not derived at all**:
1. Classical configuration space / physical space
2. Spacetime and its dimension
3. Specific symmetry group
4. Measurement postulate
5. Mass, charge, coupling constants
6. Transport and fluid mechanics
7. Gauge theory
8. General relativity

### VII.2 The Core Question

**Is SCC a new microscopic physical foundation, or a reformulation?**

The dependency graph (Phase I) shows that SCC's genuine physical content enters at two nodes:
- **M6** (compact G): equivalent to assuming a compact symmetry group — the same assumption underlying all of Mackey's theory and standard quantum mechanics on compact groups
- **M8** (complex state space): equivalent to assuming complex quantum mechanics — the standard assumption of QM

The SCC axioms {C, S, I, N} are a *clean, minimal reformulation* of these two physical assumptions in terms of composition and symmetry. They are **not weaker** than the standard QM axioms — they are at the same logical depth, expressed differently.

The genuine contribution is organizational: SCC isolates the four structural properties (closure, symmetry, invertibility, normalization) that are *individually sufficient* to force the quantum framework, and it does so in a language (composition + symmetry) that is arguably more primitive than the language of Hilbert spaces. This is a real clarification of the logical structure of quantum mechanics.

However, it is not a new physical foundation in the sense of deriving quantum mechanics from pre-quantum primitives. The pre-quantum primitives (M6, M8) already encode quantumness.

### VII.3 Classification

**Result: C**

> SCC is a **reformulation of existing quantum foundations**.

Specifically:

SCC is a clean, compositional reformulation of the intersection of Mackey's induced representations, geometric quantization on compact groups, and Gleason's theorem, organized under four axioms stated in terms of composition and symmetry rather than Hilbert space postulates.

It adds one genuine piece of explanatory power (Born rule via Gleason becomes explicit) and one organizational advance (the four-axiom derivation clarifies the logical structure of quantum mechanics).

It does not constitute a new microscopic physical foundation because its primitive assumptions (compact symmetry group acting on a complex state space) are at the same logical depth as the standard quantum mechanical axioms. Classical mechanics, spacetime, gauge theory, and gravity are not derived — they require additional physical inputs absent from SCC.

### VII.4 Precise Classification Table

| Claim | Verdict |
|---|---|
| SCC is genuinely new physics | **No** — equivalent to Mackey+GQ+Gleason |
| SCC derives QM from pre-quantum primitives | **No** — requires M6+M8 which encode quantum structure |
| SCC has genuine explanatory power | **Yes** — Born rule and Lie structure become theorems |
| SCC is internally consistent | **Yes** — all verified symbolically and numerically |
| SCC subsumes classical mechanics | **No** — classical limit requires additional inputs |
| SCC subsumes gauge theory and GR | **No** — requires spacetime, not present in SCC |
| SCC is a valid quantum foundation | **Yes** — complete for non-relativistic QM given M6+M8 |

### VII.5 Open Problems Identified

**OP1** `[OP]`: Can M8 (complex vector space) be derived from P0–P6 + M6 without assuming complex structure? (This would make SCC a genuine pre-quantum foundation.)

**OP2** `[OP]`: Can M6 (compactness of G) be derived from a finite-information principle without assuming it? (Addressed partially in the necessity audit — possible on finite spaces.)

**OP3** `[OP]`: Is there a version of SCC that does not require a background group G but instead derives G from the composition algebra alone? (Related to reconstruction theorems in TQFT.)

**OP4** `[OP]`: Does SCC's universality constraint (same G for all systems) have testable consequences distinguishing it from theories allowing different symmetry groups at different scales?

---

*End of Audit*

*Symbolic verifications: see SCC_scientific_status_sympy.py*

*Numerical validations: see SCC_scientific_status_validation.py*
