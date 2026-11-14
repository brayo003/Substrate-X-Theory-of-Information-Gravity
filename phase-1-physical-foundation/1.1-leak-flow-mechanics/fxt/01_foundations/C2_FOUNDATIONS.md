# C2_FOUNDATIONS.md
## Canonical Mathematical Foundation Document — C2 Substrate Project
**Version:** 1.0  
**Date:** 2026-07-24  
**Authority:** Compiled from all completed audits in `/home/lenovo/Desktop/fxt/`  
**Status convention:**
- **PASS** — All claims proven; no open gaps in this subsystem
- **PARTIAL** — Core results proven; secondary claims open or conditional
- **OPEN** — Central mathematical question unresolved
- **FAILED** — A claimed result has been disproved
- **UNKNOWN** — Insufficient analysis to classify

**Label convention (inherited from source audits):**
- `[T]` Proven theorem  
- `[KR]` Known rigorous result  
- `[MC]` Mathematical conjecture  
- `[CJ]` Physical conjecture  
- `[OP]` Open problem  
- `[OBS]` Proved obstruction / impossibility  
- `[PHY]` Physical assumption  

---

## Preamble: Scope of the C2 Project

The C2 substrate project investigates whether a single minimal microscopic mathematical principle can generate all established physical structure — classical mechanics, quantum mechanics, statistical mechanics, spacetime geometry, and gauge theory — as internal derived consequences, without importing those structures as axioms.

The project proceeds in three layers:

1. **Transport layer:** The Persistent Random Walk (PRW) on the FPUT harmonic lattice, its continuum limit (telegrapher equation), and the full master equation [ME].
2. **Foundational layer:** The Causal-Compositional Algebra (CCA) and its five primary candidates (C1–C5) as microscopic principles.
3. **Obstruction layer:** Identification of the three structural obstructions (O1: complex structure, O2: continuum geometry, O3: renormalization) and their logical status.

This document records the exact mathematical state of every subsystem. It does not improve, extend, or redesign any result. It records what has been proved, what has been assumed, and what remains open.

---

## SUBSYSTEM 1: Persistent Random Walk (PRW) Microscopic Model

### Mathematical Definition

A discrete stochastic process on ℝ with walker state (x, σ) ∈ ℝ × {+1, −1}. The walker moves at speed v in direction σ and reverses to −σ at rate λ (Poisson process). The balance equations are:

```
∂n⁺/∂t = −v ∂n⁺/∂x − λ n⁺ + λ n⁻
∂n⁻/∂t = +v ∂n⁻/∂x + λ n⁺ − λ n⁻
```

where n⁺(x,t), n⁻(x,t) are the densities of rightward and leftward walkers.

### Assumptions

- **A-PRW1:** Walker speed v and flip rate λ are constant (spatially and temporally uniform).
- **A-PRW2:** The continuum limit Δx → 0, Δt → 0 is taken at fixed v and λ.
- **A-PRW3:** The walker process is Markovian (flip rate independent of history).

### Known Theorems

**[KR] Theorem PRW-1 (Goldstein-Kac, 1951/1974):** The sum field s = n⁺ + n⁻ satisfies the telegrapher equation: τ s_{tt} + s_t = c² τ s_{xx}, with τ = 1/(2λ), c = v.

**[Cor] Corollary PRW-1-BGK (BGK reduction):** In the limit τ → 0 with D = c²τ fixed, the telegrapher reduces to ∂s/∂t = D ∂²s/∂x². (Source: substrate_final_audit.md, Theorem EQ-2.) *(Corollary of Theorem PRW-1: τ → 0 limit.)*

**[Cor] Corollary PRW-1-WAVE (Wave limit):** In the limit τ → ∞ with c fixed, the telegrapher reduces to s_{tt} = c² s_{xx}. (Source: substrate_final_audit.md, Theorem EQ-3.) *(Corollary of Theorem PRW-1: τ → ∞ limit.)*

**[KR] Theorem PRW-4:** The actions nₖ = |Aₖ|² are exact constants of motion of the harmonic FPUT chain. (Source: projection_classification_audit.md, S3.)

### Derivations Completed

- Continuum limit of PRW balance equations → telegrapher equation. **[T]**
- Parameter identification: τ = 1/(2λ), D = v²/(2λ). **[T]**
- BGK reduction (τ → 0 limit). **[T]**
- Wave equation limit (τ → ∞). **[T]**
- Cattaneo heat equation identification. **[T]**

### Derivations Incomplete

- Multi-dimensional generalization of the PRW (1D result only).
- Non-uniform flip rate λ(x,t): the balance equations have not been derived for spatially varying λ.

### Proven Results

- The PRW is the unique local projection of the FPUT harmonic chain satisfying admissibility constraints C1–C6. (Established fact F1 in substrate_final_audit.md.)
- The PRW observable algebra is commutative: 𝒜_PRW = C^∞(ℝ, ℝ²). (F2.)
- The PRW state space is Δ₁ ≅ [0,1]; no quantum state space emerges. (F3.)

### Conditional Results

- Decoherence prediction Γ_φ = k_rot · ω_rot² is conditional on independent axioms M1 (matrix fields), M2 (Moyal deformation), and the coupling assumption H_int = g J σ_z. Without these axioms the prediction is not a consequence of the PRW alone. (F5, F6.)

### Failed Proofs

- **FAILED:** Quantum state space CP¹ ≅ S² does not emerge from the PRW. The PRW state space is the classical simplex Δ₁, not the Bloch sphere. No quantum structure emerges from the PRW transport layer. (F3, substrate_final_audit.md.)

### Impossibility Results

**[T] Theorem PRW-IMP-1:** The PRW observable algebra is commutative. No non-commutative structure (required for quantum mechanics) is derivable from the PRW without additional axioms. (F2.)

### Remaining Conjectures

**[OP]** Multi-dimensional PRW: does the 3D PRW also project uniquely to the 3D telegrapher equation under the same admissibility constraints?

**Status: PASS** (for 1D core; PARTIAL for multi-D generalization)
*Justification: The 1D PRW, its continuum limit, and its parameter identification are fully established. The multi-dimensional extension is incomplete but does not affect the 1D results.*

---

## SUBSYSTEM 2: FPUT Lattice — Projection Classification

### Mathematical Definition

The FPUT β-chain with N particles, mass m, spring constant K, periodic boundary conditions:

```
H = Σᵢ [ pᵢ²/(2m) + K(qᵢ₊₁−qᵢ)²/2 + (β/4)(qᵢ₊₁−qᵢ)⁴ ]
```

Harmonic limit: β → 0. Normal modes Aₖ with dispersion ωₖ = 2√(K/m)|sin(πk/N)|. Phase space 𝒫 = (ℝ₊)^M × T^M, dim = 2M = N−2.

An admissible projection is a map π: 𝒫 → Σ_meso satisfying six constraints:
- **C1 (Locality):** π(x) depends only on fields in a bounded neighborhood of x.
- **C2 (Conservation):** Total projected density = total microscopic action.
- **C3 (Finite speed):** Signal speed ≤ acoustic sound speed vₛ.
- **C4 (Positivity):** Projected densities ≥ 0.
- **C5 (Closure):** ∂_t π(state) expressible as function of π(state) alone.
- **C6 (Thermodynamic consistency):** Mesoscopic entropy non-decreasing.

### Assumptions

- **A-FPUT1:** Harmonic limit β = 0 throughout (anharmonicity enters only as collision rate γ).
- **A-FPUT2:** Thermodynamic limit N → ∞ with fixed lattice constant a.
- **A-FPUT3:** The six admissibility constraints C1–C6 are accepted as the complete set of physical requirements.

### Known Theorems

**[KR] Theorem FPUT-1 (Integrability):** The harmonic FPUT chain is Liouville-integrable with M commuting integrals {nₖ}.

**[T] Theorem FPUT-2 (C1 is the binding constraint):** Locality (C1) is the constraint that eliminates phase-retaining projections. C5 and C6 are NOT the binding constraints — phase evolution φ̇ₖ = ωₖ is autonomous (C5 satisfied); phase oscillations are isentropic (C6 satisfied). (Source: projection_classification_audit.md, Theorems C5-Analysis, C6-Phase.)

