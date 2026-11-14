# SUBSTRATE CLOSURE AUDIT

**Date:** 2026-08-22  
**Scope:** Can the four new microscopic ingredients (ℏ, Δε, H_B, λ) required for
CONDITIONAL CLOSURE be derived from, or are they already latent in, the original
SXC-IGC substrate ontology?  
**Method:** Systematic forensic search through the established C2 axiom set,
all proved theorems, the dimensional monoid, and every energy-like quantity in the
substrate. No redesign. Strict reporting.  
**Prior work consumed:** QUANTUM_ONTOLOGY_AUDIT.md, QUANTUM_PARENT_DERIVATION.md,
QUANTUM_ENVIRONMENT_HISTORY_AUDIT.md, FINAL_C2_MICROSCOPIC_CLOSURE_AUDIT.md,
C2_structural_obstruction_audit.md, C2_info_energy_bridge_audit.md,
C2_separation_theorem_audit.md, C2_MISSING_PRINCIPLES.md, C2_FOUNDATIONS.md,
interaction_hamiltonian_uniqueness.md, prw_deeper_substrate_audit.md,
microscopic_derivation.md, COMPLETE_MASTER_EQUATION.md.

Label convention inherited from source audits:  
[T] Proved theorem | [KR] Known rigorous result | [OBS] Proved obstruction |
[A] Assumption | [P] Postulate | [D] Derivation | [OPEN] Open problem

---

## 1. Original Ontology

### 1.1 Primitive Variables

The SXC-IGC substrate is defined at two levels.

**PRW microscopic level** (from microscopic_derivation.md §1.2, C2_FOUNDATIONS.md §1):

| Variable | Type | Units | Definition |
|----------|------|-------|------------|
| n⁺(x,t) | real scalar field | info/m³ | density of right-moving information quanta |
| n⁻(x,t) | real scalar field | info/m³ | density of left-moving information quanta |
| v = c | real positive constant | m/s | PRW particle speed |
| λ_rev | real positive constant | s⁻¹ | direction-reversal rate |

No other independent variables exist at the PRW level. This inventory is
complete (interaction_hamiltonian_uniqueness.md §1, exhaustive audit, 2026-07-21).

**Macroscopic transport level** (derived, not primitive):

| Variable | Definition | Units |
|----------|-----------|-------|
| s = n⁺+n⁻ | total information density | info/m³ |
| J = c(n⁺−n⁻) | net information flux | info/(m²·s) |
| τ = 1/(2λ_rev) | mean free time | s |
| D = c²τ | diffusion coefficient | m²/s |
| E_sub = ½c²s²+½J² | substrate "energy-like" density | info²·m⁻⁴ (NOT Joules) |

### 1.2 Primitive Constants

The complete set of constants appearing in all substrate equations:

| Constant | Units in C2 | Origin |
|----------|------------|--------|
| c | m/s | PRW particle speed |
| τ = 1/(2λ_rev) | s | PRW relaxation time |
| s₀ | info/m³ | reference information density |
| r_q | m | qubit interaction radius |
| α | info/(J·s) | information-energy coupling — **ESTABLISHED INDEPENDENT** [OBS F3] |
| β | info·s/J | energy-flow coupling — **ESTABLISHED INDEPENDENT** [OBS F3] |
| γ_F | info/(N·s) | force coupling — **ESTABLISHED INDEPENDENT** [OBS F3] |
| g | J·m²·s/info | interaction Hamiltonian coupling — **ESTABLISHED INDEPENDENT** [OBS F2] |
| k | kg·m³/(info·s) | gravitational coupling — **NEW, EMPIRICAL** |

### 1.3 Dimensional System

**Established (C2_FOUNDATIONS.md, C2_structural_obstruction_audit.md):**

The C2 transport layer operates in dimensional monoid:

```
D_C2 = { m^a · s^b : a, b ∈ ℚ }
```

This monoid does NOT contain the generator kg.

**Physical consequence [OBS F3, proved 2026-07-24]:**

> No polynomial combination of {c, τ, s₀, r_q} produces units of Joules
> (J = kg·m²·s⁻²). The C2 transport layer is a dimensionally massless theory.

### 1.4 Conservation Laws

From the PRW balance equations (Theorem PRW-1, C2_FOUNDATIONS.md §1):

- **Total information is conserved** in the source-free PRW: ∂s/∂t + ∂J/∂x = 0.
- **No energy conservation law exists** in the C2 transport layer — the substrate has no energy variable with units of Joules.
- **No momentum conservation law exists** — P_sub = sJ has units info²/(m⁵·s), not kg·m/s.
- The **FPUT action variables** nₖ = |Aₖ|² are constants of motion of the harmonic FPUT chain (Theorem PRW-4). They have units of action-squared divided by mass — they carry kg.

### 1.5 State Space

**[OBS F3, C2_FOUNDATIONS.md §1]:** The PRW state space is the probability
simplex Δ₁ ≅ [0,1], a classical convex set.
It is NOT the Bloch sphere S² (quantum state space) and NOT ℂ² (Hilbert space).

No quantum state space emerges from the PRW transport layer. This is a proved
impossibility (Theorem PRW-IMP-1: commutative observable algebra).

### 1.6 Interaction Rules

The only interaction in the PRW is the direction-reversal at rate λ_rev.
There is no particle creation, no energy exchange, no bath.

### 1.7 C2 Master Equation Primitives

The full extended master equation introduces additional constants:

```
τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s − ∇·(sv_sub + χsu) + αE + β∇·(Ev_sub) + γ_F F − σ_irr
```

The constants α, β, γ_F are classified as follows (C2_structural_obstruction_audit.md §2):

- **α** requires kg (via J = kg·m²·s⁻²): independent of C2 transport primitives [OBS F3].
- **β** requires kg: independent [OBS F3].
- **γ_F** requires kg (via N = kg·m·s⁻²): independent [OBS F3].
- **E** (appearing in αE) is physical energy density with units J/m³ = kg·m⁻¹·s⁻²: absent from the transport layer.

### 1.8 Summary: What the Original Ontology Contains

The original ontology contains: a 1D discrete-direction stochastic transport
process, its macroscopic continuum limit, a set of phenomenological coupling
constants that carry kg, and a reference to external physical energy (E) whose
source is not internal to the substrate.

