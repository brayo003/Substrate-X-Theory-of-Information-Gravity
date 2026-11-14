# 41_W3_HESSIAN_CONVENTIONS_AUDIT
## Complete Convention Audit for W₃ Hessian Calculation

**Date:** August 2026
**Purpose:** Establish all conventions for actual tensor-level quadratic Hessian calculation

---

## 1. W₃ DEFINITION

**Exact definition used by project:**
```
W₃ = C_{αβγδ} C^{αβ}_{\ \ εζ} C^{γδεζ}
```

**Equivalent forms in project documentation:**
- `C_{μνρσ} C^{νμαβ} C^{σρ}_{αβ}` (used in recent work)
- `C_{αβ}^{\ \ γδ} C_{γδ}^{\ \ εζ} C_{εζ}^{\ \ αβ}` (from 01_W3_OPERATOR_AUDIT.md)

**Operator independence:** VERIFIED - W₃ is independent in 4D basis (01_W3_OPERATOR_AUDIT.md)

**Normalization:** No additional normalization factor - W₃ is defined as the bare cubic Weyl contraction

---

## 2. η_W3 DEFINITION

**Definition from 32_W3_ANOMALOUS_DIMENSION.md:**
```
η_{w̃₃} = (1/w̃₃) × (loop corrections proportional to w̃₃)
```

**Connection to Hessian:**
```
η_{w̃₃} is defined as the coefficient of w̃₃ in β_{w₃} divided by w̃₃
```

**FRGE specification from 13_FRGE_TRUNCATION_SPEC.md:**
```
β_{cᵢ} = projection of (1/2) STr[ (Γ_k^{(2)} + R_k)^{-1} ∂_t R_k ] onto ∫√g Oᵢ
```

**Physical interpretation:** η_W3 is the anomalous dimension of the W₃ coupling, extracted from the kinetic term coefficient in the W₃ Hessian.

---

## 3. BACKGROUND CONVENTION

**Required background:** S²(r₁) × S²(r₂) (from 13_FRGE_TRUNCATION_SPEC.md)

**Reasoning:**
- S⁴ is conformally flat: C[S⁴] = 0, W₃[S⁴] = 0
- S²×S² has C ≠ 0 and W₃ ≠ 0 (non-degenerate projection)
- Mathematical requirement, not technical preference

**Background metric structure (from 13_FRGE_TRUNCATION_SPEC.md):**
```
R_{μν} = Λ̄ g_{μν} with Λ̄ = 1/r² (r = radius of each factor)
```

**Einstein background property:** S²×S² is an Einstein manifold

**Background values (from 42_GATE2_FINAL.md):**
```
Three-background rank-3 system:

| Background | W₃ | R·C² | R³ |
|------------|-----|------|-----|
| S⁴ (R=12) | 0 | 0 | 1728 |
| S²×S² equal (R=4) | 128/27 | 16/3 | 64 |
| S²×S² unequal (R=6) | 28 | 12 | 216 |
```

**Status:** EXACT BACKGROUND METRIC NOT YET DEFINED IN DETAIL - needs explicit component definition

---

## 4. FLUCTUATION CONVENTION

**TT mode decomposition (from 42_GATE2_FINAL.md):**
```
4D TT graviton on S²(r₁)×S²(r₂) decomposes as:

(a) h_{ab}: TT on S²(r₁), scalar on S²(r₂)
    - Weyl eigenvalue: c₁ = a − R/12 = (5a−b)/6
    - Count: 2 modes per representation
    - Couples to Weyl → contributes to W₃

(b) h_{AB}: scalar on S²(r₁), TT on S²(r₂)
    - Weyl eigenvalue: c₂ = b − R/12 = (5b−a)/6
    - Count: 2 modes
    - Couples to Weyl → contributes to W₃

(c) h_{aA}: vector×vector
    - C_{aAbB} = 0, no Weyl coupling
    - Excluded from N_eff counting
```

**N_eff = 4 VERIFIED (sector counting)**

**Fluctuation parametrization:**
```
g_{ab} = ḡ_{ab} + h_{ab}
```

**Status:** Standard fluctuation convention, but S²×S² metric components need explicit definition

---

## 5. TT/PROJECTOR CONVENTIONS

**From 42_GATE2_FINAL.md:**
- TT conditions used for mode counting
- Projector coefficients used for N_eff = 4 calculation
- Explicit TT projector algebra not yet defined

**Status:** TT sector identified, but explicit projector operator not yet constructed

---

## 6. α₂ = 8 DERIVATION

**From 45_ALPHA2_TENSOR_VERIFICATION.md:**
- α₂ = 8 derived from literature + TensorAtlas + manual derivation
- Source: C² kinetic term coefficient
- Verification: Triangulation of multiple methods

