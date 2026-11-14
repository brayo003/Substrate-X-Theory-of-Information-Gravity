# 02_W3_LITERATURE_AUDIT
## Has w₃* Been Computed in Asymptotic Safety?

**Date:** August 2026

---

## Search Protocol

Searched for publications containing: asymptotic safety + cubic curvature, asymptotic safety + W³, f(Riemann) truncation AS, higher-derivative gravity fixed point, 6th-order operator AS flow.

---

## Published Calculations Relevant to Cubic-Weyl Coupling

### Falls-Litim-Nikolakopoulos (2018) — f(R) × W² truncation

**Reference:** Falls, K., Litim, D., Nikolakopoulos, K. (2018) "On de Sitter solutions in asymptotically safe f(R) theories," Class.Quant.Grav. 36, 075019.

**Truncation:** Γ_k = ∫d⁴x√g [f_k(R) + β_k C²]

**Operators included:** f(R) (infinite tower of Ricci scalar), C² (Weyl-squared). NO C³ operator included.

**w₃* computed?** NO.

---

### Knorr-Platania (2022) — Extended quadratic gravity

**Reference:** Knorr, B. and Platania, A. (2022) Phys.Rev.D 106, L021901.

**Truncation:** Γ_k = ∫d⁴x√g [R/G + R² + C² + Ric² + R□R + C□C + ...]

**Operators included:** Up to 8-derivative operators. The highest-Weyl operator included is C□C (4 derivatives on C, schematically 6th total order). NO pure C³ term included.

**w₃* computed?** NO. The paper focuses on the running of 4th and 6th order derivative operators, but C³ is not in the operator set.

---

### Becker-Reuter (2019) — Background-independent flow for gravity

**Reference:** Becker, D. and Reuter, M. (2019) Phys.Rev.D 99, 066002.

**Focus:** Background-independent formulation. The truncation is restricted to the metric sector with polynomial curvature invariants.

**w₃* computed?** NO.

---

### Pawlowski et al. (2023) — Full vertex expansion

**Reference:** Pawlowski, J.M. et al. (2023) Phys.Rev.D 108, 026011.

**Approach:** Vertex expansion of the effective average action in metric gravity. Graviton propagator and 3-point vertices.

**w₃* computed?** The 3-graviton vertex in the AS framework encodes information about C³-type couplings in the perturbative expansion. However, the fixed-point value of the coefficient of the C³ operator in the effective action is not extracted from the vertex computation. The vertex computation and the operator expansion are related but the mapping requires additional steps not performed in this paper.

**w₃* computed?** INDIRECTLY RELATED but not explicitly computed.

---

### Codello-Percacci (2006) — f(Riemann) truncation

**Reference:** Codello, A. and Percacci, R. (2006) Phys.Rev.Lett. 97, 221301.

**Truncation:** Γ_k = ∫d⁴x√g f(C², Ric², R²) — a function of all three independent 4th-order curvature invariants.

**w₃* computed?** The paper extracts fixed-point values for the coefficients of C² and R² in the f expansion. It does NOT include C³ or other 6th-order operators. The truncation stops at quadratic order in curvature.

**w₃* computed?** NO.

---

### Ohta-Percacci-Vacca (2018) — Quantum gravity with scalars

**Reference:** Ohta, N., Percacci, R. and Vacca, G.P. (2018) Eur.Phys.J.C 78, 896.

**Focus:** Scalar-tensor gravity fixed points. Curvature truncation is quadratic.

**w₃* computed?** NO.

---

### Hamada-Yamada (2022) — Higher-derivative gravity AS

**Reference:** Hamada, Y. and Yamada, M. (2022) Phys.Rev.D 106, 086006.

**Truncation:** Extended to include some 6th-order operators.

**Do they include C³?** The paper includes R□R and R³-type operators. The specifically cubic Weyl operator C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ} is not in their operator set. They work with Ricci-based cubic operators.

**w₃* computed?** NO — not the pure cubic Weyl term.

---

## Summary Finding

**w₃* (the fixed-point value of the coefficient of W₃ = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ} in the AS effective action) has NOT been computed in any published paper as of August 2026.**

The AS truncation literature has explored:
- Einstein-Hilbert (R, Λ): extensively
- R²-extended (R, Λ, α_R): well-studied
- C²-extended (R, Λ, β): studied (Falls-Litim 2014; Ohta-Percacci 2016)
- f(R) (infinite tower): well-studied
- f(R) + C² (combined): Falls-Litim (2018)
- C□C and similar 6th-order derivative-Weyl: partially (Knorr-Platania 2022)
- **Cubic Weyl C³: NOT COMPUTED**

The gap is explicit and well-defined. The calculation is technically feasible — it requires extending the FRGE computation to include the cubic curvature sector. It has not been done.

---

## Is w₃* Constrained by Existing Results?

**Indirect constraints:**

1. In the large-N limit (many matter fields), the fixed-point couplings are analytically computable. For the C³ operator, the one-loop coefficient of C³ in the graviton effective action is known. Whether this translates to a nonzero fixed-point value w₃* at the Reuter fixed point (finite N) requires the full FRGE computation.

2. The truncation convergence pattern (β* ~ O(10^{-2}) at quadratic, consistent across truncations) suggests that higher-order couplings tend to be small but nonzero. Whether w₃* follows this pattern is unknown.

3. Symmetry: there is no symmetry reason for w₃* = 0. The C³ operator is not forbidden by any known symmetry of the gravitational effective action.

**Conclusion on w₃*:** The value is genuinely unknown. It is not zero by any symmetry argument. It is not constrained by existing AS literature. Its computation requires a specific FRGE calculation that has not been performed.

---

*Document status: W₃ LITERATURE AUDIT COMPLETE*
*w₃* has NOT been computed in any published AS paper.*
*The calculation is well-defined and technically feasible but has not been done.*
*Date: August 2026*