**[T] Theorem FPUT-3 (CLASS-1: PRW is the unique local projection):** The only admissible projection satisfying C1–C6 that retains only the action variables nₖ is the coarse-grained density s(x,t) = (1/N) Σₖ nₖ e^{ikx}, whose evolution is the telegrapher equation. The phase information φₖ is not locally recoverable and is projected out by C1. (Established fact F1.)

**[T] Theorem FPUT-4 (Phase geometry is classical):** The discarded phase sector has geometry T^M (M-torus), π₁(T^M) = ℤ^M, flat curvature, trivial holonomy. (Established fact F7.)

### Derivations Completed

- Normal mode decomposition and action-angle variables. **[KR]**
- Proof that C1 eliminates phase-retaining projections. **[T]**
- Proof that PRW = unique C1–C6 admissible projection. **[T]**
- Phase geometry computation: T^M torus, π₁ = ℤ^M. **[T]**

### Derivations Incomplete

- Classification of all admissible projections for the anharmonic chain (β ≠ 0).
- Projection classification in 3D FPUT lattice.

### Proven Results

- Phase sector topology: T^M, flat. **[T]** (F7)
- PRW uniqueness as local projection. **[T]** (F1)
- No quantum structure in the phase sector (trivial holonomy). **[T]**

### Impossible Results

**[OBS] FPUT-IMP-1:** Non-trivial holonomy (Berry phase, Aharonov-Bohm) cannot arise from the FPUT harmonic chain. The phase geometry is flat with trivial holonomy; no curvature is present to generate a geometric phase. This rules out deriving the Aharonov-Bohm effect from the FPUT projection alone.

### Remaining Conjectures

**[OP]** Does the anharmonic FPUT (β ≠ 0) generate a non-trivial phase geometry with non-zero curvature?

**Status: PASS**
*Justification: The complete admissibility classification for the harmonic chain is established. The binding constraint (C1) is identified. Uniqueness of the PRW projection is proved.*

---

## SUBSYSTEM 3: Telegrapher Equation and Master Transport Equation [ME]

### Mathematical Definition

**Core equation (telegrapher):**
```
τ s_{tt} + s_t = c²τ ∇²s
```

**Full master equation [ME]:**
```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
                     − ∇·(s v_sub)
                     − ∇·(χ s u)
                     + α E
                     + β ∇·(E v_sub)
                     + γ_F F
                     − σ_irr
```

Parameters: τ = 1/(2λ), c = v, D = c²τ. Fields: s = information density, v_sub = substrate bulk velocity, u = unit coherence direction, E = energy density, F = force density, σ_irr = irreversible sink.

**Substrate transport system (first-order form):**
```
∂s/∂t + ∂J/∂x = 0              [continuity]
∂J/∂t = −c² ∂s/∂x − (1/τ) J   [C-J]
```

### Assumptions

Eight independent assumptions A1–A8 (see substrate_final_audit.md §IV.1):

| Label | Assumption |
|-------|-----------|
| A1 | PRW particles travel at speed c, reverse at rate λ |
| A2 | s = n⁺ + n⁻ identified as "information density" |
| A3 | Substrate bulk velocity v_sub given externally |
| A4 | Coherence drift χu is a second advection velocity |
| A5 | Energy density E couples to s with coefficient α |
| A6 | Energy flow ∇·(Ev_sub) couples with coefficient β |
| A7 | Force density F couples with coefficient γ_F |
| A8 | Irreversible sink σ_irr |

> **Notation remark (ME-NR-1):** The symbol γ_F in this equation denotes the force coupling constant [info/(N·s)]. It is distinct from the Lindblad jump rate γ [s⁻¹] and the abstract transition rate γ_mn [s⁻¹] that appear in §Subsystem 4. The subscript F is used throughout to prevent collision.

### Known Theorems

**[Lemma] Lemma ME-EQ-MAIN-L1 (Exact equivalence to telegrapher):** The core of [ME] is exactly the telegrapher / Maxwell-Cattaneo / Goldstein-Kac equation. (substrate_final_audit.md, Theorem EQ-1.) *(Lemma for Theorem ME-EQ-MAIN — establishes the core term before the full equivalence is extended to all terms.)*

**[T] Theorem ME-EQ-MAIN (Full equivalence to EIT):** Every term in [ME] is either exactly equivalent to or a special case of terms in Extended Irreversible Thermodynamics (EIT) and GENERIC. (Theorem EQ-MAIN.)

**[Cor] Corollary ME-EQ-MAIN-1 (No assumption reduction):** The substrate does not reduce the number of independent assumptions compared to EIT. (Theorem ASS-1.) *(Corollary of Theorem ME-EQ-MAIN. Proof: immediate — if every [ME] term is equivalent to an EIT term, the assumption count cannot decrease. ∎)*

**[Cor] Corollary ME-EQ-MAIN-2 (Assumptions renamed, not removed):** Each assumption A1–A8 corresponds to a standard EIT/GENERIC assumption under change of variable names. (Theorem ASS-2.) *(Corollary of Theorem ME-EQ-MAIN. Proof: immediate — equivalent terms carry equivalent assumptions under renaming. ∎)*

### Derivations Completed

- Telegrapher equivalence (exact). **[T]**
- Advection term = standard EIT advection (exact). **[T]**
- Coherence term = advection with renamed velocity (exact). **[T]**
- Energy coupling terms = EIT Onsager cross-effects (special case). **[T]**
- Force term = standard body force (exact). **[T]**
- Sink term = entropy production sink (exact). **[T]**
- Diffusion limit (τ → 0): standard advection-diffusion-reaction. **[T]**
- Wave limit (τ → ∞): wave equation. **[T]**

### Proven Results

**[T] Theorem ME-PRED-NONE (No new predictions):** Every observable prediction of [ME] either already follows from the telegrapher/Maxwell-Cattaneo/EIT/GENERIC equations, or is contingent on independent axioms M1, M2 and a coupling assumption not derived from [ME]. No prediction satisfies all four criteria for genuine novelty (P1: mathematically unique; P2: experimentally distinguishable; P3: not parameter fitting; P4: not reinterpretation). (substrate_final_audit.md, Theorem PRED-NONE.)

**[T] Theorem ME-NOV1 through NOV7 (No new mathematical objects, theorems, invariants, conservation laws, variational principles, symmetries, or predictions):** Proved in substrate_final_audit.md §VI.

### Failed Proofs

**FAILED PRED-1:** Finite propagation speed is NOT a new prediction. It is a property of the telegrapher equation known since Cattaneo (1948). (Theorem PRED-1-FAIL.)

**FAILED PRED-2:** Decoherence rate Γ_φ = γ·ω_mic/ω_rot is NOT a prediction of [ME] alone. It requires axioms M1, M2, and H_int = g J σ_z, none derived from [ME]. (Theorem PRED-2-FAIL.)

**FAILED PRED-3:** Coherence transport (χ term) is NOT new. It is advection with velocity χu. (Theorem PRED-3-FAIL.)

### Impossibility Results

**[T] Theorem ME-DER-NOT(a):** [ME] cannot derive Navier-Stokes equations (scalar theory vs. vector momentum field).

**[T] Theorem ME-DER-NOT(b):** [ME] cannot derive the full BGK equation (macroscopic moment vs. phase-space distribution).

**[T] Theorem ME-DER-NOT(c):** [ME] cannot derive the Lattice Boltzmann equation (continuum macroscopic limit vs. discrete velocity mesoscale).

**[T] Theorem ME-DER-NOT(d):** [ME] cannot derive nonlinear transport phenomena (equation is linear in s).

### Remaining Conjectures

None. The transport layer is fully classified.

**Status: PASS**
*Justification: Complete mathematical equivalence to EIT/GENERIC proved. All terms identified. No new predictions. The transport layer is mathematically closed.*

---

## SUBSYSTEM 4: Interaction Hamiltonian and Lindblad Master Equation

### Mathematical Definition

**Interaction Hamiltonian:**
```
H_int = g · J(x_q, t) · σ_z
```

g = quantum-classical coupling constant [J·m²·s/info], J = substrate current at qubit position x_q, σ_z = Pauli operator.

**Lindblad master equation (effective):**
```
dρ_S/dt = (Γ_φ/2)(σ_z ρ_S σ_z − ρ_S)
```

**Main prediction:**
```
Γ_φ = k_rot · ω_rot²
k_rot = 8g²s₀²r_q²τ / (3ℏ²)
```

**Rotating-frame current variance:**
```
⟨(δJ)²⟩ = (2/3) s₀² ω_rot² r_q²
```

### Assumptions

