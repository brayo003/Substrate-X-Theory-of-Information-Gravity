# G2 SURVIVING RESULT ATTACK
## Adversarial Audit: Is ξ_c/τ_B = 2c Genuinely C2-Specific?

**Date:** 2026-08-21
**Target:** The single G2 result surviving the previous audit.

---

## Attack 1 — Exact Derivation of ξ_c/τ_B = 2c

### Step-by-step trace with classifications

**Step 1.** PRW balance equations [A — definition of the model]:

    ∂ₜn⁺ + c∂ₓn⁺ = −γ(n⁺ − n⁻)
    ∂ₜn⁻ − c∂ₓn⁻ = +γ(n⁺ − n⁻)

**Step 2.** Define macroscopic fields [A — definition]:

    s = n⁺ + n⁻,   J = c(n⁺ − n⁻)

**Step 3.** Derive transport equations [B — exact algebra]:

    ∂ₜs + ∂ₓJ = 0
    ∂ₜJ + c²∂ₓs = −2γJ

The coefficient 2γ in the J-equation comes from:
∂ₜ(c·n⁺ − c·n⁻) = −c²∂ₓ(n⁺+n⁻) − γ(n⁺−n⁻)·c − γ(n⁻−n⁺)·c = −c²∂ₓs − 2γJ

**The factor 2 is here, in the damping term, and it comes from both n⁺ and n⁻
contributing to the flux damping simultaneously. It is forced by the PRW symmetry
(equal switching rates γ for both directions) plus the definition J = c(n⁺−n⁻).**

**Step 4.** Telegrapher equation [B — exact]:

    ∂ₜₜs + 2γ∂ₜs = c²∂ₓₓs

Writing τ = 1/(2γ): τ∂ₜₜs + ∂ₜs = c²τ∂ₓₓs

**Step 5.** Spatial correlation length from the static Green's function [A+B]:

The static limit (ω = 0) of the k-space propagator is:

    G(k, ω=0) ~ 1/(k² + (2γ/c)²·(1/4)·4) = 1/(k² + (γ/c)²)

Wait — more carefully: from ∂ₜJ = −c²∂ₓs − 2γJ, the Laplace-Fourier transform at
ω=0 gives s(k) ~ 1/(k² + m²) where m = 2γ/c × (something).

Let me be precise. The stationary (ω=0) spatial correlator of J satisfies:

    S_JJ(k, 0) ∝ 1/(k² + m²),   m = γ/c

