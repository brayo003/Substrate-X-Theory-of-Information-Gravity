# CURRENT_C2_ONTOLOGY_MAP.md
## Frozen Ontology Map of SXC-IGC/C2

**Date:** 2026-08-22
**Method:** Direct reconstruction from C2_FOUNDATIONS.md, substrate_final_audit.md,
  projection_classification_audit.md, and all audit documents in this session.
**Classification codes:**
  A=AXIOM | B=THEOREM/DERIVATION | C=DEFINITION | D=ASSUMPTION/INTERPRETATION
  E=FREE PARAMETER | F=EMPIRICAL INPUT

No statement is promoted silently. Every claim is classified as exactly one of A–F.

---

## LAYER 0 — Primitive Ontology

| Statement | Classification |
|-----------|---------------|
| There exists a substrate that carries "information" | A (A-FPUT1 or equivalent) |
| The substrate is described by n±(x,t) — densities of rightward/leftward walkers | C (definition of dynamical variables) |
| Walker speed v is constant and uniform | A (A-PRW1) |
| Flip rate λ is constant and uniform | A (A-PRW1) |
| The substrate occupies 2D physical space (the chip plane) | D (interpretation, not derived) |
| "Information density" s = n⁺ + n⁻ | C (definition) |
| "Information current" J = v(n⁺ − n⁻) | C (definition) |

**Free parameters at this level:** v (walker speed), λ (flip rate). Both are E.

---

## LAYER 1 — Dynamical Law (PRW Balance Equations)

| Statement | Classification |
|-----------|---------------|
| ∂n⁺/∂t = −v ∂n⁺/∂x − λn⁺ + λn⁻ | B (derived from A-PRW1–3) |
| ∂n⁻/∂t = +v ∂n⁻/∂x + λn⁺ − λn⁻ | B (derived from A-PRW1–3) |
| Continuum limit Δx,Δt→0 at fixed v,λ | A (A-PRW2) |
| The flip process is Markovian | A (A-PRW3) |

---

## LAYER 2 — Coarse-Grained Telegrapher Equation

| Statement | Classification |
|-----------|---------------|
| τ s_{tt} + s_t = c²τ ∇²s | B (Goldstein-Kac theorem, DERIVED exactly) |
| τ = 1/(2λ) | B (DERIVED, definition of bath correlation time) |
| c = v (PRW propagation speed) | B (DERIVED) |
| D = c²τ = v²/(2λ) (diffusion constant) | B (DERIVED) |
| ξ_c = 2cτ (coherence/correlation length) | B (DERIVED from τ and c) |
| Telegrapher reduces to diffusion when τ→0 | B (DERIVED limit) |
| Telegrapher reduces to wave eq when τ→∞ | B (DERIVED limit) |
| Telegrapher ≡ Maxwell-Cattaneo/EIT | B (PROVED: Theorem ME-EQ-MAIN) |

**Note:** Every term in the full master equation [ME] is equivalent to a term in
Extended Irreversible Thermodynamics. C2 introduces no new transport structure.
(Theorem ME-EQ-MAIN, ME-NOV1–NOV7 in C2_FOUNDATIONS.md.)

---

## LAYER 3 — Spatial Correlator (2D case)

| Statement | Classification |
|-----------|---------------|
| Substrate generates spatial correlations between points | B (from telegrapher propagator) |
| 2D steady-state correlator C(r) = K₀(r/ξ_c) | B (DERIVED: 2D modified Bessel) |
| ξ_c = 2cτ is the spatial scale | B (DERIVED from Layer 2) |
| K₀ is also the Green's function of 2D screened diffusion | B (mathematical fact, new finding) |
| Therefore K₀ shape is NOT unique to telegrapher | B (DERIVED consequence of above) |

---

## LAYER 4 — Quantum Coupling (Conditional)

| Statement | Classification |
|-----------|---------------|
| H_int = g · J(x_q,t) · σ_z | A (A-HC5, A-HC6: ASSUMED coupling form) |
| g is the quantum-classical coupling constant | E (FREE PARAMETER — no derivation exists) |
| Born approximation: ρ_total = ρ_S ⊗ ρ_B | A (A-HC1: ASSUMED) |
| Markov approximation: τ ≪ Γ_φ⁻¹ | A (A-HC2: ASSUMED) |
| Secular approximation applied | A (A-HC3: ASSUMED) |
| Substrate autocorrelation is stationary | A (A-HC4: ASSUMED) |
| Lindblad form follows from secular approx | B (standard quantum optics derivation) |
| Lindblad operator L = σ_z (unique) | B (Theorem HC-3, uniqueness proved) |
| T₂ ≤ 2T₁ structural bound | B (DERIVED from Lindblad structure, Theorem HC-4) |
| Γ_φ = g² S_JJ(ω_rot) / ℏ² | B (DERIVED from coupling + Kubo) |
| S_JJ(ω) = 2S₀τ / (1+ω²τ²) [Lorentzian] | B (DERIVED from telegrapher correlator) |
| Γ_φ = k_rot · ω_rot² | B (DERIVED conditional on all A-HCn assumptions) |
| k_rot = 8g²S₀r_q²τ/(3ℏ²) | B (DERIVED — but contains g which is E) |
| M1 (matrix fields) axiom | A (INDEPENDENT axiom, NOT derivable from [ME]) |
| M2 (Moyal deformation) axiom | A (INDEPENDENT axiom, NOT derivable from M1 or [ME]) |

---

## LAYER 5 — Derived Observables (Conditional on Layer 4)

