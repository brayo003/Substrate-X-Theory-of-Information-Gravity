# 42_BACKGROUND_S2XS2_DEFINITION
## Explicit S²×S² Background Definition

**Date:** August 2026
**Purpose:** Define S²×S² background metric and curvature tensors explicitly

---

## 1. S²×S² COORDINATE SYSTEM

**Product manifold:** S²(r₁) × S²(r₂)

**Coordinates:**
- First S²(r₁): (θ₁, φ₁) with radius r₁
- Second S²(r₂): (θ₂, φ₂) with radius r₂

**Combined 4D coordinates:** x^μ = (θ₁, φ₁, θ₂, φ₂)

**Metric signature:** (++++) (Euclidean for Wick-rotated FRGE calculation)

---

## 2. METRIC TENSOR

**Standard round metric on S²(r):**
```
ds² = r²(dθ² + sin²θ dφ²)
```

**Product metric on S²(r₁) × S²(r₂):**
```
ds² = r₁²(dθ₁² + sin²θ₁ dφ₁²) + r₂²(dθ₂² + sin²θ₂ dφ₂²)
```

**Metric components (block-diagonal):**
```
g_{μν} = diag(r₁², r₁² sin²θ₁, r₂², r₂² sin²θ₂)
```

**Index ordering:** μ = (θ₁, φ₁, θ₂, φ₂)

---

## 3. INVERSE METRIC

**Inverse metric components:**
```
g^{μν} = diag(1/r₁², 1/(r₁² sin²θ₁), 1/r₂², 1/(r₂² sin²θ₂))
```

---

## 4. METRIC DETERMINANT

**Determinant:**
```
√g = r₁² sinθ₁ × r₂² sinθ₂ = r₁² r₂² sinθ₁ sinθ₂
```

---

## 5. SCALAR CURVATURE

**Each S²(r) has scalar curvature:**
```
R[S²(r)] = 2/r²
```

**Product manifold scalar curvature:**
```
R = R[S²(r₁)] + R[S²(r₂)] = 2/r₁² + 2/r₂²
```

**Special cases:**
- Equal radii r₁ = r₂ = r: R = 4/r²
- Unequal radii: R = 2/r₁² + 2/r₂²

---

## 6. RICCI TENSOR

**Each S²(r) has Ricci tensor:**
```
R_{ab}[S²(r)] = (1/r²) g_{ab}[S²(r)]
```

**Product manifold Ricci tensor (block-diagonal):**
```
R_{μν} = diag((1/r₁²)g_{θ₁θ₁}, (1/r₁²)g_{φ₁φ₁}, (1/r₂²)g_{θ₂θ₂}, (1/r₂²)g_{φ₂φ₂})
```

**Einstein manifold property:**
```
R_{μν} = (R/4) g_{μν}
```

---

## 7. RIEMANN TENSOR

**Each S²(r) has Riemann tensor:**
```
R_{abcd}[S²(r)] = (1/r²)(g_{ac}g_{bd} - g_{ad}g_{bc})
```

**Product manifold Riemann tensor (block-diagonal):**
```
- R_{θ₁φ₁θ₁φ₁} = (1/r₁²)(g_{θ₁θ₁}g_{φ₁φ₁} - g_{θ₁φ₁}g_{φ₁θ₁}) = r₁⁴ sin²θ₁ / r₁² = r₁² sin²θ₁
- R_{θ₂φ₂θ₂φ₂} = (1/r₂²)(g_{θ₂θ₂}g_{φ₂φ₂} - g_{θ₂φ₂}g_{φ₂θ₂}) = r₂⁴ sin²θ₂ / r₂² = r₂² sin²θ₂
- Cross-components R_{aAbB} = 0
```

---

## 8. WEYL TENSOR

**Weyl tensor definition (4D):**
```
C_{μνρσ} = R_{μνρσ} - (1/2)(g_{μρ}R_{σν} - g_{νρ}R_{σμ} - g_{μσ}R_{ρν} + g_{νσ}R_{ρμ}) + (1/6)R(g_{μρ}g_{σν} - g_{μσ}g_{ρν})
```

**On S²×S²:**
- Due to block-diagonal structure and Einstein property, Weyl tensor has specific non-zero components
- The Weyl tensor on S²×S² is non-zero (unlike S⁴)

**Explicit components (derived from literature):**
For equal radii r₁ = r₂ = r:
```
W₃[S²×S²] = 128/27
```

For unequal radii, the Weyl components depend on the ratio r₁/r₂.

---

## 9. W₃ VALUE ON S²×S²

**From 42_GATE2_FINAL.md:**
```
| Background | W₃ | R·C² | R³ |
|------------|-----|------|-----|
| S²×S² equal (R=4) | 128/27 | 16/3 | 64 |
| S²×S² unequal (R=6) | 28 | 12 | 216 |
```

**Status:** W₃ values known numerically for specific radii, but explicit component calculation needed for Hessian

---

## 10. CADABRA2 IMPLEMENTATION

**Cadabra2 file:** 42_background_s2xs2.cdb

**Required definitions:**
1. Coordinates: θ₁, φ₁, θ₂, φ₂
2. Metric: g_{μν} as defined above
3. Inverse metric: g^{μν} as defined above
4. √g as defined above
5. Riemann tensor components
6. Ricci tensor components
7. Scalar curvature
8. Weyl tensor components
9. W₃ value

**Calculation sequence:**
1. Define metric components in Cadabra2
2. Compute Christoffel symbols
3. Compute Riemann tensor
4. Compute Ricci tensor
5. Compute scalar curvature
6. Compute Weyl tensor
7. Compute W₃
8. Verify all symmetries and tracelessness

---

## 11. SPECIAL CASE FOR CALCULATION

**Choice for calculation:** Equal radii r₁ = r₂ = r

**Rationale:**
- Simplifies calculations
- W₃ = 128/27 (known from literature)
- Still retains non-zero Weyl tensor
- Maintains essential feature: C ≠ 0

**Parameter:** Set r such that R = 4/r² = 4 → r = 1

**Simplified metric (r₁ = r₂ = 1):**
```
ds² = dθ₁² + sin²θ₁ dφ₁² + dθ₂² + sin²θ₂ dφ₂²
```

---

## 12. NEXT STEPS

**Phase 2 - Define fluctuation:**
- Define h_{ab} on S²×S² background
- Specify TT conditions
- Derive δg, δg^{-1}

**Phase 3 - Compute δR and δ²R:**
- Use Cadabra2 with the defined background
- Compute δΓ in terms of δg
- Compute δR explicitly
- Compute δ²R explicitly

---

*Document status: BACKGROUND DEFINITION COMPLETE*
*Next step: Implement in Cadabra2*
*Date: August 2026*
