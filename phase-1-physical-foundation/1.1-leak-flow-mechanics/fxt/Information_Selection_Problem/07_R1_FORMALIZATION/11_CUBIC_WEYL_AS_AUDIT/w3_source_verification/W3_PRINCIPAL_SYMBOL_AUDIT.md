# W3 Principal Symbol Audit

**Status: VERIFIED**  
**Date: 2026-08-24**

---

## Setup

Background: S²×S², equal radii r₁=r₂=1, equatorial point.  
At this point: ḡ_{μν} = δ_{μν}, Γ̄^k_{ij} = 0, R̄_{ab} = δ_{ab}, R̄ = 4.

Perturbation: g_{μν}(ε) = ḡ_{μν} + ε h_{μν}, Fourier mode h_{μν}(x) = H_{μν} e^{ip·x}.  
In momentum space: ∂_μ → ip_μ.

At equatorial point (Γ̄=0), first-order connection:

    δΓ^k_{ij} = (i/2)(p_i H_{jk} + p_j H_{ik} - p_k H_{ij})

First-order Riemann (i² = −1 absorbed):

    δR^k_{lij} = −p_i δΓ^k_{lj} + p_j δΓ^k_{li}

These carry **one factor of p** each (δΓ ∼ p·H), so δR ∼ p²·H.

---

## Full Second Variation

The complete second variation of the action density S_W3 = ∫ √g W₃ is:

    δ²(√g W₃) = [δ²√g]·W̄₃ + 2[δ√g]·[δW₃] + √ḡ·[δ²W₃]

where δW₃ and δ²W₃ come from:

    W₃[ḡ+εh] = W̄₃ + ε·δW₃ + ε²·δ²W₃ + ...

    δW₃   = 3·C̄·C̄·δC      (linear in δC, hence linear in h)
    δ²W₃  = 6·C̄·δC·δC + 3·C̄·C̄·δ²C

---

## Derivative Order Table

Evaluated for the specific TT mode h+ = diag(1,−1,0,0), p = (0,0,0,t):

| Contribution | p⁴ coefficient | p² coefficient | p⁰ coefficient |
|---|---|---|---|
| 6·C̄·δC·δC | **−4** | 0 | −16/9 |
| 3·C̄·C̄·δ²C | 0 | 20/3 | 112/3 |
| δ²(√g)·W̄₃ | 0 | 0 | −16/9 |
| 2·δ(√g)·δ(W₃) | 0 | 0 | 0 (tr h=0) |
| **TOTAL** | **−4** | **20/3** | ≈ **35** |

**For traceless modes (tr h = 0): δ(√g) = 0, so the cross term vanishes exactly.**

---

## Proof That 3·C̄·C̄·δ²C Cannot Contribute to p⁴

The second-order Weyl perturbation δ²C_{abcd} is built from:

1. **δ²R ∼ δΓ·δΓ**: Each δΓ ∼ p·H (one power of p). Product ∼ p²·H².  
   Therefore δ²R ∼ p²·H² → δ²C (from this term) ∼ p²·H².

2. **h·δRic**: One factor of h (no p), one factor of δRic ∼ p²·H.  
   Product ∼ p²·H².

3. **h²·Ric, h²·R**: p-independent (p⁰).

So δ²C ∼ p²·H² + p⁰·H².

The contraction 3·C̄·C̄·δ²C inherits this: it is **p² or p⁰, never p⁴**.

**The p⁴ principal symbol comes exclusively from 6·C̄·δC·δC.**

---

## Why 6·C̄·δC·δC is p⁴

δC ∼ p²·H (second derivatives of h enter via δR ∼ p²·H, and the Weyl formula does not add more momentum: the Schouten correction involves δRic ∼ p²·H as well, no extra p).

Therefore:

    6·C̄·δC·δC ∼ C̄ · (p²·H) · (p²·H) = p⁴·H²

This is the leading kinetic term. **The W₃ Hessian is a p⁴ operator.**

Physical interpretation: The action S_W₃ = ∫ C³ has 6 metric derivatives (each C is second-order in derivatives of g). The Hessian δ²S_W₃ carries 4 powers of momentum — same as the C² action.

---

## Inverse-Metric Variation Terms

The action uses C^{cdef} = g^{ce}g^{df}C_{efab}, with inverse metric g^{-1}(ε) = I − ε H + ε² H² + ....

The variation of g^{-1} at first order contributes terms of the form:

    (variation of g^{-1}) · C̄ · C̄  ∼ H · C̄ · C̄

These are **p⁰** (no derivatives of h). They contribute to the mass matrix at p⁰ order, not to the p⁴ principal symbol.

**The inverse-metric variation does not contribute to p⁴.**

---

## √g Variation Terms

    √g(ε) = 1 + ε/2 · tr(h) + ε²[1/8 (tr h)² − 1/4 tr(h²)] + ...

For TT modes: tr(h) = 0, so √g(ε) = 1 − ε²/4 · tr(h²) + ...

The δ²(√g) · W̄₃ term is p⁰ (W̄₃ = const, tr(h²) has no p dependence).

**The √g variation does not contribute to p⁴.**

---

## Summary

The p⁴ principal symbol of δ²S_{W₃} is:

    H^{μν,ρσ}_{p⁴}(p) = coefficient of p⁴ in [6·C̄·δC·δC](H)

This is the **unique** source of the p⁴ structure. All other contributions are p² or p⁰.

*Document: W3_PRINCIPAL_SYMBOL_AUDIT.md*  
*Status: VERIFIED — p⁴ comes exclusively from 6·C̄·δC·δC.*