- **A-HC1 (Born):** ρ_total = ρ_S ⊗ ρ_B (weak coupling).
- **A-HC2 (Markov):** Substrate correlation time τ ≪ Γ_φ⁻¹.
- **A-HC3 (Secular):** Secular approximation applied.
- **A-HC4 (Stationary):** Substrate autocorrelation C_JJ(t,τ) = C_JJ(τ).
- **A-HC5 (Linear coupling):** H_int linear in J — minimal coupling assumption.
- **A-HC6 (Local coupling):** H_int local at qubit position x_q.
- **A-M1 (Matrix fields):** Quantum field M1 is an independent axiom, not derivable from [ME]. (F5.)
- **A-M2 (Moyal deformation):** M2 is an independent axiom, logically independent of M1 and [ME]. (F6.)

### Known Theorems

**[KR] Theorem HC-1 (Bloch-Redfield):** The Bloch-Redfield master equation follows from Born-Markov approximations applied to H_int = g J σ_z.

**[KR] Theorem HC-2 (Lindblad form):** Under secular approximation, Bloch-Redfield reduces to Lindblad form with L = σ_z, Γ_φ = 2γ. CPTP property holds.

**[T] Theorem HC-3 (Pure dephasing operator uniqueness):** Under A-HC5 and A-HC6 (linear local coupling), the unique pure-dephasing Lindblad operator is A = σ_z. T₁ = ∞ (no relaxation). (Source: interaction_hamiltonian_uniqueness.md.)

**[T] Theorem HC-4 (T₂ ≤ 2T₁ structural bound):** From Im(ω) = 1/(2τ), the bound T₂ ≤ 2T₁ follows. This reproduces the standard quantum channel bound without invoking quantum mechanics at the substrate level. (capability_audit.md §IV.4.)

### Derivations Completed

- Bloch-Redfield derivation from H_int. **[T]**
- Lindblad reduction under secular approximation. **[T]**
- Γ_φ formula from current autocorrelation integral. **[T]**
- Rotating-frame current variance ⟨(δJ)²⟩. **[T]**
- Main prediction Γ_φ = k_rot · ω_rot². **[T]**
- Empirical fit: k_rot = 4.5 × 10⁻⁷ s from IBM Quantum data. **[E]**

### Conditional Results

- The decoherence prediction Γ_φ = k_rot · ω_rot² holds **conditional on** A-M1, A-M2, A-HC1 through A-HC6. Removing any of M1 or M2 makes the prediction unsupported.

### Failed Proofs

**FAILED:** M1 (matrix fields) is NOT derivable from the transport layer [ME] or the PRW. (F5.)

**FAILED:** M2 (Moyal deformation) is NOT derivable from [ME] or M1. (F6.)

### Impossibility Results

**[OBS] HC-IMP-1:** The Lindblad operator A = σ_z is the unique pure-dephasing operator for local linear coupling. No alternative Lindblad structure is consistent with the coupling assumptions. This uniqueness is a theorem, not a choice.

**[T] Theorem HC-GAMMA-NOFOMEGA (Non-derivability of γ_mn = F(ω_mn)):** The statement γ_mn = F(ω_mn) for some scalar F: ℝ → ℝ₊ is not derivable from the T_C2 quantum completion axioms (A-QUANT-1 through A-QUANT-11, A-GEOM-1–3). The specific T_C2 result is γ_01 = (1/2) k_rot ω_rot², which is a function of the bath parameter ω_rot, not the system Bohr frequency ω_01. Derivation of γ_mn = F(ω_mn) requires the additional Axiom S2 (coupling matrix element uniformity; see §Open Assumptions), which is not in the frozen assumption set. (Source: Quantum Completion Audit, Stage 9, 2026-07-25.)

### Remaining Conjectures

**[OP]** What determines g (the quantum-classical coupling constant)? No derivation of g exists from the substrate.

**[OP]** Multi-mode / non-Markovian corrections: do they modify the ω_rot² scaling?

**[OP]** Transverse coupling: can T₁ become finite within the substrate framework?

**Status: PARTIAL**
*Justification: The Lindblad structure and T₂ ≤ 2T₁ bound are proved. The main prediction Γ_φ = k_rot·ω_rot² is derived but conditional on M1, M2, and coupling assumptions. The coupling constant g is undetermined.*

---

## SUBSYSTEM 5: SXC-IGC Transport-Phase Classifier (Q diagnostic)

### Mathematical Definition

```
Q(x,t) = 4c²τ²|∇ ln s(x,t)|² − 1
```

**Regime classification:**
- Q > 0: oscillatory (coherent) regime
- Q < 0: overdamped (incoherent) regime
- Q = 0: exact phase boundary (critical point)

**Coherence length:** ξ_c = 2cτ (extracted from Q = 0 condition)

**Decoherence rate near threshold:** Γ_dec ≈ (1/2τ)√|Q| for Q → 0⁻

### Assumptions

- s(x,t) is a sufficiently smooth scalar field with ∇s well-defined.
- c and τ are known (calibrated from measurements).
- The field s satisfies the telegrapher equation [ME core].

### Known Theorems

**[T] Theorem Q-1 (Stability equivalence):** Q = 0 is exactly the standard stability threshold of the telegrapher equation (eigenvalue condition from dispersion relation λ± = −1/(2τ) ± √(c²k² − 1/(4τ²)) = 0 at k = k_c). (capability_audit.md §II.6.)

**[T] Theorem Q-2 (Coordinate invariance):** Q = 4c²τ²|∇ ln s|² − 1 is coordinate-invariant. |∇ ln s|² = g^{ij}(∂_i ln s)(∂_j ln s) is a scalar contraction. (capability_audit.md §III.4.)

**[T] Theorem Q-3 (ωτ equivalence for plane waves):** For a plane wave of wavenumber k, Q = 4c²τ²k² − 1, and Q = 0 ⟺ ωτ = 1/2. Q is exactly equivalent to the standard ωτ criterion for homogeneous sinusoidal fields. (capability_audit.md §IV.2.)

**[T] Theorem Q-4 (T₂ ≤ 2T₁ derivation):** T₂ ≤ 2T₁ follows from Im(ω) = 1/(2τ) with no quantum input.

**[T] Theorem Q-5 (Local heterogeneous extension):** For spatially heterogeneous fields, Q(x,t) detects local transitions invisible to global criteria (ωτ, Reynolds number). No existing single diagnostic performs this task. (capability_audit.md §III.1.)

### Derivations Completed

- Q as algebraic shortcut for eigenvalue stability analysis. **[T]**
- Cross-domain unification (acoustic, thermal, EM, concentration). **[T]**
- T₂ ≤ 2T₁ bound from substrate. **[T]**
- O(N) computational cost vs. O(N) eigenvalue problems. **[MC]**

### Proven Results

The Q diagnostic is a new **reduced-order engineering framework** (Classification B in capability_audit.md). It is not a fundamentally new physical prediction but provides:

1. Local, coordinate-invariant, spatially heterogeneous regime classification — no existing equivalent. **[T]**
2. Cross-domain unification under one formula — no existing equivalent. **[T]**
3. Algebraic stability classification replacing eigenvalue analysis. **[T]**

### Failed Claims

**FAILED (Category A):** Q does not predict any fundamentally new physical phenomenon beyond existing theories. (capability_audit.md §VI.1.)

### Impossibility Results

**[T]** Q cannot replace full PDE time evolution, Lindblad quantum state dynamics, or nonlinear stability analysis. It is a diagnostic, not a solver.

### Remaining Conjectures

**[OP]** Calibration of c and τ for specific physical systems (requires experimental input).

**Status: PASS (as engineering diagnostic); PARTIAL (as physical theory)**
*Justification: Q's mathematical properties are fully established. Its status as a novel reduced-order diagnostic is proved. Its status as a source of new physics is not supported.*

> **Structural remark (Q-SR-1):** Theorems Q-1 through Q-5 depend only on the transport layer (Theorem PRW-1, A-TRANS-4). They do not connect to any quantum layer theorem. The Q diagnostic is a complete, self-contained transport-layer tool. No theorem in the quantum dephasing computation (§Subsystem 4) requires or references Q. Readers expecting a connection between Q(x,t) and the dephasing rate Γ_φ will not find one — this is not a gap but a correct structural separation.


---

## SUBSYSTEM 6: Causal-Compositional Algebra (CCA)

### Mathematical Definition

