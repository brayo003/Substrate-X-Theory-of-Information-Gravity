# 10_FINAL_VERDICT
## Cubic Weyl / W₃ in Asymptotic Safety — Final Verdict

**Date:** August 2026

---

## Required Answer to Each of the 10 Questions

**Q1. Is w₃* known?**

NO. The fixed-point value of the coefficient of W₃ = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ} in the
AS effective action has not been computed in any published paper (02_W3_LITERATURE_AUDIT.md).
The AS truncation literature has reached quadratic Weyl (C²) and some 6th-order
derivative-Weyl operators (C□C), but the pure cubic-Weyl sector has not been computed.

**Q2. Is w₃* nonzero?**

UNKNOWN. No symmetry forbids it (the cubic Weyl operator is a genuine independent operator in
the 4D basis, not removable by any field redefinition or Gauss-Bonnet identity). No symmetry
requires it to vanish. The value could be zero or nonzero — genuinely unresolved.

**Q3. What is δW₃/δg on Kasner?**

NOT YET RIGOROUSLY CALCULATED. File 03 gives a structural argument (E·E·E products nonzero
for anisotropic Kasner; no algebraic identity makes E³ ∝ identity; ∇C terms nonzero). But
"generically nonzero" is a heuristic conclusion, not a closed-form computation. The explicit
variation has not been carried out.

**This is the first gate, not the second.** δW₃/δg|_{Kasner} must be computed in closed form
before spending any effort on the FRGE. If the variation vanishes — even by a mechanism not
yet identified — there is no reason to compute w₃*. The corrected calculation order is:

  Gate 1: Compute δ(√g W₃)/δg^{μν}|_{Kasner} explicitly (12_W3_VARIATION_EXPLICIT.md)
  Gate 2: If nonzero, compute w₃* via FRGE (13_FRGE_TRUNCATION_SPEC.md)
  Gate 3: If w₃* ≠ 0, check operator mixing cancellation
  Gate 4: Prediction problem (structural, independent of Gates 1–3)

**Q4. Does Kasner remain a saddle?**

CONDITIONALLY NOT: if w₃* ≠ 0, Kasner fails the saddle condition. The only live adversarial
route by which Kasner could survive despite w₃* ≠ 0 is operator mixing (Route K4,
05_KASNER_ADVERSARIAL_TEST.md): a specific numerical conspiracy between higher-order
fixed-point couplings could in principle cancel the w₃* contribution on Kasner. This
requires knowing all fixed-point couplings simultaneously — not yet computed. Kasner survival
routes K1 (W₃=0 on Kasner), K2 (algebraic identity), and K3 (derivative cancellation) are
all killed.

**Q5. Does the full operator basis change the answer?**

POTENTIALLY, VIA OPERATOR MIXING ONLY. All Ricci-based operators vanish on Kasner and cannot
cancel the W₃ contribution. The only operators that could cancel it are higher Weyl-polynomial
operators (quartic, quintic Weyl, etc.). Such a cancellation would require a specific numerical
relationship between the fixed-point couplings w₃*, w₄*, ... with no symmetry basis.
No field redefinition eliminates W₃ in 4D (04_FULL_OPERATOR_BASIS_AUDIT.md).

**Q6. Does the mechanism produce restriction or only weighting?**

IF ESTABLISHED: RESTRICTION (Outcome A). The mechanism does not merely weight Kasner less
— it excludes Kasner from the solution set of δΓ_AS/δg = 0. If the argument extends to all
high-Weyl vacuum solutions (which have B_{μν}=0 by virtue of being vacuum), then Γ_phys is
exactly the set of C=0 vacuum initial data — a hard restriction. This is a stronger result
than the C² weighting, which was Outcome B (08_PHASE_SPACE_IMPLICATION.md).

**Q7. Does it satisfy the firewall?**

PASSES STRUCTURALLY. The derivation chain can be written with abstract symbols without
importing low-Weyl curvature as an input (07_FIREWALL_AUDIT.md). The W₃ operator is
independently defined in theory space via the RG flow from the UV fixed point. The
critical condition: w₃* must be computed from the FRGE (the functional renormalization
group equation), not assumed nonzero because the mechanism needs it. If w₃* is assumed,
the firewall fails at step (3). If computed independently, it passes.

**Q8. Does it admit FLRW?**

YES. FLRW has C_{αβγδ} = 0 exactly (conformally flat). Therefore W₃|_{FLRW} = 0 and
δW₃/δg|_{FLRW} = 0. FLRW is a saddle of Γ_AS regardless of w₃*. Near-FLRW perturbations
are suppressed by O(δg)² from the W₃ term — completely negligible for CMB-level perturbations
(06_FLRW_ADMISSION_TEST.md).

**Q9. Does it actually advance R1?**

