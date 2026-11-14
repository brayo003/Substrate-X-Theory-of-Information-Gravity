# W3 Normalization Audit

**Status: PARTIALLY VERIFIED — C²/W3 ratio computed; FRGE normalization factor UNRESOLVED**  
**Date: 2026-08-24**

---

## What Was Computed

### C² Hessian (for normalization reference)

For the action S_C2 = ∫ d⁴x √g C_{abcd} C^{abcd}, the leading kinetic piece of the
Hessian is the p⁴ part of 2·(δC)²:

    Q_C2(H) = 2 · Σ_{abcd} [δC_{abcd}]²   (all-lowered at g̅=I)

Results on all 5 TT modes:

| Mode | Q_C2 (p⁴ coeff) | |h|² | K_C2 = Q4/|h|² |
|------|----------------|-----|-----------------|
| h+  | +2             | 2   | **+1**          |
| hs  | +6             | 6   | **+1**          |
| hx  | +2             | 2   | **+1**          |
| h02 | +2             | 2   | **+1**          |
| h12 | +2             | 2   | **+1**          |

**K_C2 = 1 universally** — all TT modes give the same eigenvalue for C².  
This is consistent with the fact that C² is isotropic on any Einstein background.

### W3/C² Ratio by Mode

| Mode | K_W3 | K_C2 | Ratio K_W3/K_C2 |
|------|------|------|-----------------|
| h+  | −2   | 1    | **−2**          |
| hs  | +2   | 1    | **+2**          |
| hx  | −2   | 1    | **−2**          |
| h02 | +1   | 1    | **+1**          |
| h12 | +1   | 1    | **+1**          |

The ratio K_W3/K_C2 splits by sector, reflecting the S²×S² product geometry.

---

## The Project's C² Normalization

From `45_ALPHA2_TENSOR_VERIFICATION.md`: **α₂ = 8** is cited as the C² Hessian coefficient.

From `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`: "α₂ = 8 derived from literature + TensorAtlas + manual derivation."

**Discrepancy**: Our direct computation gives K_C2 = 1 (for p⁴, 2·(δC)² term).  
The project's α₂ = 8 is a factor of 8 larger.

**Possible sources of the factor 8**:

1. The FRGE trace with a Litim regulator on S²×S² includes contributions
   from the heat-kernel expansion and the Lichnerowicz spectrum. The effective
   coefficient α₂ in the flow equation is not simply K_C2 evaluated at a single momentum.

2. The project's α₂ may include the full trace: Σ_{modes} (eigenvalue × multiplicity).

3. There may be a convention difference: the FRGE beta function uses
   ∂_t Γ_k = (1/2) Tr[...], with a factor of 1/2 relative to δ²S.

Without the explicit FRGE trace formula (which requires the full Lichnerowicz
spectrum on S²×S² and the regulator choice), we cannot independently verify α₂ = 8.

---

## What Is Needed for η_{W₃}

The formula (from `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`) is:

    η_{W₃} = (N · K_W3) / w̃₃

where N is the FRGE normalization factor derived from the trace. The project
computes N using α₂ = 8 and N_eff = 4.

To verify this, we would need:
1. The explicit Litim regulator functional form.
2. The Lichnerowicz spectrum on S²×S².
3. The projection onto the W₃ operator.
4. A resolution of the sector split (which K_W3 enters N).

None of these are derivable purely from the Hessian computation.

---

## Summary Table

| Quantity | Value | Status |
|----------|-------|--------|
| W₃_bar on S²×S² | 32/9 | VERIFIED |
| C²_bar on S²×S² | 16/3 | VERIFIED |
| K_C2 (p⁴, 2·(δC)²) | 1 (all TT modes) | VERIFIED |
| K_W3 (p⁴, h+,hx sector) | −2 | VERIFIED |
| K_W3 (p⁴, hs sector) | +2 | VERIFIED |
| K_W3 (p⁴, cross-sector) | +1 | VERIFIED |
| α₂ from project | 8 | UNVERIFIED independently |
| FRGE normalization N | — | NOT COMPUTED |
| η_{W₃} | — | CANNOT COMPUTE (UNRESOLVED) |

---

## Consequences

The Hessian computation is **complete** for the p⁴ principal symbol.
The **normalization step** (connecting K_W3 to η_{W₃}) is blocked by:

1. Missing FRGE trace formula (Litim regulator on S²×S²).
2. Sector-split ambiguity in K_W3.
3. Unverified α₂ = 8.

**Do NOT compute η_{W₃}** until these are resolved. Per the stated conditions:
"Do NOT use η_{W₃} = 0.236416. Do NOT use η_{W₃} = 0.050661."

*Document: W3_NORMALIZATION_AUDIT.md*  
*Status: PARTIALLY VERIFIED — Hessian complete; FRGE normalization UNRESOLVED*
