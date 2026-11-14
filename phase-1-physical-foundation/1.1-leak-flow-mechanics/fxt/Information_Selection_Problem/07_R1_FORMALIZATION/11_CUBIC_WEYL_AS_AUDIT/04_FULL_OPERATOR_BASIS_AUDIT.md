# 04_FULL_OPERATOR_BASIS_AUDIT
## Does the Full Operator Basis Cancel the W₃ Contribution on Kasner?

**Date:** August 2026

---

## The Question

Even if w₃* ≠ 0 and δW₃/δg|_{Kasner} ≠ 0, the full effective action contains many operators. The equation of motion on Kasner is:

  δΓ_AS/δg^{μν}|_{Kasner} = Σ_n w_n* δO_n/δg^{μν}|_{Kasner} = 0?

where the sum is over all operators O_n in the AS effective action with fixed-point couplings w_n*.

If the W₃ contribution is exactly cancelled by contributions from other operators, Kasner remains a saddle.

---

## Operators That Vanish on Kasner (Cannot Cancel W₃)

From KASNER_FULL_ACTION_AUDIT.md:

All operators built from Ricci tensor or Ricci scalar vanish on Kasner because R_{μν} = 0, R = 0. These include:
- R, R², R_{μν}R^{μν}, R³, R_{μν}R^{νρ}R^{ρμ}, R R_{μν}R^{μν}, ...
- R□R, R_{μν}□R^{μν}, ...
- R × C², R_{μν} × C^{μανβ}C_{αβ}, ...

Their variations on Kasner all involve Ricci tensors (from integration by parts and the variation formulas) and vanish. They cannot produce a nonzero contribution to δΓ/δg|_{Kasner}.

**These operators cannot cancel the W₃ contribution.**

---

## Operators That Do Not Vanish on Kasner

The only operators that can contribute a nonzero δO_n/δg|_{Kasner} are those built purely from the Weyl tensor (and its covariant derivatives), since on Kasner Riemann = Weyl.

Complete list of independent Weyl-polynomial operators at each order:

**4th order (quadratic Weyl):**
- C² = C_{αβγδ}C^{αβγδ}: variation = Bach tensor B_{μν} = 0 on Kasner (KASNER_FULL_ACTION_AUDIT result)

**6th order (cubic Weyl):**
- W₃ = I₁ = C_{αβγδ}C^{αβ}_{\ εζ}C^{γδεζ}: variation nonzero (this file)
- I₂ = parity-odd cubic: zero in parity-invariant theory

**8th order (quartic Weyl):**
- I₄₁ = (C²)² = C_{αβγδ}C^{αβγδ} C_{εζμν}C^{εζμν}: scalar squared
- I₄₂ = C_{αβγδ}C^{αβ}_{\ εζ}C^{γδμν}C_{μν}^{\ \ εζ}: cyclic quartic
- Additional independent quartic Weyl invariants...

Their variations on Kasner are generically nonzero (same argument as W₃).

**Higher-order Weyl operators:** Also nonzero on Kasner.

---

## Could Other Weyl-Polynomial Operators Cancel W₃?

The equations of motion on Kasner from the full effective action:

  Σ_n w_n* δ(W_n)/δg^{μν}|_{Kasner} = 0

For this to hold (Kasner to be a saddle), we would need:

  w₃* (δW₃/δg)|_{Kasner} = − Σ_{n≥4} w_n* (δW_n/δg)|_{Kasner}

This is a specific algebraic identity between the fixed-point couplings and the Kasner metric variations. It would require:

1. A specific numerical relationship between w₃*, w₄₁*, w₄₂*, ...
2. This relationship to hold exactly at the AS fixed point

There is no known symmetry or theorem that requires such a cancellation. The AS fixed-point couplings are computed independently for each operator, and their values are not constrained to satisfy this cancellation identity.

**Assessment:** Accidental cancellation is possible but has no support from any known result. The fixed-point couplings at higher orders are not constrained to cancel the W₃ contribution on Kasner.

---

## Field Redefinition Ambiguity

Could a field redefinition g_{μν} → g_{μν} + ε f_{μν}(g) transform the W₃ term into a total derivative or into operators that vanish on Kasner?

For field redefinitions in higher-derivative gravity:
- At quadratic order: field redefinitions can be used to eliminate some R² or Ric² operators (they can be moved into R or R_{μν} terms via the Gauss-Bonnet identity and Bianchi identities).
- At cubic order in curvature: field redefinitions can produce Gauss-Bonnet-type identities. In 4D, the Gauss-Bonnet term GB = R² − 4Ric² + C² is topological (total derivative) and its cube GB³ or products with other scalars can be simplified.

However: the cubic Weyl W₃ is NOT related to the Gauss-Bonnet term by any simple field redefinition. The Gauss-Bonnet identity in 4D involves only quadratic curvature. There is no 4D analog for cubic curvature that trivializes W₃.

**Conclusion:** No field redefinition eliminates W₃ in 4D.

---

## Conclusion

If w₃* ≠ 0:
- No Ricci-based operator can cancel δW₃/δg|_{Kasner} (they all vanish on Kasner)
- Cancellation by higher Weyl-polynomial operators is possible in principle but requires a specific numerical conspiracy between fixed-point couplings with no symmetry basis
- Field redefinitions cannot eliminate W₃ in 4D

**Working conclusion:** If w₃* ≠ 0 and δW₃/δg|_{Kasner} ≠ 0 (as established structurally in file 03), then Kasner is not a saddle of the AS effective action that includes W₃. The full operator basis does not automatically save Kasner, absent a specific (unmotivated) cancellation conspiracy.

**Remaining uncertainty:** Whether such a cancellation occurs at the AS fixed point is unknown. It requires knowing all fixed-point couplings simultaneously — not just w₃*.

---

*Document status: FULL OPERATOR BASIS AUDIT COMPLETE*
*No cancellation mechanism identified. Remaining uncertainty: specific numerical conspiracy between higher-order fixed-point couplings.*
*Date: August 2026*
