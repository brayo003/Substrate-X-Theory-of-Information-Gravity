# PRIMITIVE_COMPARISON
## Gate 5 Part IV (supplemental) — Comparison of Surviving Candidates

**Candidates:** P01 (Asymptotic Safety UV Fixed-Point), P06 (Constraint-Algebra Anomaly-Freedom)
**Also includes post-adversarial record for killed candidates P02, P08.**
**Authority:** DERIVATION_REQUIREMENTS.md §§1–8
**Date:** August 2026

---

## Requirement Scores

Each requirement is scored: PASS / CONDITIONAL / FAIL / UNKNOWN.

### Requirement 1 — Phase-Space Restriction
*Must derive Γ_phys ⊊ Γ_GR with all elements of Γ_phys having small Weyl curvature.*

**P01:** CONDITIONAL. β > 0 at the AS fixed point suppresses large-Weyl configurations in truncated theory space. Γ_phys ⊊ Γ_GR is conditionally established. Full-theory result absent.

**P06:** FAIL (current state). LQC shows anomaly-free Bianchi I states exist. No nontrivial restriction demonstrated on the classical initial-data space.

**P02 (killed):** FAIL. Equivalent to Einstein's equations — all GR solutions satisfy it.

**P08 (killed):** FAIL. All classical GR solutions are saddle points. No restriction within classical GR solution space.

---

### Requirement 2 — Background Independence
*Must be definable on arbitrary (h_ij, K_ij) without assuming FLRW or any preferred background.*

**P01:** CONDITIONAL PASS. The FRGE is defined on arbitrary background geometries in the background-independent formulation (Reuter-Weyer 2009). In practice, all calculations use a specific background. The concept is background-independent; the computation is not.

**P06:** PASS. The Dirac constraint algebra is defined canonically on any Cauchy surface (h_ij, π^{ij}) in the ADM formalism — inherently background-independent.

---

### Requirement 3 — Adversarial Substitution Must Fail
*A maximally pathological initial dataset (Bianchi IX, large Weyl, inhomogeneous) must NOT satisfy the primitive.*

**P01:** PARTIAL. Large-Weyl configurations at the Planck scale are suppressed by β > 0. Sub-Planckian Bianchi I and Bianchi IX are classical GR solutions and not excluded.

**P06:** FAIL. Anomaly-free Bianchi I states exist in LQC (Ashtekar-Wilson-Ewing 2009). The adversarial substitution does not fail for the most important anisotropic class.

---

### Requirement 4 — No Assumption Laundering
*The primitive definition must not contain homogeneity, isotropy, FLRW, low Weyl, or smoothness.*

**P01:** PASS. The UV fixed point G* is defined in theory space by the FRGE fixed-point condition. It does not mention geometric properties of initial data. The Weyl suppression is an output (via β > 0), not an input.

**P06:** PASS. Anomaly freedom is a condition on the quantum constraint algebra. It does not mention Weyl curvature, homogeneity, or FLRW in its definition.

---

### Requirement 5 — Consistency with Established Physics
*Must reproduce GR in the classical limit, be consistent with QFT, thermodynamics, CMB, BBN.*

**P01:** PASS. The renormalized trajectory from G* flows to classical GR at k → 0. The asymptotic safety program is explicitly designed to recover GR as its classical limit. The corrections are suppressed by powers of (k/M_Planck)². Post-inflationary cosmology (BBN, CMB) is in the classical GR regime and unaffected.

**P06:** PASS. The anomaly-free physical Hilbert space, in the semiclassical limit, reproduces the classical constraint surface of GR. Post-bounce evolution in LQC approaches standard GR cosmology for scales >> Planck.

---

### Requirement 6 — Ekpyrotic Gap Addressability
*Must either explain why the pre-contraction state was inside the ekpyrotic attractor basin, or provide an independent route to the required gravitational initial state.*

**P01:** CONDITIONAL. The AS fixed point acts at the Planck scale. If the post-bounce (or post-Planck-epoch) state that emerges from the AS-governed regime has suppressed Weyl curvature, this provides an independent route to the initial state — bypassing the need for a slow-contraction phase. Whether the AS initial state is specifically within the ekpyrotic attractor basin is not established, but it may provide an alternative to ekpyrosis rather than supplementing it.

