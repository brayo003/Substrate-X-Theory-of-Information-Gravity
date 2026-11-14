# 10_DECISION
## Final Decision: R1 Formalization Stage

**Date:** August 2026

---

## The Four Possible Outcomes

A. R1 is mathematically well-posed and remains genuinely open.
B. R1 is well-posed only after precise mathematical reformulation.
C. R1 contains an implicit measure/state assumption that must be removed.
D. R1 is not the correct fundamental question.

---

## Decision

**Outcome B: R1 is well-posed only after precise mathematical reformulation.**

R1-original ("extremely small region of phase space") contains an implicit, undefined probability measure on Γ_GR. As established in 02_MEASURE_AUDIT.md, no canonical measure on the infinite-dimensional, gauge-redundant gravitational phase space exists that satisfies the required properties.

However, R1-original is not fundamentally misconceived. The physical intuition is correct. The reformulation R1-D removes the measure dependency while preserving the physical content:

"The correct theory of quantum gravity possesses a physical initial-data sector Γ_phys ⊊ Γ_GR such that all elements of Γ_phys have C² < C²_threshold at the Planck epoch — derived from the theory, not imported."

Under R1-D, R1 is well-posed, open, and not solvable by any known mechanism.

**Outcome C also partially applies:** The phrase "low gravitational entropy" in R1-original imports the Penrose WCH (S_grav ~ C²), which is contested. R1-D removes this. The reformulation is required.

---

## R1 Status

**R1 (final formulation R1-D): WELL-POSED and OPEN.**

The problem is genuinely open — not due to any flaw in R1's formulation (after reformulation), but because no existing theory produces Γ_phys ⊊ Γ_GR with C² restriction derived from first principles.

---

## The Final Answer to the Central Question

**"What exactly would a successful theory have to mathematically produce in order to solve the cosmological initial-state problem?"**

**The answer is an explicit mathematical object:**

A function (or functional) F: Γ_GR → {0, 1} — a selection function — satisfying:

1. **Covariance:** F is invariant under spatial diffeomorphisms (Diff(Σ)-invariant)
2. **Background independence:** F(h,K) is evaluable on any (h,K) ∈ Γ_GR without a reference background metric
3. **Firewall:** The definition of F does not contain C_{αβγδ}, homogeneity, isotropy, FLRW, or smoothness as inputs
4. **Selection:** F(h,K) = 1 if and only if C²[h,K] < C²_threshold(F), where C²_threshold is derived from the definition of F
5. **Kasner exclusion:** F(Kasner) = 0 (the most-anisotropic Kasner configuration fails F)
6. **FLRW admission:** F(FLRW) = 1 (the standard cosmological initial data satisfies F)
7. **Derivation:** F follows from a physical theory T with independent motivation outside R1
8. **Non-triviality:** {(h,K) : F(h,K) = 1} ⊊ Γ_GR strictly (not all of Γ_GR satisfies F)
9. **Prediction:** T produces at least one observational consequence distinguishable from ΛCDM + inflation + ekpyrosis

Alternatively: a quantum theory T producing a Hilbert space H with a physical subspace H_phys ⊂ H such that:
- The semiclassical configurations supported by states in H_phys have C² < C²_threshold
- C²_threshold is derived from T
- H_phys is defined without importing the desired initial state
- T makes at least one distinguishable prediction

No existing theory provides either object. The specific open calculations that could advance the state of knowledge are:

1. **C³/w₃* in AS:** Compute the fixed-point value of the C³ coupling in the asymptotic safety effective action. If w₃* ≠ 0 and δW₃/δg|_{Kasner} ≠ 0, the AS effective action has no Kasner saddle — partial progress toward the selection function F.

2. **Extended GR constraints:** Identify an independently motivated primary constraint C₀[h,K] = 0 whose Dirac algorithm closure produces secondary constraints excluding Kasner. The primary constraint must not encode Weyl suppression.

3. **Non-local condition:** Construct an integral condition ∫_Σ Q[h,K] d³x = 0 where Q is independently motivated and the condition fails for Kasner but holds for FLRW. The Cotton-York avenue was explored and failed (Kasner satisfies Y=0); other tensor integrals remain unexplored.

Until one of these three calculations produces the explicit selection function F (or its quantum analog), R1 remains open.

---

## What Is Not an Answer

The following statements are not solutions to R1 under the final formulation:

- "All known mechanisms fail, therefore [new ontology] is required." — Argument from ignorance.
- "The universe is smooth, so it must have started smooth." — Circular.
- "Path-integral weighting prefers smooth initial states." — Established but insufficient (Outcome B, O(1) weighting).
- "Quantum gravity resolves singularities." — True but does not restrict Γ_phys ⊊ Γ_GR.
- "Information-theoretic bounds require the initial state to be smooth." — Not derived; kills for encoding (P03 failure).

---

## Governance Note

This decision does not authorize:
- A new primitive sweep before the three open calculations are attempted
- Introduction of SXC-IGC as an answer on the basis of this audit
- Weakening of R1 to make existing mechanisms satisfy it

R1 (final) is the correct formulation. The problem is open. The work continues only via the three specific open calculations or via discovery of a genuinely new mathematical structure outside the surveyed domains.

---

*Document status: DECISION COMPLETE*
*Outcome B: R1 well-posed after reformulation. Genuinely open.*
*Required object: Selection function F satisfying 9 conditions, or quantum analog.*
*Date: August 2026*