**Status:** VERIFIED - can be used as cross-check but not as substitute for W₃ Hessian

---

## 7. EXISTING W3 VARIATION WORK

**From 12_W3_VARIATION_EXPLICIT.md:**
- Full W₃ variation structure derived
- Decomposition: δ²W₃ = 3·C·C·δ²C + 6·C·δC·δC
- Analytical framework established

**Status:** Framework exists, but tensor-level calculation not completed

---

## 8. EXISTING CADABRA2 FILES

**From recent work:**
- Cadabra2 successfully installed at /tmp/cadabra2
- δR calculation verified: `δR = ∂(δΓ) + δΓ·Γ + Γ·δΓ`
- Files: /tmp/step1_delta_r.cnb, /tmp/test_riemann_corrected.cnb

**Status:** Cadabra2 functional for tensor variations, but full W₃ Hessian not yet computed

---

## 9. A_W3 CALCULATION

**From 46_AW3_INDEPENDENT_VERIFICATION.md:**
- A_W3 formula derived from first principles
- Numerical values: A_W3(Litim) = 12.22, A_W3(Exp) ≈ 6.26
- Method: FRGE trace reconstruction with α₂ = 8, N_eff = 4

**Status:** VERIFIED - A_W3 ≠ 0 under project assumptions

---

## 10. REGULATOR CONVENTIONS

**From 13_FRGE_TRUNCATION_SPEC.md:**
- Litim regulator used for numerical calculations
- Exponential regulator mentioned for comparison
- Exact regulator functional form not yet specified

**Status:** Regulator choice defined, but explicit functional form needed for full calculation

---

## 11. NORMALIZATION CONVENTIONS

**From 42_GATE2_FINAL.md:**
- Ghost contribution = 0 (verified)
- Projection cancellation (EH sector) = 0 (verified)
- Trace normalization via N_eff = 4 (verified)

**Status:** Normalization conventions established

---

## 12. CRITICAL GAPS IDENTIFIED

**Missing explicit definitions:**
1. **S²×S² metric components** - exact coordinate form, radii, inverse metric
2. **Christoffel symbols on S²×S²** - explicit calculation
3. **Riemann tensor on S²×S²** - explicit components
4. **Weyl tensor on S²×S²** - explicit components
5. **W₃ on S²×S²** - explicit value
6. **TT projector operator** - explicit momentum-space form
7. **Fluctuation metric** - explicit h_{ab} components on S²×S²
8. **δΓ in terms of δg** - explicit tensor expression
9. **δ²Γ in terms of δg** - explicit tensor expression
10. **Quadratic action structure** - explicit δ²(√g W₃)

**These must be computed explicitly before η_W3 can be extracted.**

---

## 13. EXISTING CANDIDATE VALUES (REJECTED)

**Identity estimate:**
- η_W3 = 0.050661
- Method: Weyl identity coefficient → kinetic coefficient
- Status: REJECTED - algebraic identity ≠ kinetic operator

**Candidate from scalar chain:**
- η_W3 = 0.236416
- Method: Scalar coefficient multiplication from δR chain
- Status: REJECTED - tensor structure not retained, TT projection not performed

**Current status:** η_W3 = NOT COMPUTED

---

## 14. REQUIRED CALCULATION SEQUENCE

Following the specification:

1. **Define S²×S² background explicitly** (coordinates, metric, inverse metric, curvature)
2. **Define fluctuation h_{ab} explicitly** on this background
3. **Compute δΓ, δ²Γ explicitly** in terms of δg
4. **Compute δR, δ²R explicitly** using Cadabra2
5. **Compute δC, δ²C explicitly** from definition
6. **Expand √g W₃ to O(h²) explicitly**
7. **Construct Hessian H^{ab,cd} explicitly**
8. **Define TT projector explicitly**
9. **Fourier transform to momentum space**
10. **Project Hessian onto TT sector**
11. **Extract K_W3 coefficient explicitly**
12. **Compute η_W3 from K_W3 using project definition**

---

## 15. CONVENTION SUMMARY

**Fixed/Verified:**
- W₃ definition
- η_W3 definition (conceptual)
- Background choice (S²×S²)
- Fluctuation sector counting (N_eff = 4)
- α₂ = 8 (for cross-check only)
- A_W3 ≠ 0
- Normalization conventions

**Missing/To Be Computed:**
- Explicit S²×S² metric components
- Explicit curvature tensors on S²×S²
- Explicit fluctuation definitions
- Explicit δΓ, δ²Γ
- Explicit TT projector operator
- Explicit quadratic Hessian
- Explicit K_W3 extraction

---

*Document status: CONVENTION AUDIT COMPLETE*
*Next step: Define S²×S² background explicitly*
*Date: August 2026*