**It does not contain:**
- Any quantum structure (Hilbert space, operator, ℏ)
- Any mass scale (kg is absent from all derived substrate quantities)
- Any natural frequency or energy level structure
- Any environment or bath
- Any particle creation mechanism

---

## 2. Required Microscopic Ingredients

From FINAL_C2_MICROSCOPIC_CLOSURE_AUDIT.md §14, the four ingredients required
for CONDITIONAL CLOSURE of C± = αE are:

| Ingredient | Physical role | Units | Current status in C2 |
|------------|--------------|-------|----------------------|
| ℏ | action scale; quantum of action | J·s = kg·m²·s⁻¹ | ABSENT; irreducibly independent [HC-2 failed] |
| Δε = ε₁−ε₀ | energy gap of substrate information quanta | J = kg·m²·s⁻² | ABSENT; no discrete energy levels in PRW |
| H_B | bosonic thermal bath Hamiltonian | — | ABSENT; no environmental DoF in PRW |
| λ_coup | bath-system creation coupling | J^{1/2}·s^{-1/2} or equiv. | ABSENT; free parameter |

The following sections test each ingredient against the full original ontology.

---

## 3. ℏ / Action Scale

### 3.1 Definition of the Test

Can any combination of existing C2 primitives {c, τ, s₀, r_q, info} produce a
quantity with dimensions of action [J·s = kg·m²·s⁻¹]?

### 3.2 Exhaustive Dimensional Analysis

Form the most general combination:

```
X = c^a · τ^b · s₀^c · r_q^d
```

Dimensions:

```
[X] = (m/s)^a · s^b · (info/m³)^c · m^d
    = info^c · m^{a+d-3c} · s^{b-a}
```

For [X] = J·s = kg·m²·s⁻¹:

```
info^c = 1              → c = 0 (treating info as dimensionless)
m^{a+d} = m²            → a + d = 2
s^{b-a} = s^{-1}·s^0   → Wait: [J·s] = kg·m²·s⁻¹, so s exponent = -1... 
```

Correcting:
```
[J·s] = kg · m² · s⁻¹
```

The exponent of s in [X] is (b − a). We need b − a = −1 AND m exponent = 2 AND kg exponent = 1.

**The exponent of kg in [X] is 0 regardless of a, b, c, d** — because none of the
primitives {c [m/s], τ [s], s₀ [info/m³], r_q [m]} carries kg.

Therefore no combination of C2 primitives produces kg¹. Action requires kg.
Action cannot be constructed from C2 primitives.

**[OBS ℏ-1]:** The action scale ℏ cannot be constructed from the original C2 ontology.
The obstruction is dimensional: kg ∉ D_C2.

### 3.3 Candidate Action-Like Quantities in C2

Two candidate "action-like" structures have been previously identified in the project:

**Candidate A1: Causal entropy × time — S_causal · τ**

S_causal (C2_NOVELTY_AUDIT.md NC-2) has units "nats" (dimensionless). S_causal · τ
has units [s]. This is not [J·s] — it lacks kg.

**Candidate A2: PRW coherence length as action**

ξ_c = 2cτ has units [m]. ξ_c · mass = action only if a mass is available.
No mass is available. This fails.

**Candidate A3: HC-1 (C2_MISSING_PRINCIPLES.md Problem 2)**

HC-1 proposed ℏ = m_eff · c · ξ_c, but identified m_eff as a new parameter not
derivable from C2. The principle was assessed as merely relocating the problem.

**Candidate A4: HC-2 (C2_MISSING_PRINCIPLES.md Problem 2)**

HC-2 proposed ℏ = ΔS_min/ω_char, but required the unproved CCA-C3 conjecture
and an undefined "minimum action." Assessed as conditional on an unproved theorem.

**Verdict:** No existing C2 quantity constitutes or generates ℏ.
C2_MISSING_PRINCIPLES.md explicitly states (with MEDIUM confidence):

> "The Planck constant gap cannot be closed by adding a single non-circular
> principle to the current proved results. Within the current proved C2 mathematics,
> ℏ is an irreducibly independent constant."

**[OBS ℏ-2]:** ℏ is irreducibly independent of the original C2 ontology.
This was established 2026-07-24 and is not overturned here.

---

## 4. Energy Gap

### 4.1 Definition of the Test

Does the substrate contain a discrete energy spectrum with a characteristic
gap Δε = ε₁ − ε₀ [J]?

### 4.2 Energy Structure of the PRW

The PRW has no energy variable in its state description. The state of a PRW
particle is (position, direction): (x, ±). There is no energy coordinate.

The macroscopic E in the master equation is an *external* energy density
(supplied from outside the substrate — a field representing mass-energy of
physical matter, not a PRW property). This is explicit in:

- microscopic_derivation.md §1.8: "Term αE: Particles are created at rate αE
  per unit volume... E is the external mass-energy density."
- C2_structural_obstruction_audit.md F3: "A bridge I → E is logically independent
  of A_C2."

**The PRW transport layer has no internal energy variable with units of Joules.**
There is no energy spectrum and no energy gap.

### 4.3 FPUT Lattice Energy Structure

The FPUT harmonic chain has normal mode energies E_k = ℏωₖ (or classically E_k = ωₖ Aₖ²
where A_k is the mode amplitude). This contains:

- A discrete frequency spectrum ωₖ = 2√(K/m)|sin(πk/N)| [s⁻¹]
- Mode energies Eₖ with units [kg·m²·s⁻²] = [J]
- A mass scale m (particle mass) and spring constant K (both carry kg)

**However:** The FPUT structure is the *pre-projection* microscopic theory. The
PRW is the unique C1–C6 admissible projection of the FPUT, and the projection
discards all energy information: by Theorem FPUT-3, only action variables nₖ = |Aₖ|²
survive, and their energy interpretation requires the mass scale m_FPUT [kg].

The PRW does not inherit the FPUT energy spectrum. Theorem FPUT-3 explicitly
shows that the PRW is the result of *discarding* the energy/frequency structure
of the FPUT lattice.