**Definition CCA-0.1:** A CCA is a tuple **(O, M, ⊗, ≤, †, ε)** where:

| Primitive | Type | Role |
|-----------|------|------|
| O | Finite set | Objects (state labels) |
| M | Morphisms with src, tgt ∈ O | Processes |
| ⊗ | Partial binary operation on M | Composition / parallel combination |
| ≤ | Partial order on M | Causal order |
| † | Involution (†² = id) | Time-reversal / adjoint |
| ε | Map M → [0,1], Σ_{m:A→B} ε(m) = 1 | Probabilistic weight |

**Axioms:**
- **Ax1:** (O, M, ⊗) is a symmetric monoidal category with finite hom-sets and unit I.
- **Ax2:** (M, ≤) is a locally finite partial order.
- **Ax3:** † reverses causal order: m ≤ m' ⟹ m'† ≤ m†.
- **Ax4:** ε: M → [0,1] with Σ_{m:A→B} ε(m) = 1 for every (A,B).
- **Ax5:** (≤, ε) makes each Hom(I,A) a probability simplex ordered by causal depth.

### Assumptions

The sole starting assumption is that Ax1–Ax5 constitute the complete primitive axiom set. No additional structure is imported.

### Known Theorems — Internal Consequences of Ax1–Ax5

**[T] Theorem CCA-1 (State spaces):** Hom(I, A) is a well-defined probability simplex for each A. (cca_foundation_audit.md, Theorem 1.1.)

**[T] Theorem CCA-2 (Observables):** End(A) = Hom(A,A) is a finite monoid acting on states. (T 1.2.)

**[T] Theorem CCA-3 (Causal depth function):** The rank r(m) = length of longest chain below m in (M,≤) is well-defined. (T 1.3.)

**[T] Theorem CCA-4 (Symmetry groups):** Aut(A) is a well-defined finite group for each A. (T 1.4.)

**[T] Theorem CCA-5 (Shannon entropy):** H(A) = −Σ ε(s) log ε(s) is a well-defined non-negative real number for each A. (T 1.5.)

**[T] Theorem CCA-6 (Partition function):** Z_β(A) = Σ exp(−β r(s)) is a finite positive real number. (T 1.9.)

**[T] Theorem CCA-7 (Discrete causal structure):** The Alexandrov topology on (M,≤) gives a discrete spacetime candidate. (Theorem 2.1.)

**[T] Theorem CCA-8 (Tensor locality):** Spacelike separation = incomparability in (M,≤). (T 2.3.)

**[T] Theorem CCA-9 (Categorical QM emergence):** A †-compact symmetric monoidal category with chosen basis structure on each object generates finite-dimensional QM (Born rule, measurement, entanglement, no-cloning). (Coecke-Abramsky [KR], cca_foundation_audit.md T 3.1.)

**[T] Theorem CCA-10 (Classical coarse-graining):** The quotient by diagonal morphisms (decoherence basis selection) recovers classical stochastic mechanics. (foundational_principle_audit.md, Theorem 8.1.)

### Derivations Completed

- Internal closure: state spaces, observables, entropy, causal depth, symmetry groups, tensor products, coarse-graining. **[T]**
- QM emergence from †-compact structure. **[KR]** (conditional on choosing †-compact subclass)
- Classical mechanics from decoherence coarse-graining. **[T]**
- Statistical mechanics from thermodynamic coarse-graining. **[T]**
- Discrete causal structure from (M,≤). **[T]**

### Derivations Incomplete

- Continuous spacetime manifold: requires continuum limit (N → ∞) — not proved from Ax1–Ax5 alone.
- Lorentz group: requires continuum limit + Bombelli-Lee-Meyer-Sorkin conjecture — unproved.
- Quantum field theory: not derived from any CCA candidate.
- Gauge symmetry: not derived internally.

### Proven Results

**[T]** Internal to Ax1–Ax5: categorical structure, probability, causal order, entropy, free energy, coarse-graining. All internally generated.

**[T]** External targets generated **conditionally** (requiring specific subclass choices):
- Finite-dimensional QM: requires †-compact structure. [KR]
- Classical mechanics: requires decoherence basis choice. [T]
- Statistical mechanics (Gibbs): requires energy function assignment. [T]
- Lorentzian geometry: requires continuum limit conjecture. [KR conditional]

### Impossibility Results

**[OBS] CCA-IMP-1 (No continuum from finite CCA):** Ax1–Ax5 generate only a finite discrete structure. A continuous Lorentzian manifold cannot emerge without a limiting procedure and faithfulness condition. (cca_foundation_audit.md, Obstruction 2.1a.)

**[OBS] CCA-IMP-2 (No Lorentz group from finite automorphisms):** The Lorentz group SO(3,1) is a continuous Lie group. CCA generates only finite automorphism groups. Exact Lorentz symmetry cannot emerge from any finite CCA. (Obstruction 2.5a.)

**[OBS] CCA-IMP-3 (No continuum speed from counting):** Finite propagation speed as a physical ratio requires a metric. CCA provides only a counting measure (rank). Numerical value of c is not derivable from Ax1–Ax5 alone. (Obstruction 2.4a.)

### Remaining Conjectures

**[MC] CCA-C1 (CCA generates quantum causal processes):** Ax1–Ax5 simultaneously generate quantum process theory, causal structure, and probabilistic weights without importing any separately. (cca_foundation_audit.md, Conjecture 6.2.) **Status: unproved.**

**[MC] CCA-C2 (Causal entropy non-decrease):** H_c(B) ≥ H_c(A) for any causal evolution m: A → B. (Conjecture 6.6.) **Status: unproved.**

**[MC] CCA-C3 (Causal action extremization):** Physically realized morphisms are those extremizing S_causal = −log ε(m) + r(m). (Conjecture 6.8.) **Status: unproved.**

**[MC] CCA-C4 (CCA is strictly stronger than existing frameworks):** CCA structure cannot be decomposed into independent applications of any single existing framework. (Conjecture 7.3.) **Status: unproved.**

**[OP] CCA-OP1 (GNS representation theorem for CCA):** Is every abstract CCA representable as a CCA of matrices with causal order given by a time-like partial order? (Open Problem 6.4.)

**[OP] CCA-OP2 (QFT emergence):** No candidate generates quantum field theory internally. (Open Problem 8.4.)

**Status: PARTIAL**
*Justification: Internal consequences of Ax1–Ax5 are fully established. Emergence of continuous spacetime, Lorentz symmetry, and QFT from CCA is unproved. Four central conjectures remain open.*

---

## SUBSYSTEM 7: Five Primary Microscopic Candidates (C1–C5)

### Mathematical Definitions

**C1 (†-compact symmetric monoidal category):** A small †-compact SMC with finite hom-sets, unit I, and dualizing functor (−)†.

**C2 (Finite-state channel category):** A finite set S with stochastic matrix T: S → ΔS, closed under composition.

**C3 (Dependent type theory):** Dependent type theory with identity types, Σ-types, Π-types, and universe hierarchy U₀ : U₁ : U₂ : …

**C4 (Finite partial order with covering relations):** Locally finite poset (P, ≤) with rank function r: P → ℕ.

**C5 (σ-finite measure algebra):** σ-finite measure space (Ω, Σ, μ) with Ω a standard Borel space.

### Known Theorems (Emergences)

**[T] Theorem C1-QM (Categorical QM):** C1 with basis structure generates full finite-dimensional quantum mechanics. (Coecke-Abramsky [KR].) Born rule emerges from Gleason's theorem. **[T]**

**[T] Theorem C2-Gibbs (Statistical mechanics):** Finite ergodic Markov chain (C2) generates Gibbs distribution as unique maximum-entropy distribution at fixed mean energy. (foundational_principle_audit.md, Theorem 5.2.) **[T]**

**[T] Theorem C2-Hthm (H-theorem):** H(μ_t) non-decreasing, converges to H(μ*). **[T]**

**[KR] Theorem C4-Malament (Lorentzian geometry):** Lorentzian manifold determined up to conformal factor by causal order (Malament theorem). C4 generates spacetime geometry from causal order + volume measure. **[KR]**

**[KR] Theorem C5-Hamiltonian:** Measure-preserving flows on symplectic manifolds = Hamiltonian flows (Halmos). C5 ⊇ classical Hamiltonian mechanics. **[KR]**

### Emergence Table

