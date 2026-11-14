# 13_FRGE_TRUNCATION_SPEC
## FRGE Truncation for β_{w₃} and w₃* — Corrected Specification

**Date:** August 2026 (revised)
**Replaces:** previous 13_FRGE_TRUNCATION_SPEC.md
**Corrections applied:**
  (a) Nonredundant 4D operator basis
  (b) S⁴ degeneracy identified — S²×S² required as primary projection background
  (c) Goroff-Sagnotti result correctly scoped
  (d) β_{w₃} framed as FRGE trace projection, not "triangle diagram"

**Status:** Active only if Gate 1 passes (12B_W3_FULL_VARIATION_RESULT.md).

---

## 1. The FRGE

The Wetterinck equation:

    ∂_t Γ_k = (1/2) STr [ (Γ_k^{(2)} + R_k)^{-1} ∂_t R_k ]

where t = ln(k/k₀), Γ_k^{(2)} is the Hessian, R_k is the IR regulator.
The beta function for any coupling cᵢ is obtained by projecting the right-hand
side onto the corresponding operator:

    β_{cᵢ} = projection of (1/2) STr[...] onto ∫√g Oᵢ

The projection is exact within the truncation. It is not a perturbative
Feynman-diagram expansion. Whether the projection onto C³ involves a "triangle
diagram" or not is a consequence of the calculation, not an assumption.

---

## 2. Nonredundant Operator Basis in 4D

In four dimensions the Gauss-Bonnet identity is:

    GB = R_{μνρσ}² − 4 R_{μν}² + R²  =  total derivative

Therefore only two independent 4th-order scalar invariants exist (up to total
derivatives):

    {R², C²}

where C² = R_{μνρσ}² − 2R_{μν}² + (1/3)R² (using the GB identity to eliminate
Ric²). Carrying both R² and Ric² as independent couplings is redundant in 4D.

**Nonredundant truncation basis:**

    Γ_k = ∫ d⁴x √g [
        −(1/16πG_k)(R − 2Λ_k)     [Einstein-Hilbert, 2 couplings: G_k, Λ_k]
        + c₂_k C_{αβγδ}C^{αβγδ}   [quadratic Weyl]
        + w₃_k W₃                  [cubic Weyl — new]
    ]

where W₃ = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ}.

Note: R² could also be included at 4th order. It does not vanish on the
projection backgrounds considered here, so its running could in principle mix
with w₃. For a first determination of w₃*, the EH + C² + W₃ truncation is the
minimal nonredundant starting point.

**Why Ric² is omitted:** By the 4D GB identity, ∫Ric² = ∫[(R²/4) + (C²/2) − GB/4].
The GB term is topological; Ric² is therefore a linear combination of R² and C²
up to a topological term. It is not an independent operator.

---

## 3. The S⁴ Degeneracy Problem

The standard AS background is the 4-sphere S⁴. On S⁴:

    C_{αβγδ}[S⁴] = 0    (S⁴ is conformally flat)

Therefore W₃|_{S⁴} = 0 and more critically:

    δ(√g W₃)/δg^{μν}|_{S⁴} = 0

This means: projecting the FRGE right-hand side onto ∫√g W₃ using an S⁴
background yields zero at the level of the background action. The linear-in-w₃
contribution to β_{w₃} vanishes on S⁴.

The quadratic-in-w₃ term (from expanding the full trace to second order in w₃)
could in principle be nonzero even on S⁴. But this requires working at O(w₃²) in
the fluctuation expansion — it does not directly give the anomalous generation
term (the source term at w₃=0 that drives w₃ away from zero).

**The anomalous generation term** is the piece of β_{w₃} that is independent of
w₃ itself — i.e., the loop contribution to the running of w₃ from the EH and C²
sectors alone. If this term is nonzero, then w₃=0 is not a consistent fixed
point. On S⁴ this term cannot be extracted because the projection background has
zero C³ structure.

**Consequence:** S⁴ is insufficient as the sole projection background for computing
β_{w₃}. This is not a minor technical issue — it affects whether w₃* can be
extracted at all from a purely S⁴ calculation.

---

## 4. Required Projection Background: S²×S²

The product space S²×S² is an Einstein manifold:

    R_{μν} = Λ̄ g_{μν}    with    Λ̄ = 1/r²   (r = radius of each factor)

On S²×S², the Weyl tensor is nonzero:

    C_{αβγδ} ≠ 0

Specifically, S²×S² has nonzero W₃:

    W₃[S²×S²] ≠ 0

This makes S²×S² the natural projection background for the C³ coupling.

**Properties needed:**

| Property | S⁴ | S²×S² |
|----------|-----|--------|
| C[background] | 0 | ≠ 0 |
| W₃[background] | 0 | ≠ 0 |
| Laplacian spectrum known | Yes | Yes (product formula) |
| Heat kernel coefficients | Tabulated | Derivable from S² data |
| Einstein background | Yes | Yes |
| Suitable for FRGE projection onto C³ | NO | YES |

**The projection background must be S²×S² (or another background with nonzero Weyl)
to extract β_{w₃} at linear order in w₃.**

This choice is not merely a technical preference — it is a mathematical requirement
for a non-degenerate projection onto the C³ operator.

---

## 5. Structure of the β_{w₃} Computation on S²×S²