**[OBS Δε-1]:** The projected (PRW) layer has no discrete energy spectrum.
The pre-projection (FPUT) layer has a discrete energy spectrum but carries kg
(via particle mass m_FPUT and spring constant K), which are not in D_C2.

### 4.4 Candidate Energy Scales

**Candidate E1: k_rot = 4.5 × 10⁻⁷ s (empirical decoherence parameter)**

k_rot has units [s], not [J]. It is not an energy.

**Candidate E2: c²τ (diffusion coefficient D)**

[D] = m²/s. Not an energy.

**Candidate E3: s₀c² (information-density × speed²)**

[s₀c²] = (info/m³)(m/s)² = info/m. Not an energy (and contains info, not kg).

**Candidate E4: CCA rank × energy unit**

The CCA rank r is dimensionless. As shown in C2_info_energy_bridge_audit.md §3
Route 1, E = E₀ · r requires E₀ [J] as a free parameter and is empirically wrong
(produces UV catastrophe for FPUT). Rejected.

**Verdict:** No natural energy gap emerges from the original ontology.

**[OBS Δε-2]:** Δε is dimensionally forbidden from D_C2 and structurally absent from
the PRW state space. A discrete energy spectrum requires introducing kg.

---

## 5. Environment

### 5.1 Definition of the Test

Does the original substrate already contain degrees of freedom that can
legitimately serve as a thermal bath (H_B)?

A legitimate bath must satisfy:
1. Large number of degrees of freedom
2. Separation of timescales (τ_bath << τ_system)
3. Correlation decay (bath autocorrelation decays to zero)
4. Effective irreversibility
5. Markovian limit of reduced dynamics
6. Energy exchange capability
7. Positivity of reduced dynamics (complete positivity)

### 5.2 Candidate Bath Structures

**Candidate B1: Unresolved high-frequency PRW modes**

The PRW is a continuum theory. Its "modes" are spatial Fourier modes
q_k(t) ~ e^{ikx}. Each mode oscillates (or decays) at rate k·c with damping 1/τ.

- DoF count: uncountably many spatial modes ✓
- Timescale separation: modes with k >> 1/(cτ) damp at rate >> 1/τ ✓ (formally)
- Correlation decay: the PRW Green's function decays as exp(−t/τ) at fixed x ✓
- Irreversibility: the PRW is NOT irreversible — the telegrapher equation is
  time-reversal invariant modulo the first-order term ∂s/∂t. The damping
  term makes it dissipative but not thermodynamically irreversible (no entropy
  production in the source-free PRW).
- Energy exchange: The PRW has no energy variable [OBS Δε-1]. Its "modes"
  carry information quanta, not energy. Energy exchange with a bath requires
  an energy variable — absent.
- Complete positivity: The PRW is a classical stochastic process, not a
  quantum channel. Complete positivity is undefined for it.

**Verdict for B1:** The PRW modes provide timescale separation and mode
richness, but FAIL on energy exchange (no energy variable) and fail on
thermodynamic irreversibility. They cannot serve as a thermal bath for an
energy-exchange process.

**Candidate B2: Discarded FPUT modes (phase information φₖ)**

When the FPUT is projected to the PRW, the phase variables φₖ are discarded
(Theorem FPUT-3, C2_FOUNDATIONS.md §2). The discarded sector is the torus T^M
(Theorem FPUT-4, geometry: flat, π₁ = ℤ^M, trivial holonomy).

- DoF count: M modes ≈ N/2 modes for large chain ✓
- Timescale separation: φₖ evolves at rate ωₖ (acoustic frequencies) —
  can be fast compared to PRW relaxation rate 1/τ ✓ (for high-k modes)
- Correlation decay: Phase fluctuations δφₖ of the FPUT chain do decay due
  to mode-mode coupling (anharmonic terms). In the harmonic limit, φₖ is
  exactly periodic (no decay). Decay requires anharmonicity β ≠ 0. ✓/✗ (conditional)
- Irreversibility: Anharmonic FPUT (β ≠ 0) does thermalize and exhibits
  decay of correlations. ✓ (if β ≠ 0)
- Energy exchange: FPUT modes carry energy E_k = ℏωₖ (quantum) or
  E_k = ωₖnₖ (classical action). Energy exchange between FPUT modes is
  possible via anharmonic coupling. ✓ (but carries kg via nₖ·ωₖ)
- Complete positivity: Not applicable (classical dynamics)

**The critical problem:** The FPUT phase sector was explicitly discarded at
the projection step because it is NOT locally recoverable (Theorem FPUT-3,
Theorem FPUT-2). Any use of φₖ as a bath would require un-discarding the
discarded sector — which means the substrate is no longer the PRW, but the
full FPUT chain.

**Verdict for B2:** The discarded FPUT phases can in principle serve as a
classical bath IF (a) anharmonicity β ≠ 0 is included (not in the current
harmonic PRW theory), AND (b) the projection back to PRW from FPUT is
re-examined to allow energy exchange. This is a non-trivial extension,
not a use of existing structure.

**Candidate B3: Distant spatial PRW modes (long-wavelength limit)**

The PRW in a large spatial volume has long-wavelength modes that evolve
slowly (timescale ~ L/c for system size L). These could act as a low-frequency
environment for a local sub-region.

- DoF count: finite for any finite-volume system. Bath requires N_bath → ∞.
  This is a thermodynamic limit requirement, not automatically satisfied.
- Timescale separation: long-wavelength modes are SLOW (τ_bath ~ L/c >> τ_local).
  The required condition is τ_bath << τ_system. Long-wavelength modes are the
  WRONG direction — they are slower, not faster, than the system.

**Verdict for B3:** Fails timescale separation. Long-wavelength modes cannot
serve as a Markovian bath for local dynamics.

**Candidate B4: External substrate (v_sub field)**

The master equation contains a substrate flow velocity v_sub(x,t). This field
represents the background medium through which information moves. It is treated
as externally prescribed, not as an independent dynamical degree of freedom
with its own Hamiltonian.

A bath requires its own Hamiltonian dynamics, energy spectrum, and equilibrium
distribution. v_sub is a prescribed drift field, not a bath.

**Verdict for B4:** v_sub is not a bath. It has no Hamiltonian, no energy spectrum,
and no equilibrium distribution defined within C2.

