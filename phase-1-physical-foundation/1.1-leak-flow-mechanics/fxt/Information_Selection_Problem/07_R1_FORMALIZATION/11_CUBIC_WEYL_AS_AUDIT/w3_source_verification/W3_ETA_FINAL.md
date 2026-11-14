# W3 Eta — Final Status

**Status: CANDIDATE NOT COMPUTED — STOP CONDITIONS TRIGGERED**  
**Date: 2026-08-24**

---

## STOP Conditions Triggered

The following STOP conditions from the computation specification were triggered:

### STOP 1: Sector Split — No Unique K_W3

> "If the −2/+1 split means that no unique K_W3 exists under the project's
> current Hessian convention — STOP and report."

The W₃ Hessian on S²×S² gives three distinct eigenvalues in the TT sector:

| Sector | Modes | K_W3 |
|--------|-------|------|
| In-sector diagonal | h+, hs | −2, +2 |
| In-sector off-diagonal | hx | −2 |
| Cross-sector | h02, h12 | +1 |

**There is no unique K_W3** under the project's current Hessian convention.

### STOP 2: FRGE Normalization Unresolved

> "The factor relating K_W3 to η_{W₃} must be derived from the project's
> canonical FRGE normalization."

This factor requires:
1. The explicit Litim regulator functional on S²×S²  
2. The Lichnerowicz operator spectrum on S²×S²  
3. A projection prescription for the sector split  
4. Verification of α₂ = 8

None of these have been computed or verified in the current audit.

---

## What HAS Been Established (VERIFIED)

| Quantity | Value | Evidence |
|----------|-------|----------|
| W₃ background scalar | 32/9 | Direct computation, 3 index structures agree |
| C² background scalar | 16/3 | Direct computation |
| Background Weyl symmetries | All satisfied | 0 violations in 256-component enumeration |
| Bianchi identity | Satisfied | 0 violations |
| p⁴ principal symbol | Exclusively from 6·C̄·δC·δC | Phase B derivative-order table |
| K_W3(h+) | −2 | Routes 1 and 2 agree |
| K_W3(hs) | +2 | Routes 1 and 2 agree |
| K_W3(hx) | −2 | Routes 1 and 2 agree |
| K_W3(h02) | +1 | Routes 1 and 2 agree |
| K_W3(h12) | +1 | Routes 1 and 2 agree |
| 3·C̄·C̄·δ²C contribution to p⁴ | ZERO | Phase B computation |
| 128/27 in project docs | ERROR | No normalization convention produces it |

## What Is UNRESOLVED

| Quantity | Blocker |
|----------|---------|
| Unique K_W3 | Sector-split ambiguity |
| FRGE normalization N | Requires Lichnerowicz spectrum + regulator |
| α₂ = 8 verification | No independent derivation found |
| η_{W₃} | Blocked by above two items |

---

## What Would Unblock This

To proceed to Phase G (compute η_{W₃}):

1. **Define the projection prescription**: Which sectors of the TT decomposition
   enter the FRGE trace? The S²×S² background splits TT into three sectors.
   Specify how the supertrace combines them.

2. **Compute the Lichnerowicz spectrum on S²×S²**: The eigenvalues of
   Δ_L = −∇² + R̄ (or the appropriate 4th-order analog) are needed for the trace.
   These are products of S² Laplacian eigenvalues and are in principle computable
   from the known S² spectrum.

3. **Apply the Litim regulator**: With spectrum in hand, perform:
   Tr[K_sector · p⁴ / (K_sector · p⁴ + R_k)] · (∂_t R_k)
   and project onto the W₃ curvature structure.

4. **Verify α₂ = 8** by the same computation applied to the C² Hessian.

---

## What η_{W₃} Is NOT

Per the specification, the following are explicitly rejected:

- η_{W₃} = 0.236416  (REJECTED — not derived from first principles)
- η_{W₃} = 0.050661  (REJECTED — not derived from first principles)
- η_{W₃} = [Goroff-Sagnotti coefficient]  (REJECTED — perturbative, different context)
- η_{W₃} = [dimensional analysis]  (REJECTED — no derivation)

---

## Summary

The Hessian audit (Phases A–F) is complete and internally consistent.  
The p⁴ principal symbol of the W₃ Hessian is verified by two independent routes.  
The sector eigenvalues {−2, +2, −2, +1, +1} are exact.  
The connection to η_{W₃} requires additional input not yet available.

**η_{W₃} = CANDIDATE — NOT COMPUTED**

*Document: W3_ETA_FINAL.md*  
*Status: STOP conditions triggered in Phases D and F. Phases A–E: VERIFIED.*
