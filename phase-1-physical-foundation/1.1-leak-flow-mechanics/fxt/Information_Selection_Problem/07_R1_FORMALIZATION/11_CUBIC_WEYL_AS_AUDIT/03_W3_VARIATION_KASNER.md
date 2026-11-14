# 03_W3_VARIATION_KASNER
## Analytic Computation of δW₃/δg^{μν} on Vacuum Kasner

**Date:** August 2026

---

## Setup

**Operator:** W₃ = C_{αβγδ} C^{αβ}_{\ \ εζ} C^{γδεζ}

(Using index-raising with the metric g^{μν}. This is the unique parity-even cubic Weyl scalar in 4D.)

**Goal:** Compute δ(√g W₃)/δg^{μν} evaluated on the vacuum Kasner metric.

**Kasner metric:** ds² = −dt² + t^{2p₁}dx² + t^{2p₂}dy² + t^{2p₃}dz²
with p₁ + p₂ + p₃ = 1 and p₁² + p₂² + p₃² = 1.
Vacuum: R_{μν} = 0, R = 0 (exact).

---

## General Variation Formula

The variation of an integral of a cubic curvature scalar Q = I₁(C) = C_{αβγδ}C^{αβ}_{\ εζ}C^{γδεζ} is:

  δ(∫√g Q d⁴x)/δg^{μν} = √g P_{μν}

where P_{μν} is the Euler-Lagrange expression. For cubic Weyl invariants, this is a 6th-order PDE in the metric.

**General form (from Oliva-Ray 2010, Bueno-Cano 2016):**

For the cubic Lagrangian L = w₃ C_{α₁β₁γ₁δ₁} C^{α₁β₁}_{\ \ α₂β₂} C^{γ₁δ₁α₂β₂}, the variation produces:

  P_{μν} = −(1/2) g_{μν} W₃
           + 3 C_{μ}^{\ αβγ} C_{αβ}^{\ \ δε} C_{νγδε}    (schematic — 3 terms from index symmetry)
           + (total derivative terms from integration by parts involving ∇²C and ∇⁴g)

The full expression includes:
- Algebraic terms: products of three Weyl tensors contracted with the metric variation
- Derivative terms: □(C²) contributions, ∇∇(CC) contributions

The complete variation is known in principle (e.g., from computer algebra systems using Cadabra or xAct), but is lengthy to write explicitly. The key question for Kasner is whether any of these terms vanish by the Kasner symmetries.

---

## Evaluation on Kasner: Algebraic Terms

The algebraic terms in P_{μν} are schematically:

  P_{μν}^{alg} = −(1/2)g_{μν} W₃ + 3 C_{μ}^{\ αβγ} C_{αβ}^{\ \ δε} C_{νγδε} + (permutations)

**On vacuum Kasner:**

W₃|_{Kasner} = C_{αβγδ}C^{αβ}_{\ \ εζ}C^{γδεζ}|_{Kasner}

The Kasner Weyl tensor in orthonormal frame {e^0 = dt, e^1 = t^{p₁}dx, e^2 = t^{p₂}dy, e^3 = t^{p₃}dz}:

  C_{0i0j} = K_{ij} − (K/3)h_{ij}   (electric Weyl in terms of extrinsic curvature for vacuum)

For Kasner: K_{ij} = diag(p₁/t, p₂/t, p₃/t). The electric Weyl components are:

  E_{ij} = diag((p₁ − p̄)/t, (p₂ − p̄)/t, (p₃ − p̄)/t)   where p̄ = (p₁+p₂+p₃)/3 = 1/3

The magnetic Weyl tensor B_{ij} = 0 for Kasner (Kasner has no rotation/twist — it is a purely electric Weyl spacetime).

**W₃ for purely electric Weyl:**

  W₃ = I₁ = C_{αβγδ}C^{αβ}_{\ εζ}C^{γδεζ}

For a purely electric Weyl tensor (B = 0):

  I₁ ~ Tr(E³)   (schematically)

  W₃|_{Kasner} = 8 Tr(E³)/t⁶   where E_{ij} = diag(p₁−1/3, p₂−1/3, p₃−1/3)/t

  = 8(p₁−1/3)³ + (p₂−1/3)³ + (p₃−1/3)³) / t⁶

Using the Kasner constraint: p₁+p₂+p₃=1 and Σp_i²=1, we can compute that for generic Kasner (not isotropic):

  W₃|_{Kasner} ≠ 0   for generic anisotropy (p_i not all equal to 1/3)

For the maximally anisotropic case (p₁=1, p₂=p₃=0):

  W₃|_{Kasner,max} = 8[(1−1/3)³ + (0−1/3)³ + (0−1/3)³] / t⁶
                   = 8[(2/3)³ − 2(1/3)³] / t⁶
                   = 8[8/27 − 2/27] / t⁶
                   = 8 × 6/27 / t⁶ = 16/(9t⁶)

So W₃ ≠ 0 on Kasner. (This was already established in the operator audit.)

**Now: are the algebraic terms in P_{μν} nonzero?**

  P_{μν}^{alg} ~ −(1/2)g_{μν} W₃ + (C·C·C terms contracted on one index)

The (C·C·C) terms: for Kasner with purely electric Weyl E_{ij} and B_{ij}=0:

  C_{μ}^{\ αβγ} C_{αβ}^{\ \ δε} C_{νγδε}|_{Kasner}