### 5.3 Verdict on Environment

**[OBS H_B-1]:** No existing C2 degree of freedom constitutes a thermal bath
capable of driving energy → information creation.

The closest candidate (discarded FPUT phases, B2) requires:
- Anharmonicity β ≠ 0 (currently forbidden in the harmonic PRW derivation)
- Re-inclusion of the discarded sector (reverses the FPUT → PRW projection)
- Energy units (kg) for the mode energies E_k = ωₖnₖ

Using B2 would mean replacing the PRW with the full anharmonic FPUT chain —
which is a substantive change to the substrate, not a discovery of hidden
bath structure already present in the PRW.

---

## 6. Coupling

### 6.1 Definition of the Test

Can the bath-system coupling λ_coup be derived from existing substrate constants
{c, τ, s₀, r_q}?

### 6.2 Dimensional Analysis of λ_coup

From FINAL_C2_MICROSCOPIC_CLOSURE_AUDIT.md §12:

```
α = (2π/ℏ) |λ_coup|² ρ_bath(Δε/ℏ) f_thermal
```

For α to have units [info/(J·s)]:

```
[λ_coup]² = [α] · [ℏ] / [ρ_bath] = (info/J·s) · (J·s) / s = info/s
```

Therefore [λ_coup] = √(info/s).

Treating info as dimensionless: [λ_coup] = s^{-1/2}.

Can s^{-1/2} be constructed from {c [m/s], τ [s], s₀ [info/m³], r_q [m]}?

General combination:
```
c^a · τ^b · s₀^c · r_q^d  must have units  s^{-1/2}
```

```
(m/s)^a · s^b · (info/m³)^c · m^d = s^{-1/2}
→ info^c = 1                     → c = 0
→ m^{a + d - 3c} = m^{a+d} = 1  → a + d = 0  → d = -a
→ s^{b-a} = s^{-1/2}            → b - a = -1/2
```

This system has solutions: e.g., a = 1, d = -1, b = 1/2 gives:

```
λ_coup ~ c · τ^{1/2} / r_q
```

with units: (m/s) · s^{1/2} / m = s^{-1/2} ✓ (if info is dimensionless)

**So dimensionally, a coupling scale can be constructed from existing primitives.**

However: this dimensional match is necessary but not sufficient. The question
is whether the physics singles out a specific combination.

### 6.3 Physical Identification of λ_coup

The coupling λ_coup governs the rate at which a high-energy substrate quantum
exchanges energy with the bath and creates a new information quantum. Physically,
it is analogous to:
- The dipole moment in quantum optics (determines spontaneous emission rate)
- The electron-phonon coupling in condensed matter
- The Fermi constant in weak interactions

In all known physical examples, such coupling constants are NOT derivable from
the transport theory of the medium alone. They require:
- The specific matrix element of the interaction between system and bath
- The spatial overlap integral of system and bath wavefunctions
- A fundamental interaction (electromagnetic, phononic, etc.)

The PRW transport layer describes the long-wavelength, coarse-grained information
dynamics. It has no information about microscopic interaction matrix elements.

**Dimensional argument:** c · τ^{1/2} / r_q is a dimensionally valid form for
λ_coup, but its coefficient (the dimensionless prefactor) is unconstrained by
any C2 equation or principle. It can take any positive value.

**[OBS λ-1]:** λ_coup is dimensionally constructible from existing primitives
(unlike ℏ and Δε, which require kg). However, its specific value is not
determined by any existing C2 equation. It is a free parameter.

**Classification:** λ_coup is CALIBRATED, not DERIVED. Its dimensions are
consistent with C2 but its magnitude requires empirical measurement.

---

## 7. Full Derivation Chain

Attempting the complete chain using only the original ontology:

```
STEP 1: original substrate  →  microscopic state
```
The substrate state is (n⁺(x,t), n⁻(x,t)) — two real fields.

**Status: EXISTING — the PRW is the microscopic state.**

---

```
STEP 2: microscopic state  →  quantum structure
```
Requires assigning a Hilbert space to the PRW particle direction and energy.
The direction sector {+, −} is naturally a two-level system ℂ².
The energy sector requires energy levels ε₀, ε₁ [J].

**Direction → ℂ²:** The identification of {+, −} with a qubit is an assumption.
The direction is a classical binary variable. Making it quantum requires the
complex field extension O1 (C2_separation_theorem_audit.md). This is NOT derived
from the PRW — it is a structural extension.

**Energy sector:** Requires Δε [J] — not present in original ontology [OBS Δε-2].

**Status: [A] ASSUMED — requires O1 (complex structure) and new energy scale Δε.**

---

```
STEP 3: quantum structure  →  energy spectrum
```
Once the quantum structure is in place, the energy spectrum {ε₀, ε₁} is defined.
The gap Δε = ε₁ − ε₀ must be specified.

**Status: [A] ASSUMED — Δε is a new primitive, not derivable from C2 primitives.**

---

```
STEP 4: energy spectrum  →  environment
```
The environment must be a bosonic bath H_B with modes at frequency ω ≈ Δε/ℏ.
No such bath exists in the original ontology [OBS H_B-1].

**Status: [A] ASSUMED — H_B is a new ingredient. The discarded FPUT phases are
the closest candidate but require re-inclusion of β ≠ 0 anharmonicity (not in
the PRW derivation).**

---

```
STEP 5: environment  →  interaction
```
The interaction H_int = Σ_k λ_k (b_k + b_k†) ⊗ (creation of info quantum)
requires λ_coup [free parameter, OBS λ-1].

**Status: [A] ASSUMED — H_int form follows from physical plausibility but
λ_coup is not determined by existing equations.**

---

```
STEP 6: interaction  →  reduced dynamics
```
Born-Markov-secular approximation gives Lindblad equation with rate α.
The approximations are justified when:
- τ_bath << τ_creation (Markovian): plausible for high-frequency bath modes ✓
- Born: weak coupling λ_coup << Δε·τ_bath: constraint on λ_coup (not fully determined) ✓/✗
- Secular: Δε/ℏ >> α: self-consistency condition ✓ (provided Δε and ℏ are given)