Therefore: ξ_c = 1/m = c/γ [B — exact from Green's function]

**Step 6.** Definition of τ_B [A — pure definition]:

    τ_B ≡ 1/(2γ)

**This is a DEFINITION, not a physical result.** The physical damping rate of J is 2γ.
The "correlation time" τ_B is defined as half the inverse damping rate of J.
Alternatively τ_B is the half-life of the temporal autocorrelation of J:

    C_JJ(t) ∝ exp(−2γ|t|),   so τ_B = 1/(2γ) is the 1/e time divided by 2.

The choice τ_B = 1/(2γ) rather than τ_B = 1/γ is a **convention**.

**Step 7.** Compute the ratio [A — arithmetic]:

    ξ_c / τ_B = (c/γ) / (1/(2γ)) = 2c

**The factor 2 is not a physical prediction. It is a convention artifact.**

It arises from defining τ_B as HALF the decay time of C_JJ(t). If instead
τ_B were defined as the full decay time (τ_B = 1/γ), the ratio would be:

    ξ_c / τ_B = (c/γ) / (1/γ) = c   [no factor 2]

If τ_B were defined as the integral ∫₀^∞ C_JJ(t)/C_JJ(0) dt = 1/(2γ) = same as
the current definition — so actually the integral convention coincides with the
1/(2γ) convention for a pure exponential.

**Bottom line:** The physical invariant is:

    ξ_c · γ = c

which is the mean free path relation. ξ_c/τ_B = 2c follows only with the
specific convention τ_B ≡ 1/(2γ).

---

## Attack 2 — Is This Generic to the Telegrapher Class?

### The generic PRW telegrapher

    ∂ₜn⁺ + v∂ₓn⁺ = −γ(n⁺ − n⁻)    [arbitrary v, γ]
    ∂ₜn⁻ − v∂ₓn⁻ = +γ(n⁺ − n⁻)

This is ANY symmetric persistent random walk. Parameters: v (speed) and γ (flip rate).

Deriving ξ and τ:
- Spatial decay rate: m = γ/v → ξ = v/γ
- Temporal decay of J: rate = 2γ → τ = 1/(2γ)  [with C2 convention]
- Ratio: ξ/τ = 2v

**YES — ANY symmetric PRW telegrapher gives ξ/τ = 2v with the same convention.**

This is not C2-specific. It is a mathematical identity of the symmetric PRW.

---

## Attack 5 — Standard Phonon Transport

The Cattaneo-Vernotte (2nd sound) equation for phonon heat transport:

    τ_ph ∂ₜₜT + ∂ₜT = D∇²T,   D = c_s² τ_ph

This IS the telegrapher equation with the phonon mean free time τ_ph.

Parameters:
- τ_ph = phonon scattering time (= τ_B in C2)
- c_s = phonon group velocity (= c in C2)
- Mean free path: ℓ = c_s τ_ph
- Spatial decay: ξ = 2D/c_s = 2c_s τ_ph = 2c τ_B ← **IDENTICAL TO C2**

Standard condensed matter phonon physics gives ξ/τ = 2c (with the same convention).

**This is the conventional phonon mean free path relation.** It appears in
textbook treatments of thermal conductivity, second sound, and heat pulse propagation.
It predates C2 by at least 70 years (Cattaneo 1948, Chester 1963).

---

## Attack 9 — The Upper Bound c ≤ v_s

**Is c ≤ v_s novel?**

The bound c ≤ v_s = a√(K/m) says: "no mesoscopic excitation propagates faster
than the maximum acoustic group velocity of the underlying FPUT modes."

This is equivalent to the statement: "the coarse-grained dynamics cannot propagate
information faster than the underlying microscopic dynamics allow."

This is a GENERIC causality bound. It is an instance of the more general principle:
any coarse-grained model derived from a microscopic model inherits the microscopic
signal speed bound. In FPUT this is v_s. In a relativistic field theory it is c_light.

Compare with Lieb-Robinson bounds for quantum lattice systems, which give
|[A(t), B]| ≤ C exp(v_LR t - |x-y|) for some v_LR. The C2 bound c ≤ v_s is the
classical analogue of a Lieb-Robinson bound for the harmonic lattice.

**The Lieb-Robinson / Lightcone bound is a generic structural result for any
local theory. It is not C2-specific.**

---

## Attack 10 — Combine: ξ_c/τ_B ≤ 2v_s

The combined claim: ξ_c/(2τ_B) ≤ v_s.

This says: the "inferred substrate speed" c_eff = ξ_c/(2τ_B), computed from
separately measured spatial and temporal scales, is bounded by the acoustic speed.

**Can a conventional phonon model give the same?**

YES. For Cattaneo-Vernotte phonon transport:
- c_ph = phonon group velocity ≤ acoustic group velocity v_s (by definition, since
  the acoustic branch has v_s as the long-wavelength limit)
- ξ_ph = 2c_ph τ_ph
- Therefore ξ_ph/(2τ_ph) = c_ph ≤ v_s

**Identical structure. Standard phonon physics.**

---

## Central Conclusion

**ξ_c/τ_B = 2c is:**

**C. Generic to finite-speed stochastic transport (telegrapher universality class)**
**plus**
**E. Generic to any model with ballistic propagation + relaxation (mean free path relation)**

It is the mean free path relation ξ = v · τ_scatter, which is:
- Kinetic theory of gases (Maxwell, 1860)
- Phonon transport (Peierls, 1929)
- Cattaneo heat equation (Cattaneo, 1948)
- Telegraph noise in signal processing (1950s)
- Any symmetric PRW (Goldstein, 1951)

**The relation is not C2-specific. It is universal to the telegrapher class.**

The factor of 2 is a convention artifact of defining τ_B = 1/(2γ).

The physical invariant — ξ_c · γ = c, or equivalently ξ_c = c/γ —
is the definition of the mean free path. It is a tautology given the PRW parameters.

---

## What Survives (if anything)

The ONLY potentially C2-specific content is:

**The identification c ≤ v_s = a√(K/m) as the UPPER BOUND on c**,
**where v_s is derived from the FPUT lattice parameters a, K, m.**

But Attack 9 shows this is a generic causality bound, not a C2-specific result.

**ξ_c/τ_B = 2c does not survive as G2. It is G1 at best (mathematical identity
of the telegrapher) and arguably G0 (the mean free path relation is not a
mathematical novelty).**
