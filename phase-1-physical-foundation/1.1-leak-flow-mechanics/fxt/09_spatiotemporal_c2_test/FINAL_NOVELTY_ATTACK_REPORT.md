# FINAL NOVELTY ATTACK REPORT
## Complete Adversarial Audit — C2 Transport Layer

**Date:** 2026-08-21  
**Standard:** Every claim receives one of: DERIVED / CONDITIONALLY DERIVED / ASSUMED / DEFINITIONAL / CONVENTIONAL / DISPROVED / UNRESOLVED

---

## 1. Executive Verdict

**Final classification: G1 — VALID MATHEMATICAL RESULT, BUT CONVENTIONAL**

The C2 transport layer contains one genuine mathematical theorem (projection uniqueness under C1–C6) and one physics result (signal speed bound c ≤ v_s). Both are correct. Neither is novel beyond the telegrapher universality class. The uniqueness theorem contains a gap at step (3) that admits counterexamples. The physics bound is standard lattice causality.

**"C2 contains no novel physical content at the transport layer."**

---

## 2. Complete Surviving Theorem List

| Theorem | Status | Novel? |
|---------|--------|--------|
| LOC-3: C1-admissible observables = Alg{nₖ} | DERIVED | NO — standard ergodic/locality argument |
| FPUT-3: PRW is admissible under C1–C6 | DERIVED | NO — verified satisfaction of standard constraints |
| Main Theorem step (1)–(2): C1 forces Alg{nₖ} → n± split | DERIVED | NO — generic for any integrable chain with locality |
| Signal speed ≤ v_s (from C3) | DERIVED | NO — standard lattice causality / Lieb-Robinson analogue |
| Telegrapher equation is exact for single-speed PRW | DEFINITIONAL | NO — Goldstein-Kac 1951 |
| K₀ is the 2D stationary Green's function | DERIVED | NO — standard 2D Yukawa/screened Laplacian |
| ξ_c = c/γ (mean free path) | DEFINITIONAL | NO — tautology given definitions |

---

## 3. Complete Destroyed-Claim List

| Claim | Verdict | Reason |
|-------|---------|--------|
| c = v_s (PRW speed equals sound speed) | DISPROVED | Requires [THERM]; counterexamples exist for any non-thermal spectrum |
| ξ_c/τ_B = 2c is C2-specific | DISPROVED | Generic to all symmetric telegraphers; conventional phonon transport gives same |
| K₀ spatial shape is C2-specific | DISPROVED | Any 2D massive scalar field (NM-2) gives K₀; not C2-specific |
| H_int = g J σ_z is derivable | DISPROVED | Three unresolvable obstructions (OB-A, OB-B, OB-C) |
| g is derivable from substrate | DISPROVED | Requires ℏ, absent from all substrate equations |
| Γ_φ ∝ ω_rot² is C2-specific | DISPROVED | Any bath with ⟨J²⟩ ∝ ω_rot² gives same; NM-3 reproduces exactly |
| Uniqueness of PRW projection (Main Theorem step 3) | DISPROVED (gap found) | Multi-speed PRW satisfies all C1–C6; "minimal" is not a stated axiom |

---

## 4. C1–C6 Independence Analysis

| Constraint | Content | Category | Novel? |
|-----------|---------|----------|--------|
| C1 Locality | Observable at x depends only on local state | Standard locality (cf. Kadanoff-Wilson coarse-graining) | NO |
| C2 Conservation | Total action conserved by projection | Standard conservation law requirement | NO |
| C3 Finite speed ≤ v_s | Signal speed bounded by acoustic speed | Standard causality / Lieb-Robinson | NO |
| C4 Positivity | Mesoscopic densities ≥ 0 | Standard positivity of probability densities | NO |
| C5 Closure | Dynamics closed in mesoscopic variables | Standard Markovian closure assumption | NO |
| C6 Entropy non-decreasing | Second Law at mesoscopic level | Standard thermodynamic consistency | NO |

**Independence:** C1 is the sole binding constraint that eliminates phase-retaining projections (confirmed by the project itself: Theorem C5-NOT-OBSTRUCTION, C6-NOT-OBSTRUCTION). C2–C6 are necessary conditions but do not independently select the PRW — they are individually satisfied by a wide family of projections.