In the electric-magnetic decomposition, the triple contraction with one free index pair (μν) produces:

  (C·C·C)_{μν} ~ E_{μα}E^{α}_{\ β}E^{β}_{\ ν}   (schematic for purely electric)

This is Tr(E³) × (matrix structure) — which is nonzero for generic Kasner with E_{ij} nonzero and non-degenerate.

Therefore:

  P_{μν}^{alg}|_{Kasner} ~ (E_{μα}E^α_{\ β}E^β_{\ ν} − proportional to g_{μν} W₃)

Both terms are nonzero on Kasner. The combination may or may not vanish, depending on whether the Kasner geometry satisfies a specific algebraic identity.

**Key question: Can P_{μν}^{alg}|_{Kasner} = 0?**

For Kasner, E_{ij} is a diagonal traceless matrix with eigenvalues (p₁−1/3, p₂−1/3, p₃−1/3)/t. The condition P_{μν}^{alg} = 0 would require:

  E_{μα}E^α_{\ β}E^β_{\ ν} = (1/4)g_{μν} W₃ / something

This is a specific algebraic condition on the Kasner parameters. It is NOT automatically satisfied by any diagonal traceless matrix — it would require a specific relationship between the p_i values. For generic Kasner, this is not satisfied.

**The algebraic part of δW₃/δg is generically nonzero on Kasner.**

---

## Evaluation on Kasner: Derivative Terms

Beyond the algebraic terms, δW₃/δg contains derivative terms (from varying the metric in the covariant derivatives implicit in the definition of the Weyl tensor via the Riemann tensor):

  P_{μν}^{der} ~ ∇_α∇_β (C^{αμβν} W_C + ...) + higher-order

where W_C denotes Weyl-dependent terms from varying the cubic.

**On Kasner:**

These derivative terms involve ∇²(C²) and similar. On Kasner, the Weyl tensor has explicit time dependence: C ~ 1/t² (schematically). Its covariant derivatives are nonzero:

  ∇_t C_{0i0j} ~ ∂_t C_{0i0j} ~ ∂_t(E_{ij}) ~ 1/t² + p_i/t² ~ O(1/t²)

The derivative terms in P_{μν}^{der} are therefore nonzero on Kasner (they involve spatial or time derivatives of the Weyl tensor, which are not zero for the t-dependent Kasner solution).

**Preliminary conclusion:** Both the algebraic and derivative parts of δW₃/δg are nonzero on Kasner.

---

## Is δW₃/δg^{μν}|_{Kasner} Nonzero?

**Based on the analysis above:**

The variation δW₃/δg^{μν} evaluated on vacuum Kasner is **generically nonzero** for the following reasons:

1. The algebraic part involves products E·E·E contracted to a 2-tensor, which is nonzero for generic anisotropic Kasner (B=0, E≠0, E³ ≠ 0 component-wise).

2. The derivative part involves covariant derivatives of the time-dependent Weyl tensor, which are nonzero.

3. No Kasner symmetry (Ricci-flatness, conformal flatness of spatial slices, uniform K) eliminates these terms — they depend on the Weyl tensor itself, not on Ricci.

**CRITICAL CAVEAT:** This is a structural argument based on the component analysis. A complete rigorous calculation requires:
- Full explicit computation of all terms in δW₃/δg
- Substitution of the specific Kasner metric
- Verification that no cancellation occurs between algebraic and derivative terms

The structural argument is strong (no symmetry forces cancellation) but does not constitute a theorem. The explicit calculation has not been performed.

---

## What Would Force δW₃/δg|_{Kasner} = 0?

For the variation to vanish on Kasner, there would need to be:

1. A specific algebraic identity satisfied by all diagonal traceless matrices E (the electric Weyl of Kasner) — this would need to be proven. For generic diagonal traceless matrices, no such identity is known.

2. A specific cancellation between algebraic and derivative terms — this would require both to have opposite signs and equal magnitudes, which seems unlikely without a symmetry argument.

3. A field redefinition that moves the C³ contribution into a total derivative — possible in principle but no known field redefinition achieves this for the cubic Weyl in 4D.

None of these three escape routes is established. The working conclusion is that δW₃/δg|_{Kasner} ≠ 0 generically.

---

## Summary

| Question | Answer |
|----------|--------|
| W₃|_{Kasner} = 0? | NO — nonzero for generic anisotropic Kasner |
| δW₃/δg algebraic terms nonzero on Kasner? | YES — involve E³ products |
| δW₃/δg derivative terms nonzero on Kasner? | YES — involve ∇C ≠ 0 |
| Any symmetry forces δW₃/δg|_{Kasner} = 0? | NO known symmetry |
| Rigorous theorem: δW₃/δg|_{Kasner} ≠ 0? | STRUCTURAL ARGUMENT ONLY — explicit calculation not performed |

**Working conclusion:** δW₃/δg^{μν}|_{Kasner} ≠ 0 generically. If w₃* ≠ 0, Kasner likely fails the full saddle-point equation.

**The decisive remaining step:** Full explicit computation of δW₃/δg in closed form and substitution on Kasner, with verification that no cancellation occurs. This is a specific tensor computation feasible with computer algebra.

---

*Document status: W₃ VARIATION CALCULATION COMPLETE (structural)*
*δW₃/δg|_{Kasner} generically nonzero — no symmetry forces cancellation.*
*Full explicit computation (computer algebra) required for certainty.*
*Date: August 2026*