| Candidate | Classical Mech | Stat Mech | Wave/QM | Relativity | QFT | Gauge | Gravity |
|-----------|---------------|-----------|---------|------------|-----|-------|---------|
| C1 (Cat) | [T] via classical limit | [MC] | [T] full QM | [OP] | [OP] | [MC] | [OP] |
| C2 (Info) | [T] permutations | [T] Gibbs | [OP] | [OP] | [OP] | [OP] | [OP] |
| C3 (Type) | [MC] | [OP] | [CJ] | [CJ] | [CJ] | [KR] gauge | [OP] |
| C4 (Order) | [CJ] | [OP] | [OP] | [KR] causal | [OP] | [OP] | [KR] Malament |
| C5 (Meas) | [KR] Hamiltonian | [KR] ergodic | [MC] | [OP] | [OP] | [OP] | [OP] |
| CCA (New) | [MC] | [MC] | [MC] | [MC] | [OP] | [OP] | [OP] |

### Impossibility Results

**[OBS] C-IMP-1 (Quantum gravity gap):** No single candidate C1–C5 has been shown to generate both quantum mechanics and Lorentzian geometry internally. The quantum gravity emergence problem is completely open. (Open Problem 4.1.)

**[OBS] C-IMP-2 (QFT gap):** No candidate generates quantum field theory (renormalization, running couplings, vacuum structure) in a rigorous internal way. (Open Problem 8.4.)

### Remaining Conjectures

**[MC]** C1 ∩ C4 (categorical + causal poset enrichment) may generate both QM and spacetime. Designated C1C4. Status: uninvestigated.

**[MC]** Large-N universality forces O1 (complex structure) and O2 (continuum) in any framework with N → ∞ interacting degrees of freedom. (Obstruction audit, Conjecture 8.5.) **Status: unproved; would upgrade classification from Result B to Result A.**

**Status: PARTIAL**
*Justification: Core emergences for C1 (QM), C2 (Stat Mech), C4 (spacetime) proved. Full QFT, gauge theory, and gravity emergence unproved for all candidates.*

---

## SUBSYSTEM 8: Foundational Obstruction Analysis (O1, O2, O3)

### Mathematical Definitions

**O1 (Complex structure):** The state space or amplitude space requires complex number enrichment (ℂ-valued amplitudes) rather than real-valued probabilities.

**O2 (Continuum geometry):** The state or configuration space requires a continuous, differentiable manifold structure (not merely a discrete or countable set).

**O3 (Renormalization):** The theory requires a systematic procedure for handling UV divergences arising from integrating over infinitely many degrees of freedom in a continuum.

**Unavoidable floor U1–U6** (any candidate physical foundation must satisfy):
U1: Logical non-triviality. U2: Distinguishability. U3: Composability. U4: Reproducibility. U5: Non-trivial dynamics. U6: Finite information per bounded region.

### Known Theorems

**[T] Theorem OBS-O1-TYPE:** The obstruction preventing real-probability frameworks from generating interference is **algebraic** (field extension: ℝ → ℂ). (foundational_obstruction_audit.md, Theorem 4.1.)

**[T] Theorem OBS-O2-TYPE:** The obstruction preventing discrete frameworks from being differentiable is **geometric/topological** (discrete spaces lack locally Euclidean neighborhoods). (Theorem 4.2.)

**[T] Theorem OBS-O3-TYPE:** The obstruction requiring renormalization is **analytic** (divergent integrals over continuous modes). It is a consequence of O2 + local interactions, not an independent primitive. (Theorem 4.3, Theorem 5.11.)

**[T] Theorem OBS-INDEPENDENCE:** O1 and O2 are logically independent (O1 does not imply O2; O2 does not imply O1). (Theorem 6.2.) Independence is certified by four explicit models: M00 (neither η nor O1), M10 (η only), M01 (O1 only), M11 (both η and O1), all satisfying A_C2. (Models defined in C2_separation_theorem_audit.md §Section 3 and Quantum Completion Audit §Stage 3, 2026-07-25.)

**[Cor] Corollary OBS-O2-RG (Renormalization derived):** O3 is not an independent obstruction. O2 + local interactions ⟹ O3. The minimal independent set is {O1, O2}. (Theorem 6.1, Theorem 6.3.) *(Corollary of Theorem OBS-O2-TYPE. See foundational_obstruction_audit.md, Theorem 5.11 for the full derivation.)*

**[T] Theorem OBS-UNIVERSAL-FALSE:** The implication Foundational(X) ⟹ O1 ∧ O2 ∧ O3 is FALSE as a universal statement. Finite automata satisfy U1–U6 without O1, O2, or O3. (Theorem 8.1.)

**[T] Theorem OBS-CONDITIONAL:** O1 is necessary if and only if the framework generates interference phenomena with rotational symmetry in ≥ 2 dimensions with half-integer spin objects. O2 is necessary if and only if the framework generates smooth local field equations. (Theorems 8.2, 8.3.)

### Derivations Completed

- O1 from 2D geometry + SO(2) + continuity: **partially derivable** (requires continuity as input). **[T]** (Theorem 5.1–5.5.)
- O2 from discrete counting + completeness axiom: **derivable given completeness**. **[T]** (Theorems 5.6–5.8.)
- O3 from O2 + locality + scale separation: **fully derivable**. **[T]** (Theorem 5.11.)

### Proven Results

Full dependency table (foundational_obstruction_audit.md, §6.2):

| Structure | Requirements | Independent of U1–U6? |
|-----------|-------------|----------------------|
| Shannon entropy | U2+U4+U6 | No |
| Causal order | U5 | No |
| Continuum ℝ | Discrete + completeness | Yes (completeness extra) |
| Complex ℂ | 2D space + SO(2) + continuity | Yes (2D + continuity extra) |
| Renormalization | O2 + L + scale separation | No (derived from O2+L) |
| Hilbert space | ℂ + inner product | Yes (requires ℂ) |

### Impossibility Results

**[OBS] OBS-IMP-1 (Real probability cannot produce interference):** Real-valued probability [0,1] satisfies inclusion-exclusion; destructive interference requires 2 Re(ψ₁ψ₂*) < 0, impossible for non-negative reals. (Theorems 3.1, 3.2.)

**[OBS] OBS-IMP-2 (Discrete spaces are not differentiable):** A finite set with discrete topology is not locally homeomorphic to any ℝⁿ, n ≥ 1. Differentiable structure cannot emerge from a discrete framework without a limiting procedure. (Theorem 4.2.)

### Remaining Conjectures

**[MC] OBS-C1 (Large-N forces O1 and O2):** In any framework satisfying U1–U6 with N → ∞ degrees of freedom, complex phase coherence and effective continuous field equations emerge generically. (Conjecture 8.5.) **Status: the central unproved question of the entire project.**

**[OP] OBS-OP1:** Is there a framework satisfying U1–U6 + N → ∞ that avoids O1? A positive answer (counterexample) would be a major result.

**Status: PARTIAL**
*Justification: O3 fully derived. O1 and O2 partially derivable (completeness and 2D assumptions required). Large-N universality conjecture unproved. Official result: Result B (some obstructions derivable, some independent).*

---

## SUBSYSTEM 9: Symmetric Compositional Closure (SCC)

### Mathematical Definition

**SCC** = a framework satisfying:
- **(C) Closure:** State space S closed under ⊗: S × S → S.
- **(S) Symmetry:** Group G acts equivariantly on (S, ⊗).
- **(I) Invertibility:** G acts by bijections on S.
- **(N) Normalization:** S carries a G-invariant probability measure.

Equivalently: G is a complete metric group acting continuously, transitively, and by isometries on S.

### Assumptions

- **AA1 (Compactness):** The kinematic symmetry group G is compact (or locally compact unimodular). This is a physical assumption, not derived. The Lorentz group SO(1,3) is NOT compact; this assumption applies to compact subgroups (e.g., rotation group SO(3)).

- **AA2 (Evolution commutativity):** φ(s ⊗ r) = φ(s) ⊗ φ(r) — evolution commutes with composition. Required for Route A derivation of microscopic reversibility.

### Known Theorems

**[T] Theorem SCC-1 (SCC derivability from physical principles):** SCC is derivable from {R1 (distinguishable states), R2 (composability), R3 (reproducibility), R4 (finite information), R6 (no preferred frame), R7 (unitarity)} **plus AA1 (compactness of G)**. Without AA1 the derivation is blocked. (necessity_of_SCC_audit.md, Conclusion of Phase II.)

