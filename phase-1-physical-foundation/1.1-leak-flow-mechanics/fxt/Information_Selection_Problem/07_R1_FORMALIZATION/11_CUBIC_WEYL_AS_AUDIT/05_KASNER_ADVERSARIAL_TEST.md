# 05_KASNER_ADVERSARIAL_TEST
## Active Search for Why Kasner Might Survive W₃

**Date:** August 2026

This file actively seeks reasons Kasner survives despite W₃ — adversarial, not confirmatory.

---

## Route K1: Special Kasner Values Where W₃ = 0

W₃ = 0 when all p_i = 1/3 (the isotropic Kasner = flat Minkowski in disguise). This is the FLRW limit, not a Kasner solution with anisotropy.

For generic anisotropic Kasner: W₃ ≠ 0. The only Kasner parameters with W₃ = 0 are the isotropic case p₁=p₂=p₃=1/3, which cannot satisfy the Kasner constraints (Σp_i² = 1 requires Σ(1/3)² = 1/3 ≠ 1). Therefore NO anisotropic Kasner has W₃ = 0.

**Route K1 fails: no adversarial Kasner with W₃ = 0 (except the degenerate isotropic case which is not Kasner).**

---

## Route K2: δW₃/δg = 0 by Algebraic Identity

Could the specific Kasner geometry satisfy an identity making the variation vanish?

For purely electric Weyl (B_{ij} = 0, which holds for Kasner), the variation δI₁/δg could potentially simplify. The electric Weyl E_{ij} is traceless and symmetric. The condition δW₃/δg = 0 would require:

  E_{μα}E^α_{\ β}E^β_{\ ν} = (W₃/4) g_{μν}   (schematic)

This is the condition that E³ is proportional to the identity. For a diagonal traceless matrix E = diag(a, b, c) with a+b+c=0 and a²+b²+c²=σ²:

  (E³)_{ii} = a³, b³, c³   (no sum)

For this to be proportional to the identity: a³ = b³ = c³ = σ³/3. With a+b+c=0, the only solution is a=b=c=0 (isotropic). So E³ ∝ identity only in the isotropic case.

**Route K2 fails: E³ is not proportional to identity for any anisotropic Kasner.**

---

## Route K3: Derivative Terms Cancel Algebraic Terms

The full variation P_{μν} = P^{alg}_{μν} + P^{der}_{μν}. If P^{der}_{μν} = −P^{alg}_{μν}, then P_{μν} = 0 on Kasner.

This would require a specific relationship between the time-derivative structure of the Kasner metric and the algebraic Weyl contractions. For Kasner, both P^{alg} and P^{der} have power-law time dependence ~ t^{−6}. Their spatial components are determined by the Kasner anisotropy parameters p_i.

For the cancellation to occur: the p_i would need to satisfy a specific polynomial equation derived by setting P^{alg} + P^{der} = 0. This is not the Kasner constraint (Σp_i = 1, Σp_i² = 1) — it would be a DIFFERENT constraint. Since the Kasner space is 2-dimensional in anisotropy parameters (after imposing the two Kasner constraints), and the cancellation equation is an additional constraint, generically NO Kasner solution satisfies it (it would be an isolated point or empty set, not the entire Kasner family).

**Route K3 fails generically: the derivative and algebraic terms do not cancel for the full Kasner family.**

---

## Route K4: W₃ Contribution Absorbed Into a Redefinition of w₃*

Could the coefficient w₃* effectively vanish because the W₃ operator mixes with other operators under the RG flow, and at the fixed point the physical combination is zero?

This is the operator mixing question. Under the RG, operators mix. The "physical" coupling is a specific linear combination of bare couplings. If the physical combination that appears in the equation of motion has a zero fixed-point value even when individual operator couplings are nonzero, this would be a more subtle cancellation.

This requires knowing the full fixed-point structure including operator mixing — which has not been computed. This is a genuine uncertainty that cannot be resolved without the computation.

**Route K4: GENUINELY OPEN. Cannot be resolved without the full fixed-point computation including operator mixing for cubic-Weyl operators.**

---

## Route K5: A Non-Perturbative Effect Restores Kasner as a Saddle

Non-perturbative effects in the AS path integral (instantons, saddle-point contributions from topology changes) could in principle modify the saddle structure. These are not captured by the truncated effective action.

This is a theoretical possibility with no specific mechanism. It cannot be evaluated without non-perturbative control of the AS path integral.

**Route K5: SPECULATIVE. Not a live calculation.**

---

## Summary of Kasner Survival Routes

| Route | Status |
|-------|--------|
| K1: W₃ = 0 on Kasner | KILLED — no anisotropic Kasner has W₃ = 0 |
| K2: δW₃/δg = 0 by algebraic identity | KILLED — requires E³ ∝ identity, impossible for anisotropic E |
| K3: Derivative terms cancel algebraic | KILLED generically — would require a non-Kasner constraint |
| K4: Operator mixing absorbs w₃* | OPEN — requires full fixed-point computation |
| K5: Non-perturbative restoration | SPECULATIVE — no mechanism |

**The only live adversarial route is K4 (operator mixing).** This is a genuine uncertainty that must be marked as unresolved.

---

*Document status: KASNER ADVERSARIAL TEST COMPLETE*
*Only Route K4 (operator mixing) is live. All others killed.*
*Date: August 2026*
