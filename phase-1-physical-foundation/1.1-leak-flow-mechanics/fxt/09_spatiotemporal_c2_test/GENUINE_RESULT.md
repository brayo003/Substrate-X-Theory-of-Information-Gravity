# GENUINE RESULT
## The Smallest Mathematically Nontrivial Result in the C2 Theory

**Date:** 2026-08-21
**Standard:** Adversarial. Every candidate result has been attacked through
NAKED_ASSUMPTION_ATTACK.md, SUBSTRATE_ONLY_RESULTS.md, QUANTUM_MAPPING_NO_GO.md,
and GENERIC_NULL_MODEL_COMPARISON.md. Only what survives those attacks appears here.

---

## What Does NOT Qualify

The following were attacked and failed to survive as genuine C2-specific results:

- **c = v_s**: Not a theorem. Requires [THERM] or equivalent. (Attack A)
- **K₀ functional form**: Reproduced by any 2D massive scalar field. (Attack E, null model NM-2)
- **Γ_φ = k_rot ω_rot²**: Reproduced by any OU bath coupled via σ_z. (Null model NM-3)
- **Lorentzian PSD**: Generic for any exponentially correlated noise. (NM-3)
- **H_int = g J σ_z**: Not derived from substrate. Requires three external inputs. (Attack C)
- **T₁ = ∞**: Consequence of coupling choice, not substrate property. (Null model NM-1)

---

## Genuine Result G-1: Uniqueness of the Admissible Projection

**Statement:** Among all mesoscopic projections π of the harmonic FPUT chain
satisfying C1–C6, the PRW/telegrapher projection is the unique admissible one
(up to coarse-graining scale and linear recombination of action variables).

**Exact derivation:**
1. C1 (locality) forces observables into Alg{nₖ} [Theorem LOC-3]
2. C4 (positivity) forces non-negative densities
3. C2 (conservation) forces density splitting by sign of ∂ωₖ/∂k
4. C3 (finite propagation) constrains signal speed ≤ v_s
5. Steps 1–4 together uniquely identify π_RPA as the admissible projection [Main Theorem IV.3]

**Assumptions required:**
- FPUT Hamiltonian [A-FPUT] — substrate model postulate
- Six admissibility constraints C1–C6 [A-C] — design choice for what "physical" means

**What it rules out:** Every other projection of FPUT phase space (phase-retaining,
resonant, coherence matrix, winding number, etc.) is inadmissible under C1–C6.

**What it does NOT establish:** The value of c in the telegrapher equation.
Any quantum consequence. Any connection to decoherence.

**Is it C2-specific?** YES within the FPUT framework. The uniqueness relies on
the specific structure of the harmonic FPUT admissibility analysis. The general
argument (locality forces action variables) is applicable to any integrable system,
but the specific admissibility structure C1–C6 is part of the C2 program.

**Can a generic bath reproduce it?** Irrelevant — this is a theorem about the
FPUT projection structure, not an observable.

**Classification: G2 — SUBSTRATE-SPECIFIC RESULT**

---

## Genuine Result G-2: Signal Speed Upper Bound (No-Go Constraint)

**Statement:** Any admissible mesoscopic observable of the harmonic FPUT chain
has signal speed v_signal ≤ v_s = a√(K/m).

**Exact derivation:**
From C3 + FPUT dispersion: the maximum group velocity of any FPUT mode is v_s
at k→0. Mesoscopic observables are functions of the mode actions; their spatial
propagation cannot exceed the underlying mode propagation speed.

**Assumptions required:** [A-FPUT], C3 admissibility.

**What it rules out:** Any model claiming the substrate propagates information
faster than v_s = a√(K/m) is inconsistent with C1–C6.

**Classification: G2 — SUBSTRATE-SPECIFIC RESULT (negative/constraining)**

---

## Genuine Result G-3: c_eff Is NOT Uniquely Fixed (Negative Theorem)

**Statement:** The effective PRW propagation speed c_eff of the harmonic FPUT chain
is NOT determined by the substrate dynamics. It is a functional of the initial
action spectrum {nₖ} and can take any value in (0, v_s] depending on initial conditions.

