# INVARIANT AUDIT
## The Convention-Independent Physical Quantity and Factor-of-Two Analysis

**Date:** 2026-08-21

---

## The Factor of Two — Complete Trace

The relation ξ_c/τ_B = 2c arises from two definitions:

    ξ_c ≡ c/γ    [mass gap of the static Green's function — physically meaningful]
    τ_B ≡ 1/(2γ) [HALF the inverse damping rate of J — a CONVENTION]

Therefore: ξ_c/τ_B = (c/γ)·(2γ) = 2c.

The factor of 2 in τ_B = 1/(2γ) traces to how the J-equation damps:

    ∂ₜJ + c²∂ₓs = −2γJ

The damping rate of J is 2γ (not γ). This 2γ comes from BOTH n⁺ and n⁻ flipping
simultaneously at rate γ, each contributing γ to the J = c(n⁺−n⁻) decay.

**The physical content is:** J decays at rate 2γ. If τ_B is defined as the e-folding
time of J (i.e., τ_B = 1/(2γ)), then ξ_c = 2cτ_B.

**Alternative conventions produce different numerical factors:**

| Definition of τ | τ value | ξ/τ ratio |
|----------------|---------|----------|
| τ = 1/(2γ)  (C2 convention — e-folding of J) | 1/(2γ) | 2c |
| τ = 1/γ  (natural scattering time) | 1/γ | c |
| τ = ∫₀^∞ C_JJ(t)/C_JJ(0) dt = 1/(2γ) | 1/(2γ) | 2c |
| τ = 2/β where β=1/τ in ∂ₜₜs+β∂ₜs=c²∂ₓₓs | 2/(2γ)=1/γ | c |

**The factor of 2 is convention-dependent. It is not a physical prediction.**

---

## The Convention-Free Invariant

The physical content, stripped of all convention, is:

    ξ_c = c / γ    [mean free path = speed / scattering rate]

or equivalently:

    ξ_c · γ = c    [dimensionless: (length)(rate) = (speed)]

This is the mean free path relation. It is a TAUTOLOGY once c and γ are defined
as the walker speed and switching rate respectively. It says:

> "The distance a particle travels before scattering equals its speed divided
>  by its scattering rate."

This has zero predictive content beyond the definitions of c and γ.

---

## What the Upper Bound c ≤ v_s Adds

The relation ξ_c · γ = c is a tautology. But:

    c ≤ v_s = a√(K/m)

is NOT a tautology — it says the walker speed is bounded by the acoustic phonon speed.
This is derived from C3 (admissibility) + FPUT dispersion.

Combined: ξ_c · γ ≤ v_s = a√(K/m)

This says: the mean free path times the scattering rate is bounded by a quantity
derivable from the FPUT lattice parameters. That IS substrate-specific — v_s is
determined by a, K, m — but it is equivalent to the generic Lieb-Robinson / causality
statement "coarse-grained dynamics cannot exceed microscopic propagation speed."

---

## Final Verdict on the Invariant

The relation ξ_c/τ_B = 2c (or ξ_c·γ = c) is:

- A tautology in PRW/telegrapher models
- A known result in kinetic theory (mean free path relation)
- Present in phonon transport without any C2
- Convention-dependent (the factor 2 changes with τ definition)

The only non-tautological content is the UPPER BOUND c ≤ v_s, which is a
generic causality bound for the FPUT lattice, equivalent to:

    "Coarse-grained excitations cannot propagate faster than the acoustic phonon speed."

This is substrate-specific to FPUT but is not specific to C2 — it is a property
of any coarse-graining of the harmonic FPUT chain.