| Statement | Classification |
|-----------|---------------|
| Ramsey decay W(t) = exp(−Φ(t)) | B (DERIVED from Kubo formula) |
| Φ(t) = Γ_Markov·τ·[t/τ − 1 + exp(−t/τ)] | B (DERIVED exactly for Gaussian noise) |
| Non-Markovian onset: Gaussian W(t) for t≪τ | B (DERIVED) |
| Γ_φ(ω_rot) = k_rot·ω_rot² [ω_rot² scaling] | B (DERIVED conditional) |
| S_JJ(ω) reconstructed from Γ_φ(ω_rot) sweep | B (DERIVED from filter function argument) |
| C_Γ(r) = K₀(r/ξ_c) [spatial correlation] | B (DERIVED: 2D, conditional) |
| ξ_c = 2v_s·τ [Extension A] | D (INTERPRETATION: requires A-FPUT1+C5 → c=v_s) |
| c = ξ_c/(2τ_B) = constant [P3 self-consistency] | B (tautology from definitions — NOT a prediction) |

---

## LAYER 6 — Substrate Identification (GAP-7 / Extension)

| Statement | Classification |
|-----------|---------------|
| c is identified with acoustic phonon speed v_s (Extension A) | D (INTERPRETATION/ASSUMPTION, not derived) |
| c is identified with some other physical speed (Extension B) | D (ASSUMPTION — no physical candidate found) |
| A-FPUT1 + C5 → c = v_s | B (DERIVED given A-FPUT1) |
| c = v_s makes C2 equivalent to phonon bath | B (PROVED by conventional equivalence audit) |
| TLS PRW as substrate | D (FAILED — persistence mechanism absent) |

---

## LAYER 7 — Q Diagnostic

| Statement | Classification |
|-----------|---------------|
| Q(x,t) = 4c²τ²|∇ln s|² − 1 | C (DEFINITION, algebraic shortcut) |
| Q=0 is stability threshold of telegrapher | B (DERIVED, Theorem Q-1) |
| Q is coordinate-invariant | B (DERIVED, Theorem Q-2) |
| Q is equivalent to ωτ criterion for plane waves | B (DERIVED, Theorem Q-3) |
| Q predicts fundamentally new physics | FAILED (capability_audit.md §VI.1) |

---

## FREE PARAMETER INVENTORY

| Parameter | Expression | Source | Status |
|-----------|-----------|--------|--------|
| c (PRW speed) | v (walker speed) | A-PRW1 | FREE — not fixed by theory |
| λ (flip rate) | — | A-PRW1 | FREE |
| τ = 1/(2λ) | DERIVED from λ | B | FREE (λ is free) |
| g (coupling constant) | — | A-HC5 | FREE — no derivation exists |
| S₀ (noise amplitude) | from substrate state | E | FREE |
| r_q (qubit radius) | geometry | F | EMPIRICAL INPUT |
| ω_rot (rotation frequency) | experimental | F | EMPIRICAL INPUT |
| ξ_c = 2cτ | DERIVED from c, τ | B | FREE (c, τ are free) |

The theory has 4 free parameters (c, λ, g, S₀) and 2 empirical inputs (r_q, ω_rot).
Of these, only r_q and ω_rot are independently fixed before a decoherence measurement.

---

## CONSTITUTIVE ASSUMPTIONS NOT DERIVED FROM PRW

The following are ASSUMED independently of the PRW/telegrapher structure:

1. H_int = g·J·σ_z (coupling form) — A-HC5
2. Born, Markov, secular approximations — A-HC1,2,3
3. M1 (matrix fields) — independent axiom
4. M2 (Moyal deformation) — independent axiom
5. 2D geometry of substrate — D (not derived)
6. Substrate identified with any physical medium — D (not derived until Extension)

---

## PROVEN IMPOSSIBILITY RESULTS DIRECTLY RELEVANT TO EMPIRICAL PROGRAM

| Result | Statement | Source |
|--------|-----------|--------|
| ME-PRED-NONE | [ME] produces no new predictions beyond EIT | substrate_final_audit.md |
| ME-NOV1–NOV7 | No new math objects, invariants, conserved quantities from [ME] | substrate_final_audit.md |
| PRW-IMP-1 | No non-commutative structure from PRW | C2_FOUNDATIONS.md |
| HC-GAMMA-NOFOMEGA | γ_mn = F(ω_mn) not derivable without axiom S2 | quantum_completion_audit |
| K₀ not unique | K₀ = Green's function of 2D screened diffusion (not only telegrapher) | TLS_CONVENTIONAL_NULL_AUDIT.md |
| c < v_s incompatible with C5 | FPUT substrate with C5 forces c = v_s | GAP7_REDERIVATION.md |
| TLS persistence fails | No directional persistence in standard TLS | TLS_PERSISTENCE_AUDIT.md |

---

## SUMMARY: WHAT IS ACTUALLY IN THE THEORY

C2/SXC-IGC is:

1. A PRW on an unidentified substrate (speeds c, λ free)
2. Whose continuum limit is the telegrapher equation (= Maxwell-Cattaneo/EIT)
3. Coupled to qubits via an assumed H_int = gJσ_z with g free
4. Producing standard open-system dephasing under Born-Markov-secular
5. With a Lorentzian noise spectrum and K₀ spatial correlator
6. All equivalent to conventional phonon bath physics under Extension A (c=v_s)
7. With no identified substrate under Extension B

What is NOT in the theory:
- Any identification of the substrate with a known physical degree of freedom
- Any derivation of c from material parameters (GAP-7, unresolved)
- Any derivation of g
- Any new transport structure beyond EIT
- Any prediction distinguishing it from conventional open-system physics