**Status: [APPROX] APPROXIMATED — standard controlled approximations, but
their validity requires ℏ and Δε.**

---

```
STEP 7: reduced dynamics  →  C± = αE
```
Under Born-Markov-secular and high-temperature approximation:

```
C±_eff = (2π/ℏ) |λ_coup|² ρ_bath(Δε/ℏ) f_T · e±  =  α · e±
```

Total: C_total = α(e⁺ + e⁻) = αE ← matches target.

**Status: [D] DERIVED — once ℏ, Δε, H_B, λ_coup are given, the functional
form C± = αE follows by exact derivation.**

---

### Summary of Step Status

| Step | Status | New input required |
|------|--------|-------------------|
| 1. PRW → microscopic state | EXISTING | None |
| 2. Microscopic → quantum structure | [A] ASSUMED | O1 (complex structure), Δε |
| 3. Quantum → energy spectrum | [A] ASSUMED | Δε [J] |
| 4. Energy → environment | [A] ASSUMED | H_B (bath Hamiltonian) |
| 5. Environment → interaction | [A] ASSUMED | λ_coup (coupling constant) |
| 6. Interaction → reduced dynamics | [APPROX] APPROXIMATED | ℏ (for secular condition) |
| 7. Reduced → C± = αE | [D] DERIVED | None (given prior steps) |

**4 of 7 steps require new input. Only 2 of 7 are existing or derived.**

---

## 8. Dimensional Closure

### 8.1 The F3 Obstruction Revisited

The C2 dimensional monoid is:
```
D_C2 = { m^a · s^b }   (no kg)
```

The CONDITIONAL CLOSURE mechanism introduces:
- ℏ: [J·s] = kg·m²·s⁻¹  → introduces kg generator ✗
- Δε: [J] = kg·m²·s⁻²   → introduces kg generator ✗
- H_B: Hamiltonian, [J]   → introduces kg generator ✗
- λ_coup: [s^{-1/2}]     → does not introduce kg ✓
- α: [info/(J·s)]         → requires kg (via J) ✗

**The quantum mechanism does NOT resolve the F3 dimensional obstruction.**

It introduces the missing kg generator via ℏ and Δε. This is mathematically
equivalent to the η constant introduced in C2_separation_theorem_audit.md §2
(Model M10: adding kg to the dimensional monoid).

**Specifically:**
```
Δε [J/quantum] = η [J/info] × n₀ [info/quantum]
```
where n₀ is the information content per quantum (a dimensionless normalization).

So Δε = η × n₀ — the energy gap IS exactly the η constant (energy per information
quantum) already identified as the minimal mass-scale extension.

**[T Dim-1]:** The CONDITIONAL CLOSURE mechanism is dimensionally equivalent to
adding the η constant (the energy-per-information-quantum scale) to the C2
ontology. It does not solve F3; it instantiates the η extension previously
identified as the minimal required addition.

### 8.2 ℏ vs. η

Are ℏ and η independent requirements?

**From the Fermi golden rule formula:**
```
α = (2π/ℏ) |λ_coup|² ρ_bath(Δε/ℏ)
```

If Δε = η n₀, then Δε/ℏ is a dimensionless ratio (= frequency × ℏ/ℏ).
For α to have units [1/(J·s)]:

```
[1/ℏ] · [λ_coup²] · [ρ_bath] = 1/(J·s)
[s/(kg·m²)] · [s⁻¹] · [s] = s/(kg·m²)
```

This is NOT [1/(J·s)] = [s/(kg·m²)]. ✓ (They are equal: J·s = kg·m²·s⁻¹ →
1/(J·s) = s/(kg·m²)). So the formula is dimensionally consistent.

**Are ℏ and Δε independently required, or is only their ratio Δε/ℏ (a frequency)
needed?**

Looking at α more carefully:
```
α = (2π/ℏ) |λ_coup|² ρ_bath(ω₀)   where ω₀ = Δε/ℏ
```

If we substitute λ̃² = |λ_coup|²/ℏ, then:
```
α = 2π λ̃² ρ_bath(ω₀)
```

Here [λ̃²] = [λ_coup]²/[ℏ] = s⁻¹/(kg·m²·s⁻¹) = 1/(kg·m²).

This still requires kg. The combination λ̃ = λ_coup/√ℏ absorbs ℏ but
does not eliminate kg.

**ℏ and Δε are independently required only in the following sense:**
- Δε (or η) introduces kg into the ontology.
- ℏ is additionally required for the Markovian/secular conditions
  (the condition Δε/ℏ >> α requires both Δε and ℏ independently).
- If ℏ is expressed as ℏ = η × τ₀ for some characteristic time τ₀,
  then ℏ is not independent of η — but τ₀ is a new free parameter.

**[T Dim-2]:** At the level of dimensional closure, ONE new mass-carrying
constant (η or equivalently Δε) is the minimal requirement. ℏ adds a second
new constant — but ℏ was already identified as separately irreducible in
C2_MISSING_PRINCIPLES.md Problem 2. Both are needed and neither derives from
the other within the existing framework.

---

## 9. Parameter Count

| Quantity | Existing primitive? | Derivable from existing? | New free parameter? |
|----------|--------------------|--------------------------|--------------------|
| c | YES (PRW particle speed) | — | — |
| τ | YES (reversal time 1/2λ_rev) | — | — |
| s₀ | YES (reference density) | — | — |
| r_q | YES (qubit radius) | — | — |
| g (decoherence coupling) | NO — free parameter | NO [OBS F2] | YES (existing gap) |
| α (info-energy coupling) | NO — phenomenological | NO [OBS F3] | YES (existing gap) |
| ℏ | NO | NO [C2_MISSING §2] | YES — new |
| Δε | NO | NO [OBS Δε-2] | YES — new |
| H_B (bath) | NO | NO [OBS H_B-1] | YES — new structure |
| λ_coup | NO | DIMENSIONAL match only | YES — free, calibrated |
| T (bath temperature) | NO | NO | YES — new |

**Before CONDITIONAL CLOSURE extension:** 6 existing primitives + 2 existing
free parameters (g, α) = 8 total.

**After CONDITIONAL CLOSURE extension:** 6 existing + 2 existing gaps + 5 new
(ℏ, Δε, H_B structure, λ_coup, T) = 13 total.

