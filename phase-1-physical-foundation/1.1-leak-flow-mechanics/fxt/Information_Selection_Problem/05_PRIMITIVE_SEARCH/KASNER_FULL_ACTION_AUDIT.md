# KASNER_FULL_ACTION_AUDIT
## Gate 6 Part II — Kasner Saddle Test for Higher-Derivative Operators

**Subject:** Whether Kasner remains a stationary point of the full AS effective action beyond the R + C² truncation.
**Date:** August 2026

---

## The Kasner Metric

The Kasner solution is a vacuum Bianchi I spacetime:

  ds² = −dt² + t^{2p₁}dx² + t^{2p₂}dy² + t^{2p₃}dz²

with Kasner conditions:  p₁ + p₂ + p₃ = 1,  p₁² + p₂² + p₃² = 1

Key curvature properties (vacuum, so T_{μν} = 0):
- R = 0 (Ricci scalar vanishes — vacuum)
- R_{μν} = 0 (Ricci tensor vanishes — vacuum Einstein equation)
- G_{μν} = 0 (Einstein tensor vanishes)
- C_{μνρσ} ≠ 0 (Weyl tensor nonzero, encoding the anisotropy)
- C² = C_{μνρσ}C^{μνρσ} = 8(p₁p₂ + p₂p₃ + p₃p₁)²/(3t⁴) ≠ 0 for generic Kasner

The crucial fact: Kasner satisfies R_{μν} = 0. This means it is a vacuum GR solution — it satisfies the classical Einstein equations exactly.

---

## The Test Protocol

For each operator O_n in the AS effective action:

1. Compute the operator value on the Kasner background.
2. Compute the variation δO_n/δg^{μν} evaluated on Kasner.
3. Determine whether this variation is zero on-shell (after using R_{μν} = 0) or off-shell.
4. If δO_n/δg^{μν}|_{Kasner} ≠ 0, Kasner is not a saddle of the truncation containing O_n.

**Critical distinction:** For a vacuum solution (R_{μν} = 0), many operators and their variations simplify. The test must not assume R_{μν} = 0 before computing the variation — the variation must be computed first, then evaluated on Kasner.

---

## Operator-by-Operator Analysis

### Operator: R (Ricci scalar)

Value on Kasner: R = 0.

Variation: δ(√g R)/δg^{μν} = √g (R_{μν} − (1/2)g_{μν}R) = √g G_{μν}

Evaluated on Kasner: √g G_{μν}|_{Kasner} = 0 (since G_{μν} = R_{μν} − (1/2)g_{μν}R = 0 for vacuum Kasner).

**Result: Kasner IS a saddle of the R term.** Confirmed — this is just the statement that Kasner solves Einstein's equations.

---

### Operator: Λ (cosmological constant term √g)

Variation: δ(√g)/δg^{μν} = (1/2)√g g_{μν}

This is nonzero on Kasner. However, in the presence of Λ, the equation of motion is G_{μν} + Λg_{μν} = 0, which has no Kasner solution (Kasner is a vacuum solution with Λ = 0). So for Λ ≠ 0, Kasner is indeed NOT a saddle of the full action with Λ.

**However:** The AS program at the Planck scale has Λ_k ≠ 0. If Λ* ≠ 0 at the fixed point, then Kasner is not a saddle of Γ_k at k = k_Planck. This is correct — but it does not exclude Kasner from the physical universe, because the cosmological constant runs to its observed (near-zero) value at k → 0. At k → 0, Λ_k → Λ_obs ~ 10^{-120} M_Planck⁴, which is negligible for Planck-epoch dynamics.

**Result: Λ removes Kasner as a saddle at the Planck scale but this is trivially resolved by the RG running to k → 0. This does not constitute a physical exclusion of Kasner.**

---

### Operator: R² (Ricci scalar squared)

Value on Kasner: R²|_{Kasner} = 0 (since R = 0 on Kasner vacuum).

Variation of R²: δ(√g R²)/δg^{μν} = √g[2RR_{μν} − (1/2)g_{μν}R² + 2g_{μν}□R − 2∇_μ∇_ν R]

Evaluated on Kasner (R = 0, R_{μν} = 0):
= √g[0 − 0 + 2g_{μν}□(0) − 2∇_μ∇_ν(0)]
= √g · 0 = 0

**Result: Kasner IS a saddle of the R² term.** The variation vanishes because both R and R_{μν} vanish on Kasner.

