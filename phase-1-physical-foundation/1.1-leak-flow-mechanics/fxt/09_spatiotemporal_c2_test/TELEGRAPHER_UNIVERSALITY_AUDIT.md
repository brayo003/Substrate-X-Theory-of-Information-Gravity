# TELEGRAPHER UNIVERSALITY AUDIT
## Is ξ/τ = 2c Generic to Telegrapher Dynamics?

**Date:** 2026-08-21

---

## The Generic Symmetric Telegrapher

For ANY symmetric PRW with speed v and flip rate γ:

    ∂ₜn⁺ + v∂ₓn⁺ = −γ(n⁺ − n⁻)
    ∂ₜn⁻ − v∂ₓn⁻ = +γ(n⁺ − n⁻)

Combining: τ∂ₜₜs + ∂ₜs = v²τ∂ₓₓs,   τ = 1/(2γ)

This telegrapher equation has:

| Quantity | Expression | Origin |
|----------|-----------|--------|
| Propagation speed | v | Input parameter |
| Flip rate | γ | Input parameter |
| Temporal correlation time | τ = 1/(2γ) | Definition |
| Spatial correlation length | ξ = v/γ | From static Green's function |
| Ratio ξ/τ | 2v | Algebraic consequence |

**The ratio ξ/τ = 2v holds for ANY symmetric telegrapher, with ANY v and ANY γ.**

It is not a property of C2. It is a property of the telegrapher equation class.

---

## What Breaks the Relation

The relation ξ·γ = v fails if any of the following hold:

1. **Asymmetric switching:** γ₊ ≠ γ₋. Then the spatial and temporal decay
   rates decouple. The mean free path relation no longer holds.

2. **Mass term (Klein-Gordon type):** Adding ω₀²s to the telegrapher gives
   ξ = v/√(γ² + ω₀²) while τ is still 1/(2γ). The ratio ξ/τ = 2v/√(1 + (ω₀/γ)²) < 2v.

3. **Non-constant propagation speed:** If v = v(x,t), the Green's function
   is no longer translation-invariant and ξ is not well-defined globally.

4. **Non-exponential switching distribution:** If flip times are not Poisson
   (non-Markovian PRW), the temporal correlation is no longer a simple exponential
   and τ is not 1/(2γ).

**C2 uses the symmetric, massless, Markovian telegrapher — the special case
where the relation ξ·γ = v is exact. Any other telegrapher variant breaks it.**

---

## Verdict

**ξ/τ = 2v is generic to the symmetric massless Markovian telegrapher class.**

C2 is one member of this class. The relation is not C2-specific.
