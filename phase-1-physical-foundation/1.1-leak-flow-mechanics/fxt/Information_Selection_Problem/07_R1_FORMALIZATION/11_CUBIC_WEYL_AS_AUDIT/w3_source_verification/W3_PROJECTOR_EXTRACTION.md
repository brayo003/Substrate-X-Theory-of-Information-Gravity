# W3 Projector Extraction

**Status: PARTIALLY VERIFIED — sector split identified; projector contraction UNRESOLVED**  
**Date: 2026-08-24**

---

## Source of the FRGE Projector Definition

From `13_FRGE_TRUNCATION_SPEC.md`:

    β_{w₃} = projection of (1/2) STr[ (Γ_k^{(2)} + R_k)^{-1} ∂_t R_k ] onto ∫√g W₃

From `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`:

    η_{w̃₃} = (1/w̃₃) × (loop corrections proportional to w̃₃)

The FRGE flow equation requires projecting the supertrace onto the W₃ operator.
The relevant piece of Γ_k^{(2)} from the W₃ term is exactly the Hessian
computed in W3_FULL_HESSIAN_COMPONENTS.py.

**No file in the repository defines an explicit projector formula** (explicit matrix
or operator-valued distribution). The projector is implicit in the phrase
"project onto ∫√g W₃".

---

## TT Sector Decomposition for p = (0,0,0,t)

The transverse-traceless sector on S²×S² with momentum p = (0,0,0,t) consists of
5 independent modes:

| Mode | H_{μν} | Type | K_W3 |
|------|---------|------|------|
| h+  | diag(1,−1,0,0) | in-sector diagonal (S²₁ sector) | **−2** |
| hs  | diag(1,+1,−2,0) | in-sector diagonal (S²₁+S²₂ trace-free mix) | **+2** |
| hx  | H_{01}=H_{10}=1 | in-sector off-diagonal | **−2** |
| h02 | H_{02}=H_{20}=1 | cross-sector (S²₁×S²₂) | **+1** |
| h12 | H_{12}=H_{21}=1 | cross-sector (S²₁×S²₂) | **+1** |

TT conditions for p=(0,0,0,t):
- **Transverse**: h_{3μ} = 0 → eliminates (33),(03),(13),(23)
- **Traceless**: H_{00}+H_{11}+H_{22} = 0 → reduces the diagonal sector

The p⁴ Hessian matrix is **block diagonal** in these 5 TT modes (no mixing between sectors in the p⁴ piece).

---

## The Sector Split

The S²×S² background breaks the SO(4) isotropy of flat space into
SO(3) × SO(3) (the isometry of S²₁ × S²₂). Under this decomposition:

- **In-sector modes** (both indices in the same S²_i factor): eigenvalues −2, +2, −2
- **Cross-sector modes** (one index per S²_i): eigenvalue +1

These are **inequivalent** representations of the background isometry.

---

## What the FRGE Trace Requires

The Wetterinck equation supertrace is:

    STr[ (Γ^{(2)} + R_k)^{-1} ∂_t R_k ]

On S²×S², this trace splits over the spectrum of the Lichnerowicz operator.
For the W₃ contribution to β_{w₃}, the relevant Hessian is:

    Γ^{(2)}_{W₃}|_{p-sector} = K_{sector}(p) · p⁴ · (TT projector in sector)

The trace then sums:

    Σ_{sector} N_{sector} · [K_{sector} · p⁴ + (p² and p⁰ terms)] / (K_{sector}·p⁴ + regulator)

where N_{sector} is the degeneracy of each sector on S²×S².

From `41_W3_HESSIAN_CONVENTIONS_AUDIT.md`: N_eff = 4 total TT modes (counting
h+ and hx as the standard graviton polarizations, plus h02 and h12 as S²₁×S²₂ mixing modes).

---

## Critical Unresolved Issue: No Unique K_W3

The FRGE flow equation for β_{w₃} requires a **single scalar quantity** K_W3
to define the anomalous dimension:

    η_{W₃} = f(K_W3)

But the W₃ Hessian on S²×S² gives **three distinct eigenvalues**:

    K_W3 ∈ {−2, +2, +1}

depending on the TT sector.

### Options for resolution

**Option A**: Average over all 5 TT modes (counting multiplicities):
    K_W3^{avg} = (−2·1 + 2·1 + (−2)·1 + 1·1 + 1·1) / 5 = 0/5 = 0

This would give K_W3 = 0, which is **suspicious** (would imply no kinetic W₃ contribution).

**Option B**: Weight by sector degeneracy on S²×S² (requires heat-kernel computation):
    K_W3 = Σ_s N_s · K_s / Σ_s N_s

This requires the full spectrum, not yet computed.

**Option C**: Use only the spin-2 TT graviton sector (h+ and hx):
    K_W3^{TT2} = average of K(h+), K(hx) = (−2 + (−2))/2 = −2

This is the standard FRGE choice for the graviton contribution.

**Option D**: Use the projector that appears in the flat-space limit (all modes equivalent):
    Not applicable — S²×S² explicitly breaks this symmetry.

**Recommendation**: The FRGE computation requires a specific projection prescription.
The project's documents do not define which option to use. This must be resolved
before a unique K_W3 can be extracted for η_{W₃}.

---

## What IS Established

1. The p⁴ Hessian eigenvalues are exact: {−2, +2, −2, +1, +1}.
2. The block structure is fully determined.
3. The in-sector (standard graviton) sector gives K = −2.
4. The cross-sector gives K = +1.
5. No single K_W3 characterizes all 5 TT modes simultaneously.

---

## STOP Condition Triggered

Per the stated STOP conditions:

> "If the -2/+1 split means that no unique K_W3 exists under the project's current
> Hessian convention — STOP and report."

**STOP: The sector split {−2, +2, −2, +1, +1} means there is no unique K_W3 in
the TT sector on S²×S².**

A unique K_W3 can only be extracted after:
1. Specifying which sectors enter the FRGE trace,
2. Computing the sector degeneracies on S²×S², and
3. Defining the projection prescription explicitly.

*Document: W3_PROJECTOR_EXTRACTION.md*  
*Status: PARTIALLY VERIFIED — sector eigenvalues exact; projection prescription UNRESOLVED*