CONDITIONALLY, WITH A CRITICAL UNRESOLVED STEP AND A STRUCTURAL FAILURE. The mechanism
advances R1 along the chain from file 08 IF w₃* ≠ 0, IF no operator mixing cancellation
occurs, and IF the explicit variation calculation confirms the structural argument. However,
even if all these conditions are met, condition 9 of the selection function F (distinguishable
prediction) is NOT satisfied: the mechanism produces no observational prediction distinguishable
from inflation by any currently feasible measurement (09_PREDICTION_IMPLICATION.md).

Therefore: the W₃/AS mechanism advances R1 in the restricted sense of closing the
theoretical gap (excluding Kasner from Γ_phys), but does not close R1 completely because
it fails the prediction condition.

**Q10. What is the single mathematically decisive next calculation if R1 remains open?**

**Gate 1 (immediate):** Compute δ(√g W₃)/δg^{μν} in closed form on the Kasner metric,
explicitly separating algebraic and derivative contributions. This removes the current
"generically nonzero" structural argument and replaces it with a rigorous result.
See 12_W3_VARIATION_EXPLICIT.md.

If Gate 1 shows the variation vanishes: the W₃ route is eliminated. No FRGE work needed.
Proceed to extended constraint algebra (Route 2).

If Gate 1 confirms nonzero: proceed to Gate 2.

**Gate 2 (conditional on Gate 1):** Compute β_{w₃} = μ ∂w₃/∂μ via FRGE (Wetterinck
equation) for metric gravity, extending the truncation to include W₃. Extract w₃* from
β_{w₃}(w₃*, g*, λ*) = 0. See 13_FRGE_TRUNCATION_SPEC.md for the minimal truncation.

If w₃* = 0: mechanism eliminated. Proceed to Route 2.
If w₃* ≠ 0: proceed to Gate 3.

**Gate 3 (conditional on Gate 2):** Determine whether operator mixing at the fixed point
produces a cancellation of the w₃* contribution on Kasner (adversarial route K4).

**Gate 4 (structural, independent):** Address the prediction problem — identifying an
observable consequence that distinguishes the mechanism from ΛCDM + inflation.

---

## Verdict Assessment

The required chain (from the mission brief), with corrected gate ordering:

  δW₃/δg|_{Kasner} ≠ 0                                  ← GATE 1: NOT YET RIGOROUSLY CALCULATED
        ↓
  w₃* ≠ 0                                               ← GATE 2: UNRESOLVED (conditional on Gate 1)
        ↓
  No operator-mixing cancellation on Kasner              ← GATE 3: OPEN (adversarial route K4)
        ↓
  Kasner fails the full effective-action saddle equation  ← FOLLOWS IF GATES 1–3 PASS
        ↓
  Kasner is excluded from the relevant physical sector    ← FOLLOWS IF ABOVE
        ↓
  The resulting Γ_phys is demonstrably smaller than Γ_GR ← FOLLOWS IF ABOVE
        ↓
  The surviving sector is demonstrably low-Weyl           ← STRUCTURALLY YES (C=0 sector)
        ↓
  Firewall passes                                         ← PASSES IF w₃* FROM FRGE
        ↓
  Independently motivated prediction exists               ← GATE 4: FAILS (inflation erasure)

The chain has four open gates. Gate 1 (the variation calculation) is the cheapest and
gates all downstream computation. It should be done first.

**Note on the previous ordering:** The prior version of this document listed w₃* as the
primary blocker and the variation as secondary. That was wrong: the variation is cheaper,
is in principle resolvable by symbolic computation alone, and if it vanishes makes w₃*
irrelevant. Corrected per review.

**Three independent uncertainties (not two):**

1. δW₃/δg|_{Kasner} = ? (not yet rigorously calculated)
2. w₃* = ? (not yet computed in AS literature)
3. Operator-mixing cancellation possible (adversarial route K4, not yet ruled out)

Plus the structural prediction failure (Gate 4) which is independent of all three.

---

## VERDICT

**D — UNRESOLVED CALCULATION**

Three mathematical uncertainties (Gates 1–3) and one structural failure (Gate 4) prevent
establishment or elimination of the mechanism.

Gate 1 (variation calculation) is the correct starting point. It is cheaper than the FRGE,
it is in principle resolvable by symbolic tensor algebra alone, and it gates all subsequent
work. If it fails, the entire route collapses at zero cost to the w₃* effort.

The mechanism is NOT eliminated. But it does NOT survive — "not yet calculated" is not
evidence the mechanism works.

**Upgrade path:**
- Gate 1 pass (variation ≠ 0) + Gate 2 pass (w₃* ≠ 0) + Gate 3 pass (no mixing cancel)
  → upgrade to B (Conditional Survivor), with Gate 4 (prediction) remaining open.
- All four gates resolved → upgrade to A or eliminate.

---

*Document status: FINAL VERDICT — REVISED*
*Verdict: D — UNRESOLVED CALCULATION*
*Correction: variation calculation (Gate 1) precedes w₃* computation (Gate 2).*
*Three independent mathematical uncertainties + one structural prediction failure.*
*Immediate next step: 12_W3_VARIATION_EXPLICIT.md*
*Date: August 2026*