**Novelty of C1–C6 as a set:** The set is a reasonable and carefully stated collection of standard physical requirements. It is not novel. Any competent condensed-matter physicist constructing a coarse-grained description would impose all six conditions.

---

## 5. Projection Uniqueness Analysis (Attack A)

### The gap in step (3)

Main Theorem proof step (3) states:
> "Under C3 (finite propagation), the evolution of n±(x) must be a PDE with signal speed ≤ v_s. The **minimal** such system consistent with the microscopic dynamics is the PRW telegrapher equation."

**"Minimal" is not defined and is not among C1–C6.**

**Counterexample: Two-speed PRW**

Define:
- n₁±(x): action density of modes with k ∈ [0, N/4], speed c₁ = v_s cos(π/4) = v_s/√2
- n₂±(x): action density of modes with k ∈ [N/4, N/2], speed c₂ = v_s cos(π/2) → 0

Governing equations:
```
∂ₜn₁⁺ + c₁∂ₓn₁⁺ = −γ₁(n₁⁺ − n₁⁻)
∂ₜn₁⁻ − c₁∂ₓn₁⁻ = +γ₁(n₁⁺ − n₁⁻)
∂ₜn₂⁺ + c₂∂ₓn₂⁺ = −γ₂(n₂⁺ − n₂⁻)
∂ₜn₂⁻ − c₂∂ₓn₂⁻ = +γ₂(n₂⁺ − n₂⁻)
```

C1–C6 check:
- C1: n_i±(x) = Σ_{k∈band_i} nₖ w±ₖ(x) — local ✓
- C2: Σₓ(n₁⁺+n₁⁻+n₂⁺+n₂⁻) = Σₖ nₖ = total action ✓
- C3: signal speeds c₁,c₂ ≤ v_s ✓
- C4: nₖ ≥ 0 → n_i± ≥ 0 ✓
- C5: closed in (n₁±, n₂±) ✓
- C6: S = −∫Σᵢ(nᵢ⁺ ln nᵢ⁺ + nᵢ⁻ ln nᵢ⁻)dx non-decreasing ✓