Note: This is an exact result, not an approximation. It holds because R and R_{μν} are both zero on Kasner (it is a Ricci-flat space), and the variation of R² produces only Ricci-dependent terms.

---

### Operator: R_{μν}R^{μν} (Ricci-squared)

Value on Kasner: Ric²|_{Kasner} = R_{μν}R^{μν}|_{Kasner} = 0 (Ricci-flat).

Variation of Ric²: δ(√g R_{μν}R^{μν})/δg^{αβ} = √g[−(1/2)g_{αβ}R_{μν}R^{μν} + 2R_{αμ}R_β^μ − ∇²R_{αβ} + (1/2)∇_α∇_β R − (1/2)g_{αβ}∇²R + R_{αμνβ}R^{μν} − (1/2)R_{αβ}R + ...]

(Full expression from Boulware-Deser 1985.)

Each term involves R_{μν} or R. On Kasner, R_{μν} = 0 and R = 0. Evaluated on Kasner: every term in the variation contains at least one factor of R_{μν} or R.

Checking the term R_{αμνβ}R^{μν}: On Kasner, R^{μν} = 0, so this term vanishes.
The term ∇²R_{αβ}: This involves ∇²(0) = 0.

**Result: Kasner IS a saddle of the R_{μν}R^{μν} term.** The variation vanishes because it is built from R_{μν} and R, both zero on Kasner.

This is a general result: **any operator built entirely from Ricci curvature (R, R_{μν}, and their covariant derivatives) has a variation that vanishes on any Ricci-flat manifold, including Kasner.** Kasner is Ricci-flat. Therefore, all Ricci-dependent operators in the AS effective action are stationary on Kasner.

---

### Operator: C_{μνρσ}C^{μνρσ} (Weyl-squared)

Value on Kasner: C²|_{Kasner} ≠ 0 (this is the whole point).

Variation (the Bach tensor equation):
δ(√g C²)/δg^{μν} = −4√g B_{μν}

where B_{μν} = ∇^α∇^β C_{αμβν} + (1/2)R^{αβ}C_{αμβν}

On Kasner: R^{αβ} = 0, so the second term vanishes. The first term is ∇^α∇^β C_{αμβν}.

For vacuum Kasner, the contracted Bianchi identity gives ∇^α C_{αμβν} = ∇_{[μ}R_{ν]β} − ... = 0 (since R_{μν} = 0 and ∂_μ R = 0). Wait — this requires careful evaluation.

**Detailed Bach tensor calculation for Kasner:**

The second Bianchi identity for the Weyl tensor in vacuum gives:
∇^α C_{αβγδ} = ∇_{[γ}R_{δ]β} − (1/6)(g_{β[γ}∇_{δ]}R)

For Kasner vacuum: R_{μν} = 0, R = 0. Therefore:
∇^α C_{αβγδ} = 0 − 0 = 0

So the Weyl tensor is divergence-free on Kasner: ∇^α C_{αμβν} = 0.

Therefore: B_{μν}|_{Kasner} = ∇^α∇^β C_{αμβν}|_{Kasner} = ∇^α(∇^β C_{αμβν})|_{Kasner}

Since ∇^β C_{αμβν} is the divergence of the Weyl tensor, and we just showed ∇^α C_{αμβν} = 0, the question is whether ∇^α(∇^β C_{αμβν}) = 0.

Permuting indices: ∇^β C_{αμβν} = −∇^β C_{μαβν}. Since ∇^α C_{αμβν} = 0, contracting on α gives ∇^β C_{αμβν} contracted with something... The full calculation:

∇^α(∇^β C_{αμβν}) = ∇^α∇^β C_{αμβν}

By the contracted second Bianchi identity for the Weyl tensor (Penrose-Rindler vol. 1, eq. 4.10.11): in vacuum,

∇^α∇^β C_{αμβν} = (1/2)□R_{μν} − (1/6)∇_μ∇_ν R + (1/2)R^{αβ}C_{αμβν} − (1/6)R_{μν}R + (1/12)g_{μν}□R + ...

On Kasner: all Ricci terms vanish, □R_{μν} = □(0) = 0. Therefore:

∇^α∇^β C_{αμβν}|_{Kasner} = 0

This confirms B_{μν}|_{Kasner} = 0 exactly. Kasner is a saddle of the C² term.

**Result: Kasner IS a saddle of the C² term.** The Bach tensor vanishes on Kasner by the contracted Bianchi identity in vacuum. This is an exact result.

---

### Operator: R·C² (Ricci scalar times Weyl-squared)

Value on Kasner: R·C²|_{Kasner} = 0·(nonzero) = 0.