**Net addition: 5 new free parameters** (ℏ, Δε, λ_coup, T, plus the bath
spectral form ρ_bath which contains additional free parameters).

This is a significant parameter increase. The extension is not parameter-free.

### 9.1 Are Any of the New Parameters Constrained by Existing Observations?

- **ℏ:** Empirically fixed by quantum mechanics (ℏ = 1.055 × 10⁻³⁴ J·s).
  Not derivable from C2 but numerically known.
- **Δε:** Unknown. Must be measured. It sets the energy scale of substrate
  information quanta. No existing C2 result constrains it.
- **λ_coup:** Unknown. Must be measured. Analogous to g in the decoherence chain.
- **T:** Temperature of the bath. Could be measured contextually.
- **ρ_bath(ω):** Functional form of the bath spectrum. Unknown without a model
  of the physical environment.

---

## 10. No-Go Tests

### No-Go Test 1: Dimensional Impossibility of ℏ

**Claim:** ℏ cannot be derived from {c, τ, s₀, r_q}.

**Proof:** ℏ has dimensions [kg·m²·s⁻¹]. No combination c^a τ^b s₀^c r_q^d
contains kg (shown in §3.2). Therefore no such combination has dimensions
[kg·m²·s⁻¹]. QED.

**Result: NO-GO confirmed.** [OBS ℏ-1]

---

### No-Go Test 2: Energy Level Structure in PRW

**Claim:** The PRW cannot have a discrete energy spectrum without introducing kg.

**Proof:** A discrete energy spectrum requires energy levels εₙ [J] = [kg·m²·s⁻²].
The PRW state is (n⁺, n⁻) with units [info/m³]. No combination of PRW quantities
has units [J]. The unit kg is absent from D_C2. QED.

**Result: NO-GO confirmed.** [OBS Δε-1,2]

---

### No-Go Test 3: PRW Bath Impossibility

**Claim:** The source-free PRW cannot serve as a bath for an energy-exchange process.

**Proof:** A thermal bath for an energy-exchange process must be able to absorb or
donate energy [J]. The PRW has no energy variable in units of Joules [OBS Δε-1].
Therefore it cannot absorb or donate energy. It can exchange information quanta,
but information creation (C±) requires energy input (C± = αE requires E [J/m³]).

An information-exchange bath might generate information from information — i.e.,
C± ∝ s rather than C± ∝ E. But that is NOT the required source term. The
original C2 source law specifically requires C± ∝ E [J/m³], not ∝ s [info/m³].

**Result: NO-GO confirmed for energy-bath role of source-free PRW.** [OBS H_B-1]

---

### No-Go Test 4: Symmetry Obstruction for Creating kg from Massless Theory

**Claim:** No continuous symmetry transformation of the massless PRW theory can
generate a mass scale.

**Proof:** The telegrapher equation τ s_tt + s_t = c²τ s_xx is invariant under
the rescaling s → λs (linear scaling). Its dimensional analysis involves only
{m, s}. Continuous symmetry transformations of a massless theory (no kg) generate
only transformations preserving the dimensional monoid D_C2. Introducing kg
corresponds to extending D_C2 — this is a discrete extension (adding a generator),
not reachable by continuous transformations.

By analogy with classical field theory: no renormalization group flow of a
massless theory generates a mass at zero coupling. A mass term must be
introduced explicitly (dimensional transmutation requires a running coupling,
which itself requires ℏ — circular).

**Result: NO-GO confirmed.** Mass scale kg cannot emerge from the massless PRW
by any dynamical mechanism internal to the theory.

---

### No-Go Test 5: Information Quanta Cannot Self-Amplify Into Energy

**Claim:** C± ∝ E cannot arise from a substrate mechanism that creates
information from information (C± ∝ s).

**Proof:** If C± ∝ s, then the master equation source term is αE → α's for
some α' [1/s]. This is the autocatalytic source (term ε₀b₁n⁺ in INTERACTION_SPACE_AUDIT.md).
This produces exponential growth (C± ∝ s) rather than energy-proportional creation.
The original C2 master equation specifically requires C± ∝ E [J/m³], not ∝ s [info/m³].
These are dimensionally incompatible: [α][E] = (info/J·s)(J/m³) = info/(m³·s) ✓
versus [α'][s] = (1/s)(info/m³) = info/(m³·s) ✓.

Both are dimensionally valid sources. But the original C2 master equation
requires the energy-proportional form. A substrate mechanism producing C± ∝ s
would generate a *different* master equation, not the one the project requires.

**Result:** C± ∝ s is dimensionally valid but is NOT the required source term.
The required C± ∝ E cannot arise without E [J/m³] — which requires kg. QED.

---

### Summary of No-Go Results

| Test | Result | Nature of obstruction |
|------|--------|----------------------|
| 1. ℏ from C2 primitives | NO-GO | Dimensional (kg absent) |
| 2. Discrete energy from PRW | NO-GO | Dimensional + structural |
| 3. PRW as energy bath | NO-GO | No energy variable in PRW |
| 4. Mass from massless theory | NO-GO | Dimensional monoid extension |
| 5. C± ∝ E from info-only source | NO-GO | Requires E [J/m³] with kg |

All five no-go tests succeed. The original ontology cannot generate the
required ingredients.

---

## 11. Minimal Extension If Required

### 11.1 What the No-Go Results Require

The no-go results jointly prove that crossing from the massless information
transport theory (D_C2 = {m,s}) to the energy-creation mechanism (requiring kg)
requires at minimum:

**ONE new dimensional generator:** Adding kg to D_C2.

This was already identified in C2_separation_theorem_audit.md as the η constant:

```
η [J/info] = kg·m²·s⁻²/info
```

η is the energy cost per information quantum. It is exactly the bridge between
the information sector and the energy sector.

In the microscopic language of CONDITIONAL CLOSURE:

```
η ↔ Δε/n₀    where n₀ is the information content per quantum (dimensionless)
```

or equivalently:

```
η ↔ ε₀       (energy of the ground-state information quantum)
```

### 11.2 Is One New Constant Sufficient?

Adding η alone:
- Gives Δε = η × n₀ ✓
- Does NOT give ℏ (still independently required for quantum dynamics)
- Does NOT give H_B (requires a physical environment model)
- Does NOT give λ_coup (free parameter)

Adding η + ℏ:
- Allows construction of a natural frequency: ω₀ = Δε/ℏ = η n₀/ℏ ✓
- Allows Fermi golden rule rate: α = (2π/ℏ)|λ|²ρ_bath(ω₀) ✓
- Still requires H_B specification and λ_coup ✗

**Minimum viable extension for CONDITIONAL CLOSURE:**

```
EXTENSION SET E_min = { η, ℏ, ρ_bath(ω) }
```

with λ_coup treated as a single free (calibrated) parameter, analogous to g
in the existing decoherence chain.

This adds exactly:
- η: one new dimensional constant (energy/info scale) [GENUINE NEW PRIMITIVE]
- ℏ: one new action-scale constant (known from quantum mechanics) [GENUINE NEW PRIMITIVE]
- ρ_bath(ω): one new environmental function (bath density of states) [NEW ENVIRONMENTAL STRUCTURE]
- λ_coup: one new free parameter [CALIBRATED, not derived]

### 11.3 Theoretical Status of the Extension

**Does E_min preserve the project's central claim?**

The project's central claim is: *the C2 substrate (a minimal information transport
theory) can account for quantum decoherence and information creation.*

