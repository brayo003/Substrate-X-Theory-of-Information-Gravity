# SUBSTRATE-ONLY RESULTS
## What the C2 Substrate Theory Establishes Before Any Quantum Apparatus

**Standard:** Only results that follow from the FPUT Hamiltonian + admissibility
constraints C1–C6, with no coupling assumptions, no thermal preparation, no quantum
apparatus, no parameter fitting, and no "physically natural" substitutions.

---

## The Substrate Theory (Pre-Quantum)

The input:

    H_FPUT = Σₖ ωₖ nₖ,   ωₖ = 2√(K/m)|sin(πk/N)|

Admissibility constraints C1–C6 applied to coarse-grained mesoscopic observables.

No qubit. No H_int. No temperature. No thermal ensemble. No PRW walker speed value.

---

## Result S-1: Unique Admissible Projection (DERIVED)

**Statement:** Under C1–C6, the unique admissible coarse-grained projection of the
harmonic FPUT chain is the PRW / telegrapher equation in terms of action-variable
densities n±(x,t).

**Proof:** Theorem FPUT-3 / Main Theorem IV.3 in projection_classification_audit.md.
C1 (locality) eliminates all phase-dependent observables. C4 (positivity) forces
non-negative densities. The only remaining generator is Alg{nₖ}, whose minimal
non-negative conserved densities split by sign of ∂ωₖ/∂k.

**Classification: DERIVED FROM DYNAMICS (B) + DERIVED FROM SYMMETRY (C)**

**What this does NOT establish:**
- The value of c in the resulting telegrapher equation
- That the PRW is a single-speed object
- Any quantum consequence

---

## Result S-2: Sound Speed Bound on Signal Speed (DERIVED)

**Statement:** The signal speed of any admissible mesoscopic evolution satisfies:

    v_signal ≤ v_s = a√(K/m)

**Proof:** C3 (finite propagation) + FPUT dispersion relation. The maximum group
velocity of any FPUT mode is v_s = a√(K/m) at k→0. No coarse-grained observable
can propagate faster than the underlying microscopic excitations.

**Classification: DERIVED FROM DYNAMICS (B)**

**What this does NOT establish:**
- Equality v_signal = v_s (strict inequality in general)
- That the PRW speed saturates this bound
- Any spectral fact about the substrate state

---

## Result S-3: Conservation of Mode Actions (DERIVED)

**Statement:** For the harmonic FPUT chain, nₖ = |Aₖ|² are exact constants of motion.

**Proof:** Liouville integrability. The harmonic chain is exactly diagonalized by Fourier
modes. Each mode is an independent harmonic oscillator with conserved action.

**Classification: DERIVED FROM DYNAMICS (B)**

**What this does NOT establish:**
- The initial values of nₖ (arbitrary initial conditions)
- Any spatial profile for the action density
- Any temporal evolution of n±(x,t) beyond the constraint nₖ = const

---

## Result S-4: The Telegrapher Equation is the Exact Continuum Limit (DERIVED)

**Statement:** For a genuine single-speed PRW (both directions at speed c, flip rate λ),
the continuum limit of the balance equations is EXACTLY the telegrapher equation:

    τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s,   τ = 1/(2λ)

**Proof:** Goldstein-Kac (1951). PRW balance equations → telegrapher equation exactly
under PRW-1 (constant speed) and PRW-2 (continuum limit). This is a mathematical
identity, not an approximation.

**Classification: DERIVED FROM DEFINITIONS (A)**

**What this does NOT establish:**
- That the FPUT dynamics is a genuine single-speed PRW (see Attack B)
- The value of c
- Any connection to quantum dynamics

---

## Result S-5: The 2D Telegrapher Green's Function is K₀ (DERIVED — CONDITIONAL)

**Statement:** Given: (a) 2D isotropic single-speed PRW, (b) stationary regime, (c)
infinite domain, (d) λ > 0 (mass gap), the equal-time equal-frequency spatial Green's
function is:

    G(r) = (1/(2πξ_c)) · K₀(r/ξ_c),   ξ_c = v/λ

**Proof:** 2D inverse Fourier transform of the Yukawa propagator (k² + m²)⁻¹ with
m = λ/v. Standard result (Abramowitz & Stegun). Derivation in 02_2D_CORRELATION_DERIVATION.md.

**Classification: DERIVED FROM DEFINITIONS (A) — conditional on geometry/isotropy/stationarity**

**What this does NOT establish:**
- That the physical FPUT substrate is 2D, isotropic, or in the stationary regime
- That the PRW speed is a single value
- Any coupling to a qubit

---

## Result S-6: Effective Speed is NOT Uniquely Fixed (NO-GO THEOREM — NEW)

**Statement:** For the harmonic FPUT chain, the effective PRW propagation speed:

    c_eff = v_s · [∫₀^{π/2} nₖ(u) cos u du] / [∫₀^{π/2} nₖ(u) du]

is NOT determined by the substrate dynamics. It is a functional of the initial action
spectrum and ranges continuously over (0, v_s].

**Proof:** Constructed in NAKED_ASSUMPTION_ATTACK.md Attack A. Explicit counterexamples:
- nₖ concentrated at k=N/2: c_eff = 0
- nₖ concentrated at k=N/4: c_eff = v_s/√2
- Flat spectrum: c_eff = (2/π)v_s
- Classical thermal spectrum: c_eff = v_s

**Classification: DERIVED FROM DYNAMICS (B) — this is a genuine negative theorem**

**This result DESTROYS the identification c = v_s as a substrate theorem.**
**It correctly establishes that c ∈ (0, v_s] is a free parameter set by initial conditions.**

---

## Result S-7: The Single-Speed PRW is NOT Exact for FPUT (NO-GO THEOREM)

**Statement:** The passage from FPUT with dispersion ωₖ = 2√(K/m)|sin(πk/N)| to a
single-speed telegrapher equation is not exact. It requires:
(a) Truncation of the velocity moment hierarchy at first order
(b) Identification of a single representative speed c_eff
(c) Discarding all higher velocity moments M_n for n ≥ 2

The exact FPUT action transport requires a velocity-distribution kinetic equation,
not a two-state telegrapher.

**Classification: DERIVED FROM DYNAMICS (B)**

---

## What DOES Survive Without Any External Input

| Result | Classification | Survives Removal of All Apparatus? |
|--------|--------------|-----------------------------------|
| S-1: Unique projection type (PRW/telegrapher) | B+C | YES — with c unspecified |
| S-2: Signal speed ≤ v_s | B | YES |
| S-3: Conservation of nₖ | B | YES |
| S-4: Telegrapher is exact for single-speed PRW | A | YES — but "single-speed" is an additional assumption |
| S-5: K₀ Green's function in 2D | A | CONDITIONAL on geometry+isotropy |
| S-6: c_eff is NOT fixed by dynamics (NO-GO) | B | YES — this is the key negative result |
| S-7: Single-speed PRW is not exact | B | YES |

**Before any quantum apparatus, external parameters, or coupling assumptions, the
substrate theory establishes: the PRW/telegrapher structure of the projection (S-1,
S-4), the signal speed upper bound (S-2), mode conservation (S-3), and the
non-uniqueness of the effective speed (S-6). The last item is a genuine no-go theorem.**

**No positive quantum prediction survives this level of analysis.**