The FRGE trace on S²×S² produces a functional of the background curvature. The
projection onto ∫√g W₃ extracts β_{w₃}.

**Steps:**

1. Expand Γ_k[ḡ+h] to second order in the metric fluctuation h_{μν} around the
   S²×S² background. This gives the Hessian Γ_k^{(2)}.

2. The Hessian has contributions from EH, C², and W₃. On S²×S² the W₃ term
   contributes at linear order in w₃ (since C[background]≠0).

3. Compute the regulated propagator (Γ_k^{(2)} + R_k)^{-1} in the TT and trace
   sectors. This requires the spectrum of the Lichnerowicz operator on S²×S².

4. Contract with ∂_t R_k and take the supertrace.

5. Project the resulting functional onto ∫√g W₃ by identifying the coefficient
   of the W₃ term in the curvature expansion. This gives β_{w₃}.

6. Simultaneously project onto ∫√g C² and ∫(R−2Λ)√g to update the full
   fixed-point system (g*, Λ*, c₂*, w₃*) self-consistently.

**Key difference from S⁴ calculation:** On S²×S² the W₃ background value is
nonzero, so β_{w₃} receives a contribution at O(w₃¹) from the Hessian of the
W₃ term itself. The anomalous generation term (O(w₃⁰)) comes from the EH + C²
Hessian projected onto C³ via the background curvature of S²×S².

---

## 6. The Goroff-Sagnotti Result: Correct Scope

The two-loop divergence of pure gravity in 4D is (Goroff-Sagnotti 1986,
van de Ven 1992):

    Γ_div^{2-loop} = (1/ε) × (209/2880) × (1/(4π)⁴) × ∫√g W₃ + ...

This is a result in perturbative quantum gravity (dimensional regularization,
expansion around flat space).

**What this establishes:**
- W₃ is generated by quantum gravity at two loops.
- The C³ direction in theory space is not protected by any perturbative symmetry.
- The coefficient 209/2880 is a specific nonzero number.

**What this does NOT establish:**
- The value of w₃* at the non-perturbative AS UV fixed point.
- Whether the AS fixed point lies in a regime where perturbation theory is valid.
- Whether β_{w₃}(w₃*=0) = 0 or ≠ 0 at the AS fixed point.

The perturbative beta function and the FRGE beta function are related but not
identical. In particular, the FRGE beta function at the AS fixed point is
evaluated at couplings g* ~ O(1), far from the perturbative regime g→0.

**Correct use of Goroff-Sagnotti:** The result demonstrates that there is no
symmetry reason for w₃ to remain zero. It provides no information about the
sign or magnitude of w₃*.

**Incorrect use (corrected from 13_FRGE_TRUNCATION_SPEC.md):** The previous
version stated this result "provides motivation that w₃*≠0 is the more natural
outcome." That language was too strong. The defensible statement is:

    The perturbative result demonstrates that W₃ is radiatively generated
    and that no symmetry forces w₃=0. It does not determine w₃*.

---

## 7. Fixed-Point System

Including W₃ in the truncation, the fixed-point equations are:

    β_G(G*, Λ*, c₂*, w₃*) = 0
    β_Λ(G*, Λ*, c₂*, w₃*) = 0
    β_{c₂}(G*, Λ*, c₂*, w₃*) = 0
    β_{w₃}(G*, Λ*, c₂*, w₃*) = 0

These must be solved simultaneously. The values (G*, Λ*, c₂*) from the EH+C²
truncation (Ohta-Percacci 2016) are NOT automatically valid inputs — the inclusion
of W₃ shifts the fixed point. They may be used as starting approximations and
cross-checks, not as exact inputs.

**Possible outcomes:**

(a) w₃* = 0 is the only solution: W₃ is an irrelevant direction at the fixed
    point. The mechanism fails.

(b) w₃* ≠ 0 with a unique real solution: W₃ is a relevant or marginal direction.
    Gate 2 passes; proceed to Gate 3.

(c) Multiple real solutions exist: truncation dependence must be assessed. Report
    as scheme-dependent until regulator checks are performed.

(d) No real solution: fixed point structure changes qualitatively with W₃ included.
    Report as UNRESOLVED.

---

## 8. Required Checks

The computation is not complete without:

1. **Two background checks:** S²×S² primary + at least one other (e.g., S⁴ for
   the c₂* and G* sector, or a Bianchi I background for the W₃ sector).

2. **Two regulator choices:** e.g., optimized (Litim) and exponential cutoffs.
   If the sign of w₃* changes between regulators, the result is scheme-dependent
   and must be reported as UNRESOLVED.

3. **Gauge check:** Landau gauge (α→0) and one other choice. Gauge dependence
   of physical observables should vanish; if w₃* is strongly gauge-dependent,
   this is a warning sign.

4. **Operator completeness:** Verify that no operator at the same order (e.g.,
   R·C², ∇²C², or other 6th-order terms) has been omitted that could mix with
   W₃ under the RG and alter β_{w₃}.

---

*Document status: FRGE TRUNCATION SPEC — CORRECTED*
*Key corrections: nonredundant basis; S⁴ degeneracy identified; S²×S² required;
Goroff-Sagnotti scoped correctly; β_{w₃} as FRGE projection, not diagram.*
*This is a specification. The computation remains to be performed.*
*Date: August 2026*