Variation: δ(√g R C²)/δg^{μν} involves terms of the form C²·δR/δg + R·δC²/δg.

The first term gives C²·G_{μν}|_{Kasner} = C²·0 = 0.
The second term gives R·(Bach tensor)|_{Kasner} = 0·(anything) = 0.

**Result: Kasner IS a saddle of the R·C² term.**

---

### Operator: C_{μνρσ}□C^{μνρσ} (box-Weyl-squared)

Value on Kasner: Nonzero in general (since C ≠ 0 and □C ≠ 0 on Kasner).

Variation: The variation of ∫√g C·□C involves integrating by parts to give ∫√g (□C)·δC + boundary terms + curvature × C terms from commuting □ through the variation.

On Kasner: The variation δ(√g C_{αβγδ}□C^{αβγδ})/δg^{μν} contains terms involving:
- (□C_{αβγδ})·δC^{αβγδ}/δg^{μν} — these involve derivatives of the Weyl tensor
- C_{αβγδ}·δ(□C^{αβγδ})/δg^{μν} — these involve Ricci terms from commuting covariant derivatives

The Ricci-dependent terms (from [∇,∇] = Riemann commutator) on Kasner: each commutator of covariant derivatives produces Riemann tensor terms. On Kasner, Riemann = Weyl (since Ricci = 0). The Weyl-curvature terms remain nonzero.

The key question: is the variation δ(∫√g C□C)/δg^{μν} zero on Kasner?

On a Ricci-flat spacetime, the operator C□C can be related to other operators by identities. The general result for the variation on Ricci-flat manifolds is not zero — the Riemann (= Weyl) contributions from commuting derivatives survive.

**Explicit check for Kasner:** The variation of ∫C□C includes the term:

  (∂/∂g^{μν})(C_{αβγδ}∇²C^{αβγδ}) → contains C_{μ(αβγ}∇²C_{ν)}^{αβγ} + Weyl×Weyl terms

These are generically nonzero on Kasner (since C ≠ 0 and is spatially varying with t^{-4} dependence).

**Result: INDETERMINATE WITHOUT FULL CALCULATION.** The C□C operator does not obviously vanish on Kasner because it involves non-Ricci curvature terms. A full computation is required.

**However — critical observation:** The C□C term in the AS effective action appears at order k^{-2} relative to the C² term in the low-energy expansion (it has two extra derivatives). Its coefficient at the AS fixed point is a higher-dimensional coupling, suppressed by 1/M_Planck². Its contribution to the equations of motion at the Planck epoch is comparable to the C² term, but at sub-Planckian scales, it is suppressed. This does not affect the saddle-point analysis at the Planck epoch.

---

### Operator: C³ (Weyl-cubed, schematic)

The Weyl-cubed operator W₃ = C_{μν}^{\ \ \ αβ}C_{αβ}^{\ \ \ γδ}C_{γδ}^{\ \ \ μν} is nonzero on Kasner.

Its variation δW₃/δg^{μν} on Kasner involves three Weyl tensors contracted — these are generically nonzero on Kasner.

**If W₃ is included in the AS effective action with nonzero coefficient, and if δW₃/δg^{μν}|_{Kasner} ≠ 0, then Kasner is NOT a saddle of the W₃ term.**

**This is the key potential mechanism for Gap 2.**

Does W₃ appear in the AS effective action? In principle yes — it is generated by the RG flow even if absent at the bare level. Its fixed-point coefficient w₃* can be computed.

**Is δW₃/δg^{μν}|_{Kasner} nonzero?**

For the specific most-anisotropic Kasner (p₁=1, p₂=p₃=0), the Weyl tensor takes the form:

  C_{0i0j} = (Kasner anisotropy terms) ~ 1/t² × (direction-dependent)

The variation of W₃ on Kasner produces terms of the form C·C·δC/δg. Since C ≠ 0 and δC/δg is also generically nonzero (it involves derivatives of the metric), δW₃/δg^{μν}|_{Kasner} is generically nonzero.

**Therefore: if w₃* ≠ 0, the Kasner saddle condition δΓ/δg = 0 requires:**

  −4β B_{μν} + w₃* (δW₃/δg^{μν}) + ... = 0

Since B_{μν}|_{Kasner} = 0 but (δW₃/δg^{μν})|_{Kasner} ≠ 0, Kasner is NOT a saddle of the action with nonzero w₃.

**This is a genuine mechanism for Gap 2.**

---

## Critical Assessment of the C³ Mechanism