**[T] Theorem SCC-2 (Transitivity from no-preferred-state principle):** Q8 (no preferred state) ⟹ G acts transitively on S. Non-transitive actions would imply orbit-type as a preferred structure. (physical_selection_of_SCC_audit.md, Theorem 2.4.)

**[T] Theorem SCC-3 (Continuity from stability + reproducibility):** Q7 (stability) + Q2 (reproducibility) ⟹ G is a topological group with continuous action. Discrete symmetry groups are eliminated. (Theorem 2.1.)

**[T] Theorem SCC-4 (Local compactness from finite information + stability):** Q3 (finite information density) + Q7 (stability) ⟹ G is locally compact. (Theorem 2.2.)

**[T] Theorem SCC-5 (SCC uniqueness among alternative structures):** Among S1–S10 (finite automata, causal sets, stochastic channel categories, etc.), SCC is the unique structure simultaneously generating O1 (complex structure) and O2 (continuum geometry) from minimal assumptions. (physical_selection_of_SCC_audit.md, Theorem 1.6.)

**[T] Theorem SCC-6 (Selection set):** {Q2, Q3, Q6, Q7, Q8, Q9} ⟹ SCC. Physical principles of reproducibility, finite information density, compositional closure, stability, no preferred state, and reversibility jointly force SCC. (Theorem 2.6.)

### Known Emergences from SCC

**[KR]** SCC → Haar measure (D1). [KR]
**[KR]** SCC + M8 (complex vector space) → Hilbert space via Peter-Weyl. [KR]
**[KR]** Hilbert space → Born rule via Gleason's theorem. [T] (conditional on D2)
**[KR]** Hilbert space → Schrödinger equation via Stone's theorem. [KR]
**[KR]** Classical phase space via ℏ → 0 limit. [KR]
**[KR]** Gibbs ensemble from Liouville measure. [KR]

### Failed Proofs / Reconstruction Issues

**RECONSTRUCTION:** Hilbert space derivation from SCC is a **reconstruction** (RECON), not a derivation from scratch. M8 (complex vector space) is assumed explicitly; Peter-Weyl then shows the structure is L²(G). The complex structure is input, not output at this stage. (SCC_scientific_status_audit.md §II.1.)

**GENUINE DERIVATION:** Born rule from Gleason's theorem IS a genuine derivation — given Hilbert space of dim ≥ 3, Born rule is forced. Classified as **[D]** conditional on D2. (SCC_scientific_status_audit.md §II.2.)

**RENAME:** Interference = Born rule applied to superpositions. Not a separate result. (SCC_scientific_status_audit.md §II.3.)

### Open Problems / Gaps

**[OP] PA1 (Microscopic reversibility):** Why must fundamental dynamics be invertible? Routes A and B both fail or require additional assumptions (AA2). This is an **unresolved foundational gap**. (necessity_of_SCC_audit.md §III.)

**[OP] PG (Symmetry group selection):** Why U(1) × SU(2) × SU(3) × Lorentz specifically? SCC provides a framework but does not derive the specific gauge group of the Standard Model. (SCC background §"Remaining unresolved issues".)

**[OP]** Lorentz symmetry origin within SCC: non-compact G blocks AA1. The Lorentz group emergence from SCC is not established.

**Status: PARTIAL**
*Justification: SCC derivability from physical principles (given AA1) is proved. Born rule, Hilbert space, and Schrödinger equation emerge (conditional on complex structure input). Microscopic reversibility (PA1), symmetry group selection (PG), and Lorentz symmetry remain open.*

---

## SUBSYSTEM 10: Purification and Transitivity

### Mathematical Definitions

**Purification (operational):** For every mixed state ρ of system A, there exists a system B and pure state Ψ_{AB} such that Tr_B(Ψ_{AB}) = ρ. (CDP formulation.)

**Transitivity (operational):** The group of reversible transformations acts transitively on the set of pure states: for any two pure states ψ, φ, there exists a reversible U with U(ψ) = φ.

### Known Theorems

**[T] Theorem PT-1 (Equivalence of Purification formulations):** All five formulations of Purification (operational, information-theoretic, category-theoretic, convex-geometric, dynamical/Stinespring) are mutually equivalent in any OPT satisfying causality. (purification_transitivity_origin_audit.md, Theorems I.1.1, I.1.2.)

**[T] Theorem PT-2 (Equivalence of Transitivity formulations):** The operational, geometric, information-theoretic, and thermodynamic formulations of Transitivity are mutually equivalent. (Theorems I.2.1, I.2.2.)

**[T] Theorem PT-3 (Reversibility necessary but not sufficient for Purification):** Reversibility alone does NOT imply that a dilated state is pure. (Theorem II.1.2.)

**[T] Theorem PT-4 (Information conservation necessary but not sufficient for Purification):** Information conservation alone does not imply existence of a pure joint state; mixed states can be conserved. (Phase II audit result.)

**[T] Theorem PT-5 (Ergodicity does not imply Transitivity):** A system can be ergodic within each orbit without being transitive across orbits. (Counterexample: SO(2) acting on S² by z-axis rotations.) (purification_transitivity_origin_audit.md §I.2.)

### Open Problems

**[OP] PT-OP1 (Is Purification derivable?):** No existing proof derives Purification from weaker operational principles alone. It remains an independent physical axiom in all known GPT reconstructions. (purification_transitivity_origin_audit.md.)

**[OP] PT-OP2 (Is Transitivity derivable?):** No existing proof derives Transitivity from non-transitivity-assuming principles. It remains independent.

**[OP] PT-OP3 (Minimum derivation set):** What is the weakest set of physical principles from which both Purification and Transitivity follow? This is open.

**Status: OPEN**
*Justification: Both Purification and Transitivity remain as irreducible physical axioms. Their derivability from weaker principles is unproved. They are not derivable from reversibility or information conservation alone.*

---

## SUBSYSTEM 11: Complex Hilbert Space Origin

### Mathematical Definition

The question: are complex Hilbert spaces mathematically forced by the weakest unavoidable physical principles (PR1–PR10), or are they one possibility among alternatives?

Permitted primitives only: PR1 (identity), PR2 (distinguishable states), PR3 (composition), PR4 (reproducibility), PR5 (finite information density), PR6 (reversibility), PR7 (coarse-graining), PR8 (locality), PR9 (causality), PR10 (symmetry / no preferred description).

### Known Theorems

**[T] Theorem HS-1 (Local tomography eliminates real and quaternionic QM):** PR5 + PR8 ⟹ local tomography. Local tomography eliminates real Hilbert space QM (insufficient to characterize joint states by marginals alone) and quaternionic QM (incompatible with local tomography tensor product structure). (minimal_origin_of_complex_Hilbert_spaces_audit.md.)

**[KR] Theorem HS-2 (Alfsen-Shultz classification):** JB-algebras (real Banach Jordan algebras) classify all state spaces consistent with quantum-type probability rules: real QM, complex QM, quaternionic QM, and the exceptional Albert algebra (3×3 octonionic Hermitian matrices). (KR result.)

**[KR] Theorem HS-3 (Ball state space + local tomography → ℂ-Hilbert):** Ball state space Bⁿ + local tomography ⟹ complex Hilbert space (rules out real and quaternionic). (Reconstruction theorem from literature.)

**[T] Theorem HS-4 (C* algebra excluded as primitive):** C*-algebras require complex numbers as primitives — they are eliminated as a starting point. They can appear as derived objects once ℂ is derived. (minimal_origin audit.)

