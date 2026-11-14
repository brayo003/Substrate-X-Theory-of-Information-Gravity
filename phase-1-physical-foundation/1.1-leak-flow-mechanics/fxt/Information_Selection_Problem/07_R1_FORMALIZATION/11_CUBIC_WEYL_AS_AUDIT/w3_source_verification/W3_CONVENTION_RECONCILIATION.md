# W3 Convention Reconciliation

**Status: RESOLVED**  
**Date: 2026-08-24**

---

## The Discrepancy

Project document `42_BACKGROUND_S2XS2_DEFINITION.md` states:

    W₃[S²×S²] = 128/27   (for equal radii r₁=r₂=1, R=4)

Our explicit computation gives:

    W₃[S²×S²] = 32/9

Ratio: 128/27 ÷ 32/9 = **4/3**

---

## Index-Level Audit

### Three independent contractions computed

All contractions use the fully-lowered Weyl tensor C_{abcd} with g=I at the equatorial point.

**V1** (used in this project's action S_W3 = ∫√g C_{abcd}C^{cdef}C_{ef}^{ab}):

    V1 = C_{abcd} C_{cdef} C_{efab}  (sum over all a,b,c,d,e,f ∈ {0,1,2,3})

**V2** (from `01_W3_OPERATOR_AUDIT.md`: I₁ = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ}):

    V2 = C_{abcd} C_{abef} C_{cdef}  (at g=I, raising indices with δ^{ab} is trivial)

**V3** (from `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`: C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ}):

    V3 = C_{abcd} C_{abef} C_{cdef}  (identical to V2)

**Result**: V1 = V2 = V3 = **32/9** (exact, rational arithmetic, verified).

### Background Weyl tensor

Computed from first principles using Wald GR eq. 3.2.28:

    C_{abcd} = R_{abcd}
             - (1/2)(g_{ac}R_{bd} - g_{ad}R_{bc} - g_{bc}R_{ad} + g_{bd}R_{ac})
             + (1/6)R(g_{ac}g_{bd} - g_{ad}g_{bc})

Inputs at equatorial point of S²×S² (g=I):
- R_{0101} = R_{2323} = 1, all other independent Riemann components zero
- R_{ab} = δ_{ab}  (Einstein space with Λ=1)
- R = 4

Non-zero background Weyl components:
- C̄_{0101} = 2/3  (and by antisymmetry)
- C̄_{0202} = C̄_{0303} = C̄_{1212} = C̄_{1313} = −1/3
- C̄_{2323} = 2/3

### Verification of algebraic identities

All checked by explicit 4-index enumeration:

| Identity | Status |
|----------|--------|
| C_{abcd} = −C_{bacd} | ✓ VERIFIED (0 violations) |
| C_{abcd} = −C_{abdc} | ✓ VERIFIED (0 violations) |
| C_{abcd} = C_{cdab}  | ✓ VERIFIED (0 violations) |
| g^{ac}C_{abcd} = 0 (traceless) | ✓ VERIFIED |
| C_{a[bcd]} = 0 (Bianchi) | ✓ VERIFIED (0 violations) |
| Matches Wald formula | ✓ VERIFIED (max error = 0) |

---

## Diagnosis of 128/27

The value 128/27 appears in project documents (`42_BACKGROUND_S2XS2_DEFINITION.md`, `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`, `42_GATE2_FINAL.md`) cited as "from literature" with no explicit derivation.

**What was checked to produce 128/27:**

| Variant | W3 value |
|---------|----------|
| C_{abcd}C_{cdef}C_{efab}   (correct, Wald) | 32/9 |
| 3D Weyl formula (wrong n=3 coefficients)   | −80/9 |
| Traceless Riemann (no R·g term)            | −32 |
| C' = 2C normalization                      | 256/9 |
| Any normalization giving 128/27             | **none found** |

**Conclusion**: The value 128/27 does not correspond to any standard index contraction of the Weyl tensor on S²×S². It is an error propagated without derivation through project documents. The correct first-principles value is **W₃ = 32/9**.

---

## Mapping Between Definitions

The project's canonical definition (from `01_W3_OPERATOR_AUDIT.md` and `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`) is:

    W₃ = C_{αβγδ} C^{αβ}_{εζ} C^{γδεζ}

This equals, at g=I, the explicit contraction:

    W₃ = Σ_{a,b,c,d,e,f} C_{abcd} C_{abef} C_{cdef}

Our computation directly evaluates this sum and finds **W₃ = 32/9**.

The action term in the FRGE truncation is:

    S_{W₃} = w₃ ∫ d⁴x √g · C_{abcd} C^{αβ}_{εζ} C^{γδεζ}

with background value C̄_{abcd}C̄^{αβ}_{εζ}C̄^{γδεζ} = **32/9**.

The Hessian is computed from this definition throughout the audit.

---

## Impact on Subsequent Calculations

Any project calculation that used W₃ = 128/27 as the background value was using
an incorrect input. The correct value is 32/9 = (3/4) × (128/27).

This affects:
- Any formula that expressed results as multiples of W₃_bar
- Any "background ratio" R · C²/W₃ or similar

It does NOT affect the Hessian computation if it was computed independently from first principles (as this audit does). The Hessian depends on the Weyl tensor components, not on the scalar W₃ value.

---

*Document: W3_CONVENTION_RECONCILIATION.md*  
*Status: RESOLVED — 128/27 is an error. Correct value: 32/9.*