**Exact derivation:**

    c_eff = v_s · [∫₀^{π/2} nₖ(u) cos(u) du] / [∫₀^{π/2} nₖ(u) du]

Counterexamples:
- nₖ = δ(k - N/2): c_eff = 0 (valid FPUT state, zero effective speed)
- nₖ = δ(k - N/4): c_eff = v_s/√2 (valid FPUT state)
- nₖ = const: c_eff = (2/π)v_s ≈ 0.637 v_s (valid FPUT state)

All three are valid solutions of the harmonic FPUT equations satisfying C1–C6.

**Assumptions required:** [A-FPUT] only. No additional assumptions.

**What it rules out:** It rules out c = v_s as a theorem. It establishes that
any specific numerical value of c requires a spectral condition (e.g., [THERM])
as an additional postulate.

**Classification: G2 — SUBSTRATE-SPECIFIC NEGATIVE THEOREM**

This result DEGRADES previous project claims about c = v_s. They were marked
"CONDITIONALLY DERIVED" in Phase 9e. This attack confirms that is the correct
classification and that "DERIVED" (unconditional) is NOT achievable.

---

## Genuine Result G-4: The Joint Constraint ξ_c = 2c τ_B Is C2-Specific

**Statement:** Given that the C2 telegrapher applies (with accepted c, τ_B), the
coherence length and bath correlation time are not independent:

    ξ_c = 2c τ_B,   with c ≤ v_s = a√(K/m)

A generic 2D Gaussian bath has independent spatial scale ξ and temporal scale τ.
The ratio ξ_c / τ_B = 2c is a constant of the substrate, not a free parameter.

**Exact derivation:**
- τ_B = 1/(2λ) from PRW reversal rate [derived, PRW-1]
- ξ_c = c/λ = 2cτ_B [derived from telegrapher mass gap, λ/c = 1/ξ_c]
- Therefore ξ_c / τ_B = 2c exactly

**Assumptions required:**
- Single-speed PRW with speed c [A-CLOSURE]
- τ_B = 1/(2λ) [derived from PRW relaxation]
- c ≤ v_s [derived from C3]

**What it rules out:** Any model in which ξ and τ are independently adjustable
cannot reproduce the constraint ξ_c = 2cτ_B with c ≤ v_s = a√(K/m) without
explicitly choosing parameters to satisfy it.

**Is it experimentally testable?** YES — in principle. Measure ξ_c (spatial
correlations) and τ_B (temporal, from Ramsey/DD) independently on the same substrate.
Compute the ratio. The C2 prediction is that this ratio equals 2c ≤ 2v_s,
consistent with the known FPUT lattice parameters.

**Currently accessible?** NO. ξ_c >> chip size at measured τ_B. Blocked by
hardware scale, not by theory.

**Can a generic bath reproduce it?** Only by imposing ξ = 2cτ as a constraint
on its free parameters. A generic bath has no reason to satisfy this constraint.
Any experimental observation that the ratio IS a constant (and equals 2c with c
consistent with the lattice phonon speed) would be a genuine C2 signature.

**Classification: G2 → G4 (IF both ξ_c and τ_B are measured independently and
the constraint is confirmed). Currently G2.**

---

## The Single Genuine Positive Result

Among G-1 through G-4, G-4 is the only result that:
- Is mathematically nontrivial
- Has a C2-specific structure (the constraint between ξ_c and τ_B)
- Cannot be reproduced by a generic bath without imposing it by hand
- Is in principle experimentally testable
- Does not require introducing a new assumption to state it

**G-4 is the genuine result: ξ_c / τ_B = 2c with c ≤ v_s.**

**The condition for it to distinguish C2 from a generic bath is:**
1. Measure ξ_c and τ_B independently
2. Show ξ_c / (2τ_B) = const across varying conditions
3. Show that const ≤ v_s = a√(K/m) = 6000 m/s (for Si)

**If all three hold: the result is not reproduced by any independent-parameter bath.**

---

## What Is NOT Established

- That c = v_s exactly (requires [THERM])
- That the coupling is H_int = g J σ_z (requires three external inputs)
- That K₀ is a C2-specific shape (reproduced by any 2D massive scalar field)
- That the decoherence rate magnitude is predicted (g is free)
- That any currently measurable observable discriminates C2 from a generic bath