**[KR] Theorem HS-5 (Gleason's theorem):** In dim ≥ 3, any probability measure on closed subspaces consistent with orthogonal decomposition is the Born rule. Unique. **[KR]**

### Open Problems

**[OP] HS-OP1 (Ball state space origin):** Why is the pure state space a ball (Bⁿ)? This is assumed, not derived from PR1–PR10 alone.

**[OP] HS-OP2 (Dimension selection):** Why complex dimension n for the Hilbert space? Not determined by the reconstruction framework.

**Status: PARTIAL**
*Justification: Given ball state space + local tomography, complex Hilbert space is forced. The ball geometry is assumed, not derived. Born rule is derived from Gleason given Hilbert space. The origin of the ball state space from PR1–PR10 is the remaining gap.*


---

## SUBSYSTEM 12: Microscopic Reversibility (PA1)

### Mathematical Definition

**PA1:** The dynamical evolution map φ: S → S is invertible (bijective on state space S).

This is the assumption that fundamental interactions are time-reversible: every microstate has a unique predecessor.

### Assumptions

- **R7 (Unitarity):** If two preparations are distinguishable at t, they remain distinguishable at t' under reversible dynamics.
- **AA2 (Evolution commutativity):** φ(s ⊗ r) = φ(s) ⊗ φ(r).

### Known Theorems

**[T] Theorem PA1-1 (Reversibility not derivable from R1–R3):** One can construct systems satisfying R1 (distinguishable states), R2 (composability), R3 (reproducibility) in which evolution is not invertible (dissipative classical systems). R7 is therefore an independent requirement. (necessity_of_SCC_audit.md, Claim I.C.)

**[T] Theorem PA1-2 (Route A: partial derivation):** Reversibility of the composite φ(s ⊗ r) follows from R2 + R7 **if** AA2 (evolution commutativity) holds. AA2 itself is an independent assumption. (necessity_of_SCC_audit.md §III.2 Route A.)

**[T] Theorem PA1-3 (Route B fails):** Reproducibility (R3) is a forward condition. It does not force invertibility. Route B (deriving PA1 from R3) fails. (Route B assessment.)

### Open Problems

**[OP] PA1-OP1:** Is there a derivation of microscopic reversibility that does not require AA2 or an equivalent assumption? This is the central unresolved physical question of the SCC foundational program.

**Status: OPEN**
*Justification: No derivation of PA1 from physically unavoidable principles alone is known. AA2 is required and is itself an independent assumption. PA1 remains an axiom, not a theorem.*

---

## SUBSYSTEM 13: Lorentz Symmetry and Gauge Theory

### Mathematical Definition

**Target:** Derive the Lorentz group SO(3,1) and the gauge group U(1) × SU(2) × SU(3) of the Standard Model from the CCA or SCC frameworks.

### Assumptions Required

- AA1 (Compactness of G): Lorentz group SO(3,1) is non-compact. This blocks derivation within the standard SCC construction.
- Continuum limit: requires large-N convergence of CCA structure.

### Known Theorems

**[KR] Theorem LG-1 (Malament):** The causal order of a Lorentzian manifold determines its metric up to conformal factor. (Established.)

**[MC] Theorem LG-2 (Approximate Lorentz from large CCA):** In the N → ∞ limit of a family of CCA structures, the automorphism group of the resulting causal structure may approach SO(3,1). Status: **conjecture only** (Bombelli-Lee-Meyer-Sorkin program). (cca_foundation_audit.md, Conjecture 2.6.)

**[KR] Theorem LG-3 (Cohesive HoTT gauge theory):** Cohesive homotopy type theory (C3 candidate) provides internal models of differential geometry, gauge fields, and principal bundles. This is a known mathematical result. (foundational_principle_audit.md, Result 3.6.)

### Open Problems

**[OP] LG-OP1 (Lorentz derivation):** Derive SO(3,1) as an internal symmetry from any candidate (C1–C5 or CCA). **Completely open.**

**[OP] LG-OP2 (Gauge group selection):** Derive U(1) × SU(2) × SU(3) from a single structural principle. **Completely open.**

**Status: OPEN**
*Justification: No derivation of either the Lorentz group or the Standard Model gauge group from any C2 candidate has been achieved. Both are completely open problems.*

---

## SUBSYSTEM 14: Quantum Field Theory and Renormalization

### Mathematical Definition

**Target:** Generate QFT (renormalization group, running couplings, vacuum structure) internally from a C2 candidate without importing QFT axioms.

### Known Theorems

**[T] Theorem QFT-1 (UV divergences from continuum + local interactions):** Any theory with continuously many degrees of freedom at arbitrarily small scales and local interactions generically diverges when summing over all modes. (foundational_obstruction_audit.md, Theorem 3.11.)

**[T] Theorem QFT-2 (RG from coarse-graining):** The Wilsonian renormalization group is derivable from composability (U3) + locality + scale hierarchy. O3 is a consequence of O2 + local interactions. (Theorem 5.11.)

**[T] Theorem QFT-3 (RG fixed points from entropy):** Fixed points of the RG flow are entropy-maximizing distributions subject to scale invariance. Derivable from Theorem CCA-5 (entropy) + scale invariance constraint.

### Open Problems

**[OP] QFT-OP1:** Generate quantum field theory — renormalization, vacuum structure, running couplings — from any single C2 candidate. No candidate achieves this. (Open Problem 8.4 of foundational_principle_audit.md.)

**[OP] QFT-OP2:** Is QFT emergence blocked by a fundamental obstruction, or merely unstudied?

**Status: OPEN**
*Justification: QFT emergence has not been achieved by any C2 candidate. O3 (renormalization) is derived from O2 + locality, but generating the full QFT structure including vacuum energy, running couplings, and anomalies from the C2 framework has not been attempted.*

---

## SUBSYSTEM 15: Experimental Validation (IBM Quantum Ramsey Data)

### Mathematical Definition

**Prediction:** Γ_φ = k_rot · ω_rot² with k_rot = 8g²s₀²r_q²τ / (3ℏ²).

**Ramsey signal:** S(t) = cos(ω_q t) · exp(−Γ_φ t).

### Experimental Results

- Empirical k_rot = 4.5 × 10⁻⁷ s (from decoherence_prediction.py, IBM Quantum data).
- Prediction confirmed: Γ_φ ∝ ω_rot² over measured range.
- Residuals within experimental uncertainty.
- No additional free parameters beyond k_rot.

### Assumptions Required for Experimental Match

The complete assumption chain:
A-PRW1, A-PRW2, A-PRW3 (PRW model) + A1–A8 (transport) + A-M1, A-M2 (independent quantum axioms) + A-HC1 through A-HC6 (Born-Markov-secular-stationary-linear-local coupling).

**Total independent assumptions for the main prediction: ≥ 17.**

### Known Theorems

**[T] Theorem EXP-1:** The measured Γ_φ ∝ ω_rot² scaling is consistent with the prediction but is not unique to the substrate framework. Any theory generating ⟨(δJ)²⟩ ∝ ω_rot² at the qubit location would produce the same scaling.

**[T] Theorem EXP-2 (Non-uniqueness of fit):** The empirical k_rot = 4.5 × 10⁻⁷ s is a fit to the data; it does not determine g, s₀, r_q, or τ individually. The substrate cannot uniquely determine the physical meaning of k_rot without additional experimental constraints.

### Remaining Open Problems

**[OP] EXP-OP1:** Determine g (quantum-classical coupling) independently of the Ramsey fit.

**[OP] EXP-OP2:** Test non-Markovian corrections to the ω_rot² scaling at high rotation frequencies.

**[OP] EXP-OP3:** Falsification test — does a substrate-independent model (pure Lindblad bath with phenomenological ω_rot dependence) fit the data equally well?

**Status: PARTIAL**
*Justification: The ω_rot² scaling is experimentally confirmed for the available dataset. However, the prediction requires ≥ 17 independent assumptions, the coupling constant g is undetermined, and the scaling is not unique to the substrate framework. The result is consistent but not uniquely confirmatory.*

---

## Open Problems (Master List)

The following table collects all open problems identified across all 15 subsystems.

| ID | Problem | Subsystem | Blocks theorem(s) |
|----|---------|-----------|-------------------|
| OP-1 | Multi-dimensional PRW uniqueness | 1 | PRW-1 (3D generalization) |
| OP-2 | Anharmonic FPUT phase geometry | 2 | FPUT-3 (anharmonic extension) |
| OP-3 | Derivation of coupling constant g | 4, 15 | HC-D4-3 (g free parameter) |
| OP-4 | Non-Markovian decoherence corrections | 4 | HC-D4-3 (Markov assumed) |
| OP-5 | PA1: Microscopic reversibility derivation | 12 | SCC-1 (requires AA2) |
| OP-6 | Purification from weaker principles | 10 | PT-1 (equivalence chain) |
| OP-7 | Transitivity from weaker principles | 10 | PT-2 (equivalence chain) |
| OP-8 | Complex Hilbert space from PR1–PR10 (ball geometry origin) | 11 | HS-3 (ball state space assumed) |
| OP-9 | CCA GNS representation theorem | 6 | CCA-1 (state spaces) |
| OP-10 | CCA causal entropy non-decrease | 6 | CCA-5 (entropy defined) |
| OP-11 | CCA causal action extremization | 6 | CCA-6 (partition function) |
| OP-12 | Lorentz group derivation | 13 | LG-2 (conjecture only) |
| OP-13 | Gauge group selection (SM gauge group) | 13 | LG-3 (cohesive HoTT partial) |
| OP-14 | QFT emergence from any C2 candidate | 14 | QFT-1 (divergences known) |
| OP-15 | Quantum gravity: simultaneous QM + Lorentzian geometry | 7 | C-IMP-1 (proved impossible currently) |
| OP-16 | Large-N universality forces O1 and O2 | 8 | OBS-CONDITIONAL (conditional result) |
| OP-17 | Uniqueness of coarse-graining projections | 7 | FPUT-3 (uniqueness partial) |
| OP-18 | C1C4 intersection generates both QM and spacetime | 7 | C1-QM + C4-Malament |
| OP-19 | Falsification of ω_rot² scaling vs. alternative models | 15 | EXP-1 (non-uniqueness proved) |

---

## Known Limitations

1. **Transport layer is mathematically equivalent to EIT/GENERIC.** The master equation [ME] introduces no new mathematics, no new predictions, and no new experimental tests beyond what is already in established transport frameworks.

2. **Quantum structure requires independent axioms.** M1 (matrix fields) and M2 (Moyal deformation) are logically independent of the transport layer and of each other. They cannot be derived from [ME] or the PRW.

3. **Coupling constant g is undetermined.** The theory's main experimental prediction depends on g, which cannot be derived from any current C2 result.

4. **Compactness assumption AA1 blocks Lorentz group.** The SCC framework requires compact symmetry groups. The Lorentz group SO(3,1) is non-compact, blocking the derivation of special relativity from SCC without modification.

5. **PA1 (microscopic reversibility) is an unresolved axiom.** No derivation from physically unavoidable principles exists.

6. **QFT not generated.** No C2 candidate generates quantum field theory.

7. **Purification and Transitivity remain irreducible axioms** in the GPT reconstruction program.

8. **Large-N universality conjecture unproved.** This conjecture would be the key to upgrading from Result B (some structures derivable, some independent) to Result A (all structures forced). It remains unproved.

---

## Research Roadmap

The following ordering reflects logical dependencies. Problems with fewer prerequisites are listed first.

**Priority 1 — Independent of all others:**
- OP-9 (CCA GNS representation): purely internal mathematical question.
- OP-10 (Causal entropy non-decrease): purely internal CCA result.
- OP-1 (3D PRW uniqueness): extension of established 1D result.

**Priority 2 — Dependent on Priority 1 or existing results:**
- OP-11 (Causal action extremization): requires CCA stability (OP-9, OP-10).
- OP-6, OP-7 (Purification and Transitivity): requires clean GPT framework.
- OP-8 (Ball geometry origin): requires GPT reconstruction framework.

**Priority 3 — Central structural questions:**
- OP-5 (Microscopic reversibility PA1): requires new principle or proof.
- OP-16 (Large-N forces O1, O2): the central question; requires new mathematical technique.
- OP-18 (C1C4 intersection): requires combining categorical and causal approaches.

**Priority 4 — Downstream of Priority 3:**
- OP-12 (Lorentz group): requires OP-16 or OP-18.
- OP-13 (Gauge group): requires OP-12.
- OP-14 (QFT): requires OP-12 + OP-13.
- OP-15 (Quantum gravity): requires OP-12 + full QM emergence.

**Priority 5 — Experimental:**
- OP-3 (Coupling constant g): requires new physical argument or experiment.
- OP-4 (Non-Markovian corrections): requires extended experiment.
- OP-19 (Falsification test): independent experimental program.

---

## Dependency Graph

The following ASCII dependency graph shows all major results and their logical dependencies. Arrows mean "is required by" (A → B: B requires A).

```
[U1–U6: Unavoidable physical floor]
    │
    ├──────────────────────────────────────────────┐
    │                                              │
    ▼                                              ▼
[PRW: A-PRW1,2,3]                         [CCA: Ax1–Ax5]
    │                                              │
    ▼                                              ├──► [Entropy, Causal depth] [T]
[Telegrapher Eq.]──(exact equiv.)──► [Maxwell-Cattaneo/EIT] [T]    │
    │                                              ├──► [†-compact → QM] [KR]
    ▼                                              │
[Full [ME]]──(special case)──► [EIT/GENERIC] [T]  ├──► [C2 → Stat Mech] [T]
    │                                              │
    ├──► [No new physics] [T]                      └──► [C4 → Spacetime] [KR]
    │                                                        │
    └──► [M1, M2 (independent axioms)]                      ▼
              │                               [Continuum limit conjecture [MC]]
              ▼                                              │
    [H_int = g J σ_z] (constitutive)                        ▼
              │                               [Lorentz group?] [OP-12]
              ▼
    [Lindblad: Γ_φ = k_rot ω_rot²] [T, conditional]
              │
              ▼
    [IBM Ramsey: k_rot = 4.5×10⁻⁷ s] [E]


[R1–R7 + AA1 (compactness)]
    │
    ▼
[SCC: G compact, transitive, complete] [T]
    │
    ├──► [Haar measure] [KR]
    │
    ├──► [M8: complex vector space (input)] + Peter-Weyl
    │         │
    │         ▼
    │    [Hilbert space L²(G)] [KR, RECON]
    │         │
    │         ├──► [Born rule via Gleason] [T, conditional]
    │         ├──► [Schrödinger eq via Stone] [KR]
    │         └──► [Classical phase space via ℏ→0] [KR]
    │
    └──► [PA1 gap] [OP-5]


[O1 (complex)] ──(independent of)── [O2 (continuum)]
    │                                       │
    ▼                                       ▼
[Hilbert space]                    [O2 + local int. → O3] [T]
                                            │
                                            ▼
                                   [Renormalization] [T, derived]


[Purification] ─────┐
                    ├──► [CDP reconstruction: full finite-dim QM] [RT]
[Transitivity] ─────┘
    (both irreducible axioms) [OP-6, OP-7]


[Ball state space + Local tomography]
    │
    ▼
[Complex Hilbert space forced] [KR, T]
    │
    └──► [Ball geometry origin?] [OP-8]
```

---

---

## OPEN ASSUMPTIONS

The following assumptions are formally documented as open. They are neither frozen (required by existing theorems as settled) nor resolved (derived from more fundamental principles). They are documented here as named objects for reference and for the mathematical verification phase.

**[OPEN ASSUMPTION S2] Coupling matrix element uniformity:**
The matrix elements of the system coupling operator A satisfy |⟨m|A|n⟩|² = h(ω_mn) for some function h: ℝ → ℝ₊.

- Status: Not assumed. Not derived. Not contradicted by current theorems.
- Required to derive: γ_mn = F(ω_mn).
- Blocks theorem: HC-GAMMA-NOFOMEGA (which proves this is not derivable without S2).
- Source: Quantum Completion Audit, Stage 8, 2026-07-25.

---

**[OPEN ASSUMPTION A-BRIDGE-τ] Transport–quantum time identification:**
The PRW relaxation time τ = 1/(2λ) (transport layer, A-TRANS-4) is identified with the bath correlation time τ_B (quantum layer, A-QUANT-6): τ_B ≡ τ.

- Status: Used implicitly in Theorem HC-4. Not yet formally verified.
- Reserved for mathematical verification phase. Do not resolve in documentation pass.

---

**[OPEN ASSUMPTION HA-1] DC approximation / white-noise limit:**
ω_mn · τ_B ≪ 1 for all relevant Bohr frequencies ω_mn.

- Status: Used in Theorem HC-D4-3. Relationship to A-QUANT-6 reserved for mathematical verification phase.
- Do not resolve in documentation pass.

---

**[OPEN ASSUMPTION HA-6] Spectral flatness (equivalent to HA-1 for T_C2 Lorentzian bath):**
J(ω_mn) = J₀ constant over the relevant frequency range.

- Status: Equivalent to HA-1 for the T_C2 Lorentzian spectral density. Reserved for mathematical verification phase.
- Do not resolve in documentation pass.

---

*End of C2_FOUNDATIONS.md*
*Document compiled: 2026-07-24; Consolidation pass: 2026-07-25*
*All claims inherit classification labels from source audits.*
*This document records the mathematical state of C2 as of the compilation date.*
*It does not extend, improve, or redesign any result.*