The decoherence part (Γ_φ = k_rot ω²) is established with existing primitives
(given g as a calibrated parameter). This is not affected.

The information creation part (C± = αE) requires E_min. After adding E_min:
- α becomes derived rather than phenomenological
- The mechanism (energy → information via quantum emission) is physically clear
- The theory gains predictive power: α = f(η, ℏ, λ_coup, ρ_bath)

**However:**

The original C2 claim was that the substrate *already* contains the information
creation mechanism — that αE arises from the substrate dynamics with no additional
input. This claim is FALSE. The substrate requires the extension E_min to generate
αE microscopically.

**The honest classification is:**

After adding E_min, the theory is a GENUINELY EXTENDED theory (Model M11 in the
C2_separation_theorem_audit nomenclature) — not the original C2 (Model M00).

---

## 12. Comparison With Previous Audits

| Step | Previous status | This audit |
|------|----------------|-----------|
| F3: kg absent from D_C2 | ESTABLISHED (2026-07-24) | CONFIRMED — unchanged |
| ℏ independent of C2 | ESTABLISHED (2026-07-24) | CONFIRMED — unchanged |
| g independent (F2) | ESTABLISHED (2026-07-24) | CONFIRMED — unchanged |
| PRW has no quantum state space | ESTABLISHED (2026-07-21) | CONFIRMED — unchanged |
| FPUT phases = classical torus | ESTABLISHED (2026-07-21) | CONFIRMED — T^M geometry, no quantum bath |
| η as minimal mass extension | IDENTIFIED (2026-07-24) | CONFIRMED — η is exactly Δε/n₀ |
| C±_eff ∝ ΔN₁₁ from unitary parent | NEW (2026-08-22, Q7) | CONFIRMED — not same as αE |
| Bath mechanism → αE | NEW (2026-08-22, FINAL audit) | CONFIRMED — requires E_min |
| PRW as energy bath | NOT TESTED previously | NEW NO-GO: PRW cannot be energy bath |
| FPUT phases as candidate bath | PARTIALLY TESTED (D2 candidate, prw_deeper_substrate_audit) | NEW: explicit bath-function test fails |
| λ_coup dimensional construction | NOT TESTED previously | NEW: dimensionally constructible, value free |
| Minimal extension = {η, ℏ, ρ_bath} | IDENTIFIED (2026-07-24 as {η, O1}) | REFINED: O1 is for quantum structure of substrate particle; η, ℏ are for C± |

**New finding not in previous audits:**

The PRW mode structure and discarded FPUT phases were tested explicitly as
candidate baths and both fail (for different reasons). This test was not
previously completed. Previous audits identified that a bath was needed but
did not test whether the substrate's own structure could serve as one.

---

## 13. Final Classification

### B — EXTENSION REQUIRED, BUT PHYSICALLY COHERENT

The C2 substrate, in its original form, cannot generate C± = αE. The derivation
requires adding the extension set E_min = {η, ℏ, ρ_bath, λ_coup}.

This classification is NOT C (structural failure) because:
- The mechanism is mathematically sound and physically natural
- The extension is minimal and well-defined
- The added ingredients are physically motivated (η is the info-energy bridge;
  ℏ is the quantum of action; ρ_bath characterizes the physical environment)
- The result (C± = αE) follows by controlled derivation once E_min is in place
- The number of new free parameters (2 new constants + 1 environmental function
  + 1 coupling) is comparable to the parameter count of any effective field theory

This classification is NOT A (full substrate closure) because:
- Five independent no-go theorems are proved
- ℏ and η (= Δε/n₀) are dimensionally impossible to derive from {m, s}
- The PRW contains no bath degrees of freedom that can drive energy → info creation
- Every step from quantum structure through environment to C± requires new input
- The parameter count increases by 5

---

## 14. Exact Scientific Status of SXC-IGC

### 14.1 What Has Actually Been Derived

The following results are proved theorems within the C2 framework (no new inputs required):

1. **Telegrapher equation from PRW** [KR, T PRW-1]: τs_tt + s_t = c²τs_xx follows
   exactly from the PRW balance equations with τ = 1/(2λ_rev), c = v.

2. **PRW is unique local projection of FPUT** [T FPUT-3]: Under admissibility
   constraints C1–C6, the PRW is the only admissible coarse-graining of the
   harmonic FPUT chain. Phase information is locally irrecoverable.

3. **Qubit decoherence rate from substrate** [D, validated]: Given the additional
   inputs g [J·m²·s/info], ℏ, and the interaction form H_int = g·J·σ_z, the
   decoherence rate Γ_φ = k_rot·ω_rot² is derived and numerically validated
   against IBM Quantum data.

4. **Born rule from complex Hilbert space** [KR, Gleason]: Given complex Hilbert space
   (requiring O1 extension), the Born rule follows.