**The two-speed PRW satisfies all six constraints and is not equivalent to the single-speed PRW (different propagation structure, different Green's function).**

**Conclusion:** The Main Theorem uniqueness claim contains a gap. Step (3) requires an unstated assumption — either a minimality axiom (C7: use fewest state variables) or a single-speed axiom (C7': all modes propagate at one speed). Without this, C1–C6 do not force uniqueness of the telegrapher; they force the telegrapher *class*, not the specific single-speed realization.

**Surviving theorem (weakened):** C1–C6 force the mesoscopic projection to use Alg{nₖ} observables with a finite signal speed. They do NOT uniquely select the single-speed PRW.

---

## 6. FPUT Necessity Analysis (Attack C)

Three standard alternative coarse-grainings of the same FPUT system:

**Alt-1: Phonon Boltzmann transport**
```
∂ₜfₖ + v_g(k)∂ₓfₖ = −(fₖ − f^eq_k)/τ_ph(k)
```
This is the standard Boltzmann equation for phonons. It satisfies C1–C6 with a k-dependent relaxation time. It does NOT produce a single-speed telegrapher — it produces a full kinetic equation. It is a valid projection of FPUT dynamics more accurate than the single-speed PRW.

**Alt-2: Green-Kubo / Generalized Langevin**
```
∂ₜJ(t) = −∫₀ᵗ K(t−t') J(t') dt'
```
For the harmonic chain, the memory kernel K(t) is known exactly and is NOT a simple exponential. This gives a non-Markovian transport equation — satisfies C5 only if "finite memory" is allowed (as explicitly permitted by C5's wording: "possibly integro-differential with finite memory"). It satisfies C1–C6.

**Alt-3: Cattaneo-Vernotte (standard phonon)**
```
τ_ph ∂ₜₜT + ∂ₜT = D∇²T
```
Identical mathematical form to the C2 telegrapher, derived from the same FPUT substrate with no C2 machinery. Satisfies C1–C6 trivially.

**Conclusion:** At least three conventional alternative coarse-grainings satisfy C1–C6. The FPUT dynamics do not uniquely produce the C2 single-speed telegrapher.

---

## 7. Telegrapher Null-Model Comparison (Attack D)

Rewriting the C2 transport structure in conventional language:

| C2 statement | Conventional statement | Source |
|-------------|----------------------|--------|
| PRW balance equations | Goldstein-Kac random walk equations | Goldstein 1951 |
| Telegrapher equation τ∂ₜₜs + ∂ₜs = c²τ∂ₓₓs | Maxwell-Cattaneo equation | Cattaneo 1948 |
| Relaxation time τ = 1/(2γ) | Phonon collision time | Standard kinetic theory |
| Correlation length ξ = c/γ | Mean free path | Maxwell 1860 |
| K₀(r/ξ) spatial correlator | 2D Yukawa Green's function | Standard field theory |
| Signal speed c ≤ v_s | Acoustic causality bound | FPUT acoustics |

**Every equation is mathematically identical to existing theory.** No new term, coefficient relation, boundary condition, or invariant exists in the C2 transport layer that is absent from conventional theory.

---

## 8. Hidden Prediction Search (Attack E)

Searched: unusual conservation laws, scaling laws, mode-selection rules, entropy relations, constraints between observables, forbidden processes, boundary behavior, nonlinear corrections.

**Finding: None survive.**

- Conservation laws: total action conservation is standard FPUT integrability
- Entropy production: standard H-theorem for the telegrapher (Kac 1974)
- Mode selection: the ± split by sign(v_g) is standard phonon chirality
- Information conservation: s = n⁺+n⁻ is conserved by C2 — same as energy conservation
- Nonlinear FPUT corrections: not derived in project ([OP], open problem)
- Non-Gaussian statistics: generic to any finite-particle system, not C2-specific

---

## 9. Information-Theoretic Content Audit (Attack F)

**The information-theoretic language is interpretational, not dynamical.**

The substrate equations are:
```
∂ₜs + ∂ₓJ = 0
∂ₜJ + c²∂ₓs = −(1/τ)J
```

Replacing "information density" with "energy density" and "information flux" with "heat flux" yields the Cattaneo-Vernotte equation for heat transport. The equations are identical. No information-theoretic quantity (entropy, mutual information, Fisher information, channel capacity) enters the dynamics. The information interpretation is a relabeling.

**Test:** Remove the information-theoretic interpretation entirely. Replace s → T (temperature density), J → q (heat flux). The predictions do not change. Therefore the information layer is interpretational.

**Classification: INTERPRETATIONAL, NOT DYNAMICAL.**

---

## 10. Quantum Novelty Audit (Attack G)

With H_int removed, the substrate predicts no quantum effect. The substrate is a classical field theory. Its state space is the simplex Δ₁ (confirmed: F3, PRW-IMP-1). No Hilbert space emerges.

The general allowed coupling H_int = Σᵢ Fᵢ(s,J) Oᵢ(qubit) has:
- Infinite-dimensional family of substrate operators Fᵢ
- Continuous S² family of qubit operators Oᵢ
- Coupling constant g — free
- Qubit orientation — free

Nothing is uniquely predicted. **No quantum observable survives without coupling assumptions.**

---

## 11. Null-Model Domination Matrix

| C2 Prediction | NM1 (PRW) | NM2 (2D OU) | NM3 (OU noise) | NM4 (Cattaneo) | Unmatched? |
|--------------|-----------|------------|----------------|----------------|-----------|
| Telegrapher equation | IDENTICAL | — | — | IDENTICAL | NO |
| ξ = c/γ | IDENTICAL | — | — | IDENTICAL | NO |
| K₀(r/ξ) | — | IDENTICAL | — | IDENTICAL | NO |
| Lorentzian PSD | — | — | IDENTICAL | IDENTICAL | NO |
| Γ ∝ ω_rot² | — | — | IDENTICAL | — | NO |
| c ≤ v_s | — | — | — | IDENTICAL | NO |
| Ballistic front t < τ_B | — | — | NO | — | YES (unmeasurable) |

**Every currently measurable C2 prediction is dominated by at least one conventional null model.**

The sole unmatched item (ballistic causal front) is not currently measurable and is a generic property of any hyperbolic PDE, not C2-specific.

---

## 12. Counterexample Register

**CE-1:** Initial spectrum nₖ = δ(k − N/2) → c_eff = 0.  
Destroys: c = v_s as unconditional theorem.

**CE-2:** Two-speed PRW (n₁±, n₂±) with c₁ ≠ c₂, both ≤ v_s.  
Satisfies C1–C6. Is not equivalent to single-speed PRW.  
Destroys: uniqueness in Main Theorem step (3).

**CE-3:** Cattaneo-Vernotte phonon model.  
Produces ξ = 2cτ with c ≤ v_s from standard physics.  
Destroys: ξ/τ = 2c as C2-specific.

**CE-4:** 2D Ornstein-Uhlenbeck scalar field.  
Produces K₀(r/ξ) spatial correlator from (-∇²+m²)G = δ in 2D.  
Destroys: K₀ as C2-specific.

---

## 13. Physicist Whiteboard Test (Attack J)

Presented to a condensed-matter physicist:

> "Here is an FPUT chain. Here are C1–C6. They produce a telegrapher equation. Signal speed bounded by acoustic speed. Correlation length related to transport time."

**Physicist's response at each step:**

- FPUT chain: "Standard harmonic lattice."
- C1–C6: "Reasonable coarse-graining requirements."
- Telegrapher equation: "That's the Cattaneo-Vernotte/Maxwell-Cattaneo equation. Textbook."
- Signal speed ≤ v_s: "Of course. You can't propagate faster than the phonon group velocity."
- ξ = c/γ: "That's the mean free path."
- K₀ in 2D: "That's the 2D Yukawa propagator."

**The physicist never says "That does not follow from standard theory."**

**RESULT: NO NOVEL PHYSICAL EQUATION FOUND.**

---

## 14. Exact Remaining Assumptions

1. [A-FPUT]: FPUT harmonic Hamiltonian is the substrate model.
2. [A-C]: Admissibility constraints C1–C6 are the correct filter.
3. [A-single-speed]: A single representative speed c describes the multi-mode transport (unstated, required for step 3 of Main Theorem).
4. [THERM]: Substrate is in thermal equilibrium (required for c = v_s).
5. [A-lin]: H_int linear in J (required for quantum coupling).
6. [P-deph]: Pure dephasing = σ_z coupling (required for quantum prediction).
7. [A-g]: Coupling constant g is empirical.

Assumptions 3–7 are all unresolved. Assumption 3 was previously unacknowledged.

---

## 15. Exact Remaining Free Parameters

| Parameter | Fixed? | How |
|-----------|--------|-----|
| a, K, m (FPUT lattice) | YES | Material properties |
| v_s = a√(K/m) | YES | Derived from lattice |
| c | NO | Bounded by v_s; value requires [THERM] |
| γ (flip rate) | NO | Phenomenological / empirical |
| g (coupling constant) | NO | Empirical only |
| τ_B = 1/(2γ) | NO | Derived from γ, which is free |
| ξ_c = c/γ | NO | Derived from c and γ, both free |

Three independent free parameters remain: c (or equivalently the spectral state), γ, and g. No prediction is parameter-free.

---

## 16. Final Classification

```
G1 — VALID MATHEMATICAL RESULT, BUT CONVENTIONAL
```

**Justification:**

The surviving mathematical content — that C1-admissible observables of the harmonic FPUT chain are elements of Alg{nₖ}, and that this forces a transport equation with finite signal speed bounded by v_s — is correct. It follows from stated premises. However:

- It is equivalent to stating that a local coarse-graining of an integrable system produces a finite-speed transport equation for the conserved densities.
- This is a known result in mathematical physics (cf. hydrodynamic limits of integrable systems).
- The specific form (telegrapher) is the Cattaneo-Vernotte equation, known since 1948.
- The uniqueness claim (Main Theorem step 3) has a gap: multi-speed PRW satisfies C1–C6.
- No quantum prediction survives without coupling assumptions not derivable from the substrate.

G2 would require the result to distinguish the C2 substrate from conventional condensed-matter models. It does not.

---

## 17. Final Statement

**The strongest thing this project currently possesses is:**

> "A proof that locality (C1) forces the coarse-grained observables of the harmonic FPUT chain into Alg{nₖ}, and that among linear projections of this algebra, finite-speed transport (C3) requires a hyperbolic PDE with signal speed bounded by a√(K/m) — a correct but conventional consequence of integrable lattice acoustics that is reproduced by standard Cattaneo-Vernotte phonon transport without any C2 ingredients."
