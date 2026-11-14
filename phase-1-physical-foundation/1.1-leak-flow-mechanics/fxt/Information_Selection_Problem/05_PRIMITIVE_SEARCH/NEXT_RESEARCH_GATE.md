# NEXT_RESEARCH_GATE
## Gate 5 → Gate 6 Transition Requirements

**Status:** Verdict B — Conditional Survivor P01
**Date:** August 2026

---

## The Precise State

P01 achieves Outcome B: a real but O(1) weighting of Kasner relative to FLRW in the AS path integral. The gap to Outcome A (true restriction) requires one of three results. This document identifies the smallest mathematically decisive calculation that could resolve P01's status.

---

## The Single Most Decisive Calculation

**Question:** Does the full asymptotic safety effective action Γ_0 — beyond the R + C² truncation — suppress the Kasner saddle point by a factor exponentially larger than exp(−β·O(1))?

This is the central question. It decomposes into two parts:

**Part A — Sign and magnitude of β in the full theory:**

The C² coupling β must be computed in progressively larger truncations to determine whether its fixed-point value converges and whether it converges to a value β >> 1.

Existing calculations:
- R + R² truncation: Lauscher-Reuter (2002) — gives G* and λ* but does not resolve β
- R + C² truncation: Falls-Litim (2014), Ohta-Percacci (2016) — give β > 0, β ~ O(1)
- Full f(Riem) truncation: Not computed

The decisive calculation: compute β* in the truncations R + R² + C² + (additional terms), checking for convergence. If β* converges to a value β >> 1 as the truncation is enlarged, Gap 1 is closed. If β* ~ O(1) in all truncations, the O(1) suppression is confirmed and P01 cannot be upgraded.

This is a finite, specific calculation within the existing AS program. It requires functional RG methods applied to the gravity + Weyl-squared sector with progressively larger operator bases.

**Part B — Whether Kasner remains a saddle point of the full effective action:**

The Bach tensor analysis showed Kasner satisfies B_{μν} = 0 (Bach tensor vanishes for vacuum Kasner because the Weyl tensor is divergence-free). The modified equation G_{μν} − 4β B_{μν} = 0 is therefore satisfied by Kasner regardless of β.

However, in the full effective action (with infinite higher-derivative terms), there are additional terms beyond the Bach tensor. The question is whether any of these terms produce a non-zero contribution for Kasner that prevents it from satisfying the full equations of motion.

The decisive check: compute δΓ_0/δg^{μν} evaluated on the Kasner metric, including all terms in the truncated AS effective action up to order R^4. If any term contributes non-trivially to the Kasner equation of motion, Kasner may not be an exact saddle point of the full effective action, and its path-integral amplitude would be suppressed.

---

## Operational Gate 6 Entry Criterion

Gate 6 (full derivation authorized) requires one of:

**Criterion G6-A:** β* > N_min in the full AS effective action, where N_min is the value for which exp(−β*·C̄²·V_Planck) < ε_threshold for Kasner, with ε_threshold set to a value that constitutes exponential suppression (e.g., < 10^{-10}).

Derivation of N_min: From the Kasner saddle calculation, ∫C²√g ~ O(1) per Planck volume at the Planck epoch. For exponential suppression at the level of 10^{-10}, we need β* > 10 · ln(10) ~ 23. Current AS calculations give β* ~ O(1). The gap is ~ factor of 23. Whether the full theory produces β* ~ 23 is unknown but specific.

**Criterion G6-B:** Proof that Kasner is not a saddle of the full AS effective action — i.e., δΓ_0[Kasner]/δg^{μν} ≠ 0 for at least one higher-derivative term in the full truncation.

If either G6-A or G6-B is established, P01 upgrades to Outcome A and Gate 6 is authorized.

---

## If Neither Criterion Is Met

If the calculation determines β* ~ O(1) in all truncations and Kasner remains a saddle, then:

P01 is downgraded from conditional survivor to eliminated. The conclusion becomes Verdict C (all candidates killed), and the program must address the structural obstruction identified:

**The structural obstruction:** Any quantum gravity mechanism based on path-integral weighting of GR solutions cannot produce a true restriction Γ_phys ⊊ Γ_GR unless (a) the weight is exponentially large (β >> 1) or (b) some classical solutions are excluded as non-saddle-points. Neither is available for AS in its current development.

If both criteria fail, the correct program conclusion is:

> The primitive search is exhausted over the 23 taxonomy classes examined. No primitive achieves Outcome A. The weighting achieved by P01 (Outcome B) is quantitatively insufficient. R1 remains open. A new search class or a reformulation of R1 is required before a new primitive search.

---

## Whether the Taxonomy Was Too Narrow

The 23 classes covered A through W of the taxonomy. The structural obstruction identified (saddle-point inheritance) affects all path-integral-based mechanisms (classes B, R, S, G). The obstruction does not affect dynamical attractor mechanisms (class T) — ekpyrosis is in this class and already represents the strongest partial closure. It does not affect algebraic constraint mechanisms (class C) — but P06 was killed. It does not affect novel matter sectors (class V) — ekpyrosis also falls here.

The taxonomy was not too narrow. The obstruction is structural within the quantum-gravity primitive classes. New primitive classes would need to operate through a mechanism other than path-integral weighting or constraint algebra — candidates would include:
- A mechanism that modifies the set of classical GR solutions directly (requires non-GR dynamics)
- A mechanism that selects initial data via a boundary condition derived from first principles that is not equivalent to the no-boundary proposal (already killed)

Both of these represent genuinely new territory not covered by the 23 classes.

---

## Summary

**The single most decisive calculation:** Compute β* in the full AS effective action and determine whether Kasner remains a saddle point of the complete operator expansion.

**What a positive result (β* >> 1 or Kasner not a saddle) would establish:** P01 upgrades to Outcome A. Gate 6 authorized.

**What a negative result (β* ~ O(1) and Kasner remains a saddle) would establish:** P01 is eliminated. All primitives in the 23-class taxonomy are killed. Program reaches Verdict C.

**Timeline:** This is a computation within the existing AS research program. It does not require new experimental data. It requires extending current truncation calculations to higher order and performing the explicit saddle-point check on the Kasner metric.

---

*Document status: NEXT RESEARCH GATE DEFINED*
*Decisive calculation: β* in full AS effective action + Kasner saddle check*
*Date: August 2026*