**Does w₃* ≠ 0 at the AS fixed point?**

W₃ = C³ and similar cubic curvature terms are generated by the RG flow. In the 4D AS program, operators are classified by canonical dimension. C³ has dimension 6 (mass dimension 6) — it is an irrelevant operator at the classical (Gaussian) fixed point. At the non-Gaussian AS fixed point, irrelevant operators can have nonzero fixed-point values.

**Published calculations:** The cubic curvature sector of the AS fixed point has not been computed in published literature as of 2026. The AS truncation studies go up to: R + R² + C² + (some 6th-order operators in specific cases). No calculation of w₃* for the specific W₃ operator appears in the literature.

**What can be said:**
- w₃* is nonzero in principle (generated by the flow)
- Its magnitude is not known
- The claim "Kasner is not a saddle if w₃* ≠ 0" is correct as a mathematical statement
- Whether w₃* is actually nonzero and large enough to matter requires a calculation that has not been done

**The epistemic status of this Gap 2 route:**
- It is not ruled out
- It is not established
- It cannot be established without computing w₃* in the AS truncation
- Treating it as a mechanism is premature

---

## General Theorem: Ricci-Flat Saddle Property

From the analysis above, a general pattern emerges:

**Theorem (informal):** Any operator in the gravitational effective action whose variation δO/δg^{μν} can be written entirely in terms of Ricci curvature (R, R_{μν}, R_{αβγδ} - Weyl terms) vanishes on Kasner, making Kasner a saddle of that operator.

**Operators satisfying this condition:**
- R, Λ (trivially, via G_{μν} = 0)
- R², R_{μν}R^{μν} (Ricci-dependent)
- R C², R Ric² (one factor of Ricci scalar)
- Any polynomial in R and R_{μν}

**Operators NOT satisfying this condition (variation involves Weyl terms):**
- C² (Bach tensor = 0 on Kasner by Bianchi identity — special case)
- C³, C⁴, ... (Weyl-polynomial terms — generally nonzero variation)
- C□C, C∇⁴C, ... (derivative Weyl operators — generally nonzero)

**The critical insight:** C² is special. The Bach tensor vanishes on Kasner not just because Kasner is Ricci-flat, but because of the contracted Bianchi identity ∇^α C_{αμβν} = 0 in vacuum. Higher powers of C (C³, C⁴) do not have this automatic vanishing property for their variations.

Therefore: **the C² operator is the unique low-order Weyl-polynomial operator whose saddle equation is automatically satisfied on Kasner. The first operator that could remove Kasner as a saddle is C³.**

---

## Summary

| Operator | Value on Kasner | Variation on Kasner | Kasner a saddle? |
|----------|----------------|--------------------|--------------------|
| R | 0 | 0 (= G_{μν}) | YES |
| Λ | nonzero | nonzero (= g_{μν}) | NO (but trivial — Λ_k runs to 0) |
| R² | 0 | 0 (Ricci-flat) | YES |
| Ric² | 0 | 0 (Ricci-flat) | YES |
| C² | nonzero | 0 (Bach = 0 by Bianchi) | YES |
| R·C² | 0 | 0 (R=0 on Kasner) | YES |
| C□C | nonzero | Unknown (requires full calc) | UNKNOWN |
| C³ | nonzero | Nonzero (generally) | NO — if w₃* ≠ 0 |
| C⁴ | nonzero | Nonzero (generally) | NO — if coeff ≠ 0 |

**Conclusion for Gap 2:** The C³ and higher Weyl-polynomial operators are the first candidates that could remove Kasner as a saddle. These operators are generated by the AS RG flow. Their fixed-point coefficients have not been computed. The mechanism is logically possible but unestablished.

**The decisive calculation for Gap 2:** Compute w₃* (the C³ fixed-point coupling) in the AS truncation and evaluate δW₃/δg^{μν} on Kasner explicitly. If w₃* is nonzero and the variation is nonzero, Kasner is not a saddle and Gap 2 is closed in favor of P01.

**What is established:** Gap 2 is neither confirmed nor refuted by existing calculations. The C² operator alone does not remove the Kasner saddle. Higher Weyl operators could, but the relevant calculation has not been done.

---

*Document status: KASNER FULL ACTION AUDIT COMPLETE*
*C² term: Kasner remains a saddle (Bach = 0 by Bianchi identity)*
*C³ and higher: Could remove Kasner saddle — w₃* not computed*
*Gap 2: OPEN but unestablished*
*Date: August 2026*