**P06:** UNKNOWN. No established result connecting anomaly freedom to the ekpyrotic gap condition.

---

### Requirement 7 — Independent Motivation
*Must have motivation independent of R1.*

**P01:** STRONG PASS. Higgs mass prediction (confirmed), BH singularity resolution, UV completion of gravity, graviton scattering constraints.

**P06:** STRONG PASS. Mathematical consistency requirement of quantum gauge theories, critical dimension in strings, SM anomaly cancellation, LQC bounce.

---

### Requirement 8 — Distinguishable Prediction
*Must produce at least one prediction distinguishable from ΛCDM + inflation + ekpyrosis.*

**P01:** CONDITIONAL. Asymptotic safety cosmology predicts: (a) a modified scalar power spectrum at scales corresponding to k ~ M_Planck; (b) a specific tensor-to-scalar ratio if the AS fixed point is active during inflation (Platania-Wetterich 2019); (c) no trans-Planckian initial conditions problem — the spectrum has a natural UV cutoff. Whether these are distinguishable from inflation within current CMB precision is marginal; they may be distinguishable with future measurements.

**P06:** UNKNOWN. No established prediction from anomaly-freedom of the full constraint algebra for CMB observables. LQC anomaly-free models predict a modified primordial power spectrum at low ℓ (pre-bounce signature), but this is in the minisuperspace regime.

---

## Full Comparison Table

| Requirement | P01 | P06 | P02 (killed) | P08 (killed) |
|-------------|-----|-----|--------------|--------------|
| R1: Phase-space restriction | CONDITIONAL | FAIL | FAIL | FAIL |
| R2: Background independence | CONDITIONAL PASS | PASS | PASS | PASS |
| R3: Adversarial substitution fails | PARTIAL | FAIL | FAIL | FAIL |
| R4: No assumption laundering | PASS | PASS | PASS | PASS |
| R5: Consistency | PASS | PASS | PASS | PASS |
| R6: Ekpyrotic gap | CONDITIONAL | UNKNOWN | FAIL | FAIL |
| R7: Independent motivation | STRONG | STRONG | STRONG | STRONG |
| R8: Distinguishable prediction | CONDITIONAL | UNKNOWN | FAIL | FAIL |

---

## Ranking

**P01 is the strongest surviving candidate.** It is the only candidate that:
- Provides a partial derivation of Γ_phys ⊊ Γ_GR with a quantitative Weyl suppression mechanism
- Has a confirmed non-cosmological prediction (Higgs mass)
- Addresses the ekpyrotic gap via an independent Planck-scale mechanism
- Has conditional distinguishable predictions for CMB observables

**P06 is a structural requirement, not a selection mechanism.** Its independent motivation is unimpeachable (mathematical consistency), but it does not establish the required phase-space restriction. Bianchi I is not excluded. It cannot proceed to dynamics derivation without the full quantum GR result.

**Both killed candidates (P02, P08) failed because they are equivalent to GR's equations of motion and cannot restrict the GR solution space.**

---

## Critical Observation

The comparison reveals a structural divide in the survivor pool:

- **P01** acts in theory space (coupling constants) and has a mechanism for translating that restriction to initial-data space via the positive Weyl-squared coupling. The translation is incomplete but the direction is correct.
- **P06** acts in Hilbert space (quantum states) but the restriction it imposes is satisfied by all classical GR solutions studied so far.

For Gate 5 to produce a conclusion stronger than "CONDITIONAL SURVIVOR(S)", P01 would need to establish:
1. β > 0 in the full (non-truncated) theory
2. The map from the UV critical manifold to the space of low-Weyl classical initial data
3. That Bianchi I is not in the low-energy remnant of the AS-governed initial state

None of these are established. The conclusion is conditional.

---

*Document status: PRIMITIVE COMPARISON COMPLETE*
*P01: Best surviving candidate — conditional.*
*P06: Structural requirement, not a selection mechanism — conditional-weak.*
*Next: DYNAMICS_RESULTS.md*
*Date: August 2026*
