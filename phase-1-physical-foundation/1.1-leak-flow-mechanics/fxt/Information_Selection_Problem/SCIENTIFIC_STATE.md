# SCIENTIFIC STATE
**Date:** 2026-08-24

---

## 1. EMPIRICAL TARGET

The early universe had near-zero Weyl curvature. No first-principles law explains why the gravitational initial-data sector is restricted to C≈0 rather than generic high-Weyl configurations.

---

## 2. GATE 1 — CLOSED (C² FAILED)

Bach_{μν}=0 identically on all Ricci-flat spacetimes. C² cannot modify the Kasner equation of motion. β* gap: factor 230–2300.

---

## 3. GATE 1B — CLOSED (W3 NONZERO ON KASNER)

Source: `gate1b_kasner_variation.py`. All 15 checklist items verified. Permutation symmetry confirmed. C² control (Bach=0) confirmed.

    E_{11} = E_{22} = 3968 / (243 t^{22/3})  ≠ 0
    E_{33} = 6272 / (243 t^{16/3})            ≠ 0

W3 modifies the Kasner equation of motion. This gate is closed.

---

## 4. GATE 2 — CLOSED (FAILED: w3*=0)

**Canonical computation: `gate2_canonical.py` (2026-08-24)**

All eight closure criteria satisfied. No assumed inputs used.

### Operator basis

In 4D there is one independent parity-even cubic Weyl scalar (I5 = 2 I6 is a universal identity, verified numerically for 10 random Weyl tensors). The operator basis is {W3} and the S²×S² projection is unambiguous.

### C² and W3 Hessian per TT mode (computed from first principles)

Background: S²×S² equal radii r=1, equatorial point (ḡ=I, all Γ̄=0).
Verified: C̄² = 16/3,  W3_bar = 32/9.

| Mode | \|H\|² | C² Q₄ | α₂ = Q₄/\|H\|² | W3 Q₄ | K_W3 | W3 Q₀ |
|------|--------|--------|-----------------|--------|------|-------|
| h+   | 2      | 2      | **1**           | −4     | −2   | −1    |
| hs   | 6      | 6      | **1**           | 12     | +2   | +5    |
| hx   | 2      | 2      | **1**           | −4     | −2   | −1    |
| h02  | 2      | 2      | **1**           | +2     | +1   | 0     |
| h12  | 2      | 2      | **1**           | +2     | +1   | 0     |

**α₂ = 1 is identical for all 5 TT modes** (computed, not assumed).

Σ_s K_s = (−2) + (2) + (−2) + (1) + (1) = **0**

### Non-TT sectors and ghosts

| Sector       | ∂Hessian/∂w3       | W3 projection | Reason                              |
|--------------|--------------------|---------------|-------------------------------------|
| TT graviton  | K_s · p⁴ · δ^{TT,s}| nonzero       | computed above                      |
| Vector       | 0                  | zero          | pure gauge (longitudinal diffeo.)   |
| Scalar trace | 0                  | zero          | C is traceless, C^μ_{νμρ}=0        |
| Scalar long. | 0                  | zero          | gauge mode in de Donder             |
| Ghost        | 0                  | zero          | W3=C³ does not couple to FP ghosts  |

### FRGE trace chain

Full chain evaluated in `gate2_canonical.py`:

    Γ^(2) = Z_N(p²−2Λ) + 2·α₂·w̃₂·p⁴ + w̃₃·K_s·p⁴   [TT sector s]
    R_k   = Z_N(k²−p²)θ(k²−p²)
    ∂_t R_k = 2Z_N k² θ(k²−p²)
    G_s^(0) = 1/D₀  where  D₀ = Z_N(1−2λ)k² + 2α₂·w̃₂·k⁴  (Litim, p²→k²)
    d/dw̃₃ G_s = −K_s p⁴ / D₀²

