# GAP-7 THEORY AUDIT
## Is the substrate speed c derivable from C2?

**Date:** 2026-08-22
**Source files:** 00_THEORY_AUDIT.md, 01_PREDICTION_DERIVATION.md, C2_FOUNDATIONS.md,
  C2_FRONTIER_MAP.md, C2_MISSING_PRINCIPLES.md, interaction_hamiltonian_derivation.md

---

## 1. What GAP-7 States

From 00_THEORY_AUDIT.md §GAP-7:

> g is a free parameter. C2_FRONTIER_MAP.md (F10) confirms: no derivation of g
> exists from first principles in any framework.

The parameter table in 00_THEORY_AUDIT.md §6 explicitly shows:

| Parameter | Derivation status |
|-----------|-------------------|
| c = v | DERIVED (= v, the PRW speed) |
| c = v | UNKNOWN — not independently measured |
| ξ_c = 2cτ_B | DERIVED from c and τ_B |
| ξ_c | Requires independent measurement of c |

The confusion in the table is instructive: c is simultaneously "derived" (it equals v,
the PRW particle speed) and "unknown" (v is not constrained by any equation in C2).

---

## 2. Where c Enters the Theory

The C2 theory introduces a random-walking particle with:
- step size h
- time step Δt
- speed v = h/Δt (exact, the ratio of discrete parameters)
- reversal rate λ (transitions per unit time)

All derived results express things in terms of v and λ. These are the fundamental
parameters of the PRW. The theory is a continuum limit of this lattice model.

**c = v is a free parameter of the lattice.** It is not constrained by:
- Any equation of motion (the telegrapher equation holds for all v > 0)
- Any equilibrium condition (the stationary distribution is uniform for all v)
- Any thermodynamic argument (only λ and S₀ enter energy balance)
- Any dimensional argument (v has dimensions of [length/time]; no other velocity exists in the theory to fix it)
- Any quantum mechanical requirement (g enters separately and is also free)

---

## 3. Can c Be Derived?

### 3.1 From the Transport Equations

The telegrapher equation:
```
∂²s/∂t² + 2λ ∂s/∂t = v² ∇²s
```
This equation is consistent for any v > 0. Setting v = 0 gives a diffusion equation;
v → ∞ with λ → ∞ fixed gives another diffusion equation. No physical principle
from within C2 selects v.

### 3.2 From Dispersion Relations

The dispersion relation: ω(k) = −iλ ± √(v²k² − λ²).
The phase velocity at the critical wavevector k_c = λ/v is v_phase = v.
But k_c = 1/ξ_c itself depends on v. There is no constraint: any v gives a
self-consistent dispersion relation.

### 3.3 From Dimensional Analysis

The theory has three independent dimensional scales:
- v [m/s] (substrate speed)
- λ [s⁻¹] (reversal rate)
- g [J·m²·s] (coupling constant, also free per GAP-7)

These determine ξ_c = v/λ [m] and τ_B = 1/(2λ) [s], but their values are not fixed
internally. Adding quantum mechanics imports ℏ [J·s], which still does not constrain v.

### 3.4 From C2_MISSING_PRINCIPLES.md

The document explicitly identifies this as an open problem. It states that even ℏ
cannot be derived from within C2. The substrate speed c is in the same category:
it is an undetermined parameter representing the "stiffness" of the substrate.

### 3.5 From Boundary Conditions or Lattice Geometry

The IBM heavy-hex lattice spacing a = 200 µm defines a UV cutoff but does not
constrain v. The cutoff sets k_max = π/a ≈ 1.6 × 10⁴ m⁻¹, which combined with
a specific v would fix the maximum frequency, but v itself remains free.

---

## 4. Verdict: c Cannot Be Derived

**c is genuinely free within C2. GAP-7 is real and not resolvable from existing theory.**

The freedom is not a gap in the derivation — it is a structural feature of the
model. The PRW is specified by two parameters (v, λ). The theory contains no
principle that would select a specific v. Any value of v > 0 gives a valid
physical model with different ξ_c and τ_B values but the same mathematical structure.

This is not a computational gap. It is a **conceptual incompleteness**: C2 describes
how a substrate with speed v produces correlations, but does not say what determines
the speed of the substrate.

---

## 5. What Would Resolve GAP-7

### Option A: External physical identification
If the substrate corresponds to an independently identified physical medium, its
speed would be a property of that medium. For example:
- If the substrate is acoustic (phonons): c ≈ v_sound in the chip material (~5000 m/s)
- If the substrate is electromagnetic: c ≈ speed of light in the medium (~2×10⁸ m/s)
- If the substrate is a novel slow mode: c is unknown until measured

None of these identifications are made in the existing C2 theory.

### Option B: Additional dynamical principle
A constraint equation such as a Hamiltonian or energy principle that relates v
to other observables (e.g., chip temperature, phonon density) would fix c.
No such equation exists in the current framework.

### Option C: Dimensional transmutation via quantum coupling
If the coupling g to quantum systems were derivable and if a quantum energy
scale ℏω_q (qubit frequency) could be set equal to a classical substrate
energy scale involving v, then v could be fixed. But g is also free (GAP-7).
This path requires resolving g first.

### Option D: Experimental measurement
Measuring ξ_c and τ_B independently and computing c = ξ_c/(2τ_B) gives c
empirically. Comparing to v_sound then tests whether C2 is consistent with
phonon physics or requires a novel substrate. **This is the only currently
viable path, but it is an experimental measurement, not a theoretical derivation.**

---

## 6. Consequence for the Experimental Program

GAP-7 means ξ_c is not theoretically predicted. Therefore:

1. Any experiment that measures ξ_c and reports a result "consistent with C2"
   is not testing C2 — it is measuring ξ_c, which C2 accommodates for any value.

2. An experiment can falsify C2 if it finds that ξ_c ≠ 2c·τ_B for a measured c,
   i.e., if the self-consistency relation is violated.

3. An experiment would support C2 (but not confirm it) if it finds that c
   measured from ξ_c/(2τ_B) differs from all known conventional propagation speeds,
   suggesting a novel substrate. But this would be evidence for novelty, not proof
   of the C2 mechanism.

**The P3 self-consistency test (see DISCRIMINATOR_SEARCH.md) is the most rigorous
available test of C2 given the current state of the theory.**

---

## 7. Summary

| Question | Answer |
|----------|--------|
| Is c = v derived from C2 equations? | Yes, trivially (it equals the PRW speed v) |
| Is v independently constrained within C2? | No. Free parameter. |
| Can v be derived from dispersion, dimensions, or thermodynamics? | No. |
| Is this a fixable gap in the derivation? | No. Structural freedom. |
| What resolves it? | External physical identification OR experimental measurement |
| What experiments can use without resolving it? | P3 self-consistency test (measure c, compare to v_sound) |

**GAP-7 STATUS: FUNDAMENTAL. NOT RESOLVABLE FROM EXISTING THEORY.**