5. **K₀ spatial correlation shape** [D, validated]: Given the PRW with parameter c,
   the spatial decoherence correlator Γ(r) ~ K₀(r/ξ_c) is derived (spatiotemporal
   C2 test, 09_spatiotemporal_c2_test/).

6. **C±_eff ∝ Im(g*χ) from unitary quantum parent** [D, new 2026-08-22]:
   A minimal quantum parent (ℂ² × ℂ²) produces coherence-driven source, but
   this is not the required αE form.

7. **C±_bath = αE from Fermi golden rule** [D with E_min, CONDITIONAL CLOSURE 2026-08-22]:
   Given E_min = {η, ℏ, H_B, λ_coup}, the C± = αE source law is derived by
   standard open-system quantum mechanics.

### 14.2 What Remains Assumed

The following are physical assumptions or external inputs that are NOT derived
from the substrate:

1. **g [J·m²·s/info]:** The interaction coupling between the substrate current
   and qubits. Calibrated empirically. Cannot be derived from {m, s} [OBS F2].

2. **α [info/(J·s)]:** In the original theory: purely phenomenological, value
   unknown. After the E_min extension: derived as α = f(η, ℏ, λ_coup, ρ_bath),
   but η, λ_coup, and ρ_bath remain free.

3. **E (external energy density) [J/m³]:** The physical energy field that drives
   information creation. Treated as an external input throughout all C2 derivations.

4. **O1 (complex structure):** The extension of the PRW observable algebra from
   real to complex. Required for quantum state structure. Not derived from PRW.

5. **Born-Markov-Secular approximations:** Standard and justified, but
   each introduces an assumption about timescale separation.

### 14.3 What Is Genuinely New in This Project

1. **Identification of PRW as unique admissible projection of FPUT** [T FPUT-3]:
   This is a genuine new result. The C1–C6 framework and its application to the
   FPUT chain is original.

2. **Decoherence prediction Γ_φ ∝ ω_rot²** [D, validated]: The specific prediction
   Γ_φ = k_rot ω² from the substrate-qubit interaction is a specific numerical
   prediction absent from generic open-system models.

3. **Spatial K₀ correlation shape** [D, validated]: The prediction Γ(r) ~ K₀(r/ξ_c)
   for spatially correlated decoherence is a novel and non-trivial result.

4. **C±_bath = αE derivation** [CONDITIONAL, new 2026-08-22]: Identifying the
   mechanism as spontaneous emission from two-level substrate quanta into a
   thermal reservoir is new to this session. The derivation is correct given E_min.

5. **Precise identification of the dimensional obstruction (F3)** [OBS, 2026-07-24]:
   The explicit proof that kg ∉ D_C2 and the four-model independence certificate
   (M00, M01, M10, M11) is rigorous original work.

### 14.4 What Is Inherited From Earlier Work

1. The Goldstein-Kac telegrapher equation and its relationship to the PRW [KR, 1951/1974].
2. The Born-Markov-Lindblad formalism for open quantum systems [KR, standard].
3. Gleason's theorem and Born rule derivation [KR].
4. GPT reconstruction of quantum mechanics from operational axioms [KR, Hardy/Masanes-Müller].
5. Fermi's golden rule / Wigner-Weisskopf for spontaneous emission [KR].
6. Caldeira-Leggett / spin-boson open system model [KR].

### 14.5 Is C± = αE a Consequence of the Original Substrate?

**No.**

C± = αE is NOT a consequence of the original C2 substrate.

The original substrate (PRW / telegrapher) is a massless scalar information
transport theory. It conserves information. It contains no energy variable with
units of Joules. It cannot create information from energy because it has no energy.

C± = αE is a consequence of the **extended** substrate — the original PRW plus
the extension set E_min = {η, ℏ, H_B, λ_coup}.

The extended theory is physically coherent and mathematically well-defined.
The mechanism is physically natural (quantum spontaneous emission analogue).
But it is an extension, not a derivation from the original theory.

### 14.6 Minimum New Ontology Required

```
E_min = { η [J/info], ℏ [J·s], ρ_bath(ω), λ_coup }
```

| Element | Physical meaning | Status |
|---------|-----------------|--------|
| η [J/info] | Energy per information quantum (info-energy bridge) | New fundamental constant |
| ℏ [J·s] | Quantum of action | New fundamental constant (known empirically) |
| ρ_bath(ω) | Bath density of states at frequency Δε/ℏ | New environmental function |
| λ_coup | Bath-system creation coupling | New free parameter (calibrated) |

### 14.7 Does the Extension Preserve the Project's Central Claim?

**Partially.**

The project's central claim has two parts:

**Part A (preserved):** The classical PRW substrate, when coupled to qubits via
H_int = g·J·σ_z, predicts decoherence Γ_φ = k_rot·ω_rot². This is a specific,
validated prediction that differs from generic Lindblad decoherence in its
spatial and frequency structure.

**Part B (changed):** The C± = αE source term is NOT internal to the substrate.
After the extension, it becomes the Markovian limit of a quantum spontaneous
emission process, requiring three new physical constants {η, ℏ, λ_coup} and
an environmental model.

**The project began with the claim that a single minimal substrate generates both
decoherence AND information creation.** This claim must be revised:

> The substrate generates decoherence from its classical transport structure
> (Part A: confirmed). Information creation from energy (Part B: C± = αE)
> requires extending the substrate with a mass/energy scale η and quantum
> structure ℏ. These extensions are physically coherent but are not derivable
> from the original massless transport theory.

**The project's core transport results (Part A) are not invalidated.**

**The claim of derivational completeness (that C± arises from the substrate alone) is refuted.**

The honest scientific status is:

> SXC-IGC is a partially closed theory. Its transport and decoherence sectors
> are well-derived. Its information creation sector is not closed and requires
> two new fundamental constants (η, ℏ) plus a bath model. The theory is
> physically coherent as an extended framework but is not self-contained as
> originally claimed.

---

*End of SUBSTRATE_CLOSURE_AUDIT.md*  
*Date: 2026-08-22*  
*All no-go results are proved from the established C2 axiom set.*  
*No C2 structure has been redesigned in the course of this audit.*  
*The extension E_min is identified but not implemented — this is an audit, not a redesign.*