Since α₂ is sector-independent, D₀ is the same for all s, so the threshold integral I = k⁶/(24π² D₀²) is the same for all sectors:

    A_W3 = (1/W3_bar) · ½ · Σ_s K_s · [2Z_N k² · I]
         = (9/32) · [Σ_s K_s] · Z_N k⁸/(24π² D₀²)
         = (9/32) · 0 · (nonzero factor)
         = **0** (exact)

### η_W3

η_W3 arises from the same d/dw̃₃ trace projected onto W3. The same Σ_s K_s = 0 cancellation applies. At leading order in the TT sector:

    η_W3 = 0

### Beta function and fixed point

    β_{w̃₃} = (2 + η_W3) · w̃₃ + A_W3
            = 2 · w̃₃

    w̃₃* = 0  (unique fixed point)

The degenerate case η_W3 = −2 does not arise; η_W3 = 0 from the computation.

### Independent controls (all pass except Control 6 normalization note)

1. W3 eigenvalues reproduced from scratch: ✓ match {−2,+2,−2,+1,+1}
2. C² eigenvalues computed: ✓ α₂=1 for all TT modes (direct method)
3. Litim regulator against scalar Laplacian: ✓ gives π²k⁴ (standard)
4. Trace at w3=0 has no W3 projection: ✓
5. Normalization independence of fixed point: ✓
6. Second (bilinear-form) method for C²: gives α₂=2 for off-diagonal modes due to a normalization convention mismatch (basis vector norm ≠ full-matrix norm for H[i][j]=H[j][i]=1). Direct method α₂=1 is correct; mismatch is diagnosed and not a physical discrepancy.
7. W3 eigenvalues match W3_FULL_HESSIAN_COMPONENTS.py: ✓
8. Sector-independent denominator confirmed: ✓

### Critical path of the cancellation

The result A_W3=0 rests on two independently verified facts:

1. **Σ_s K_s = 0**: The W3 Hessian eigenvalues on S²×S² exactly cancel across the 5 TT modes. This is a consequence of the S²×S² geometry, not an assumption.

2. **α₂ is sector-independent**: The C² Hessian gives the same p⁴ coefficient (α₂=1) for all TT modes on this Einstein background, making the regulated propagator denominator D₀ identical for all sectors.

If either fact were false, A_W3 could be nonzero. Both are verified by direct computation in `gate2_canonical.py`.

---

## 5. PHYSICAL STATUS

**The W3 mechanism is mathematically non-trivial (Gate 1B: E_{μν}≠0 on Kasner) but does not survive the RG test (Gate 2: w3*=0).**

Without a nonzero w̃₃* at the AS UV fixed point, the W3 term is not present in the fixed-point effective action. The exclusion of Kasner from the solution set requires w̃₃*≠0. Since w̃₃*=0, Kasner is not excluded.

The W3 route fails to provide the selection function F for R1.

---

## 6. DECISION

The W3/AS mechanism in the EH+C²+W3 truncation does not produce a nonzero cubic Weyl coupling at the UV fixed point. The mechanism is eliminated within this truncation.

The C² route was eliminated by Gate 1 (exact structural identity). The W3 route is eliminated by Gate 2 (exact algebraic cancellation of the source term, verified from first principles).

**Both candidate mechanisms for solving R1 via Asymptotic Safety are eliminated within the tested truncations.**

R1 (the cosmological initial-state problem) remains open.

A nonzero w̃₃* at some other fixed point could not in any case establish: low-Weyl initial-state selection, exclusion of generic high-Weyl initial data, dynamical attraction toward FLRW, resolution of the arrow-of-time problem, or an observational prediction. Those require further gates.

---

*Canonical computation: `07_R1_FORMALIZATION/11_CUBIC_WEYL_AS_AUDIT/gate2_canonical.py` (2026-08-24)*
*Supporting evidence: `gate1b_kasner_variation.py` (Gate 1B), `W3_FULL_HESSIAN_COMPONENTS.py` (W3 eigenvalues)*
