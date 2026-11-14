# 04_NEW_CLASS_REGISTER
## New Primitive Classes From Unexplored Operation Types

**Date:** August 2026

Derived from 02_SELECTION_OPERATION_TAXONOMY.md (open classes α, γ', η) and 03_LITERATURE_SEARCH.md.

Only classes that are mathematically distinct from the 23 killed taxonomy classes are listed. No renaming.

---

## NC-1 — Constraint-Propagation Closure for Extended Gravity

**Operation class:** η (constraint-propagation stability for extended GR constraints)

**Mathematical definition:**

Consider GR extended by an additional scalar, tensor, or algebraic constraint C[h,K] = 0 beyond H=0, H_i=0. The Dirac algorithm requires:

  {C, H[N]}|_{Γ_phys} = 0    (propagation under time evolution)

If this generates a secondary constraint C'[h,K] = 0, the process continues. The physical phase space is the intersection of all constraint surfaces:

  Γ_phys = {(h,K) ∈ Γ_GR | C = 0, C' = 0, C'' = 0, ...}

**The key question:** Is there an independently motivated extension of GR whose full constraint-propagation closure produces a secondary (or higher) constraint that specifically excludes high-Weyl vacuum initial data?

**Candidate primary constraint:** The Cotton-York tensor condition.

In 3D, the Cotton tensor C_{ij} = ε_{ikl}∇^k(R^l_j − (1/4)δ^l_j R) measures conformal curvature. In 3+1D, the Cotton-York tensor Y^{ij} = ε^{ikl}∇_k(K^j_l − (1/3)δ^j_l K) encodes the conformal properties of the extrinsic curvature.

The constraint C_Cotton[h,K] ≡ Y^{ij} − F^{ij}(h) = 0 for some independently motivated tensor F^{ij}(h) would be a new constraint. If F = 0 (Cotton-York = 0), the constraint restricts the extrinsic curvature to be conformally flat in a specific sense.

**Independent motivation:** Cotton-York = 0 is related to conformal flatness of the spatial slice in certain gauges. It appears in the York canonical decomposition and in the conformal thin-sandwich formalism. It is not postulated for R1 — it appears naturally in the canonical decomposition of GR initial data.

**Does it exclude Kasner?** The Cotton-York tensor for the Kasner metric:

  Y^{ij}[Kasner] = ε^{ikl}∇_k K^j_l (since K = K_ij = diag(H₁,H₂,H₃) and K = tr K)

For Kasner, K_ij is diagonal and constant (no spatial variation), so ∇_k K^j_l = 0 → Y^{ij} = 0 exactly.

**Critical result: Kasner satisfies Cotton-York = 0 automatically.** The constraint does not exclude Kasner. This specific implementation is killed on adversarial test.

**Revised approach:** The constraint must be on the 3-geometry h_ij, not the extrinsic curvature. The 3D Cotton tensor C_{ij}(h) measures conformal properties of the spatial metric. For Kasner: the spatial metric is ds²_Σ = t^{2p₁}dx² + t^{2p₂}dy² + t^{2p₃}dz², which is conformally flat (diagonally rescaled flat metric). The Cotton tensor of a conformally flat 3-metric is zero.

**Critical result: Kasner spatial slices are conformally flat → 3D Cotton tensor = 0.** Any constraint involving only the Cotton tensor of the spatial metric also fails to exclude Kasner.

**Assessment:** The NC-1 class is in principle open, but the natural candidates (Cotton-York, 3D Cotton) fail on Kasner because Kasner is both Ricci-flat in 4D and conformally flat in 3D. The Kasner saddle problem reappears here in a different form.

**Status: CONDITIONAL-WEAK. The operation class is valid but no specific constraint within it excludes Kasner without encoding the desired conclusion.**

---

## NC-2 — Quantum Extension Completeness

**Operation class:** γ' (quantum extension completeness)

**Mathematical definition:**

Consider the space Γ_ext ⊂ Γ_GR of initial data configurations that admit a well-defined non-singular quantum gravity extension through the Planck epoch. Formally:

  Γ_ext = {(h,K) ∈ Γ_GR | ∃ a quantum gravity state |Ψ⟩ that (a) reduces to (h,K) in the semiclassical limit, (b) has no curvature singularity in the quantum regime, (c) is consistent with a non-singular post-Planck evolution}

**The claim:** Γ_ext ⊊ Γ_GR. High-Weyl configurations may not admit a non-singular quantum extension because the Planck-scale physics (whatever it is) cannot smooth out arbitrarily large Weyl curvature — only initial configurations with sufficiently small Weyl curvature can be extended through the Planck epoch without producing a true singularity.

**What makes this different from killed classes:**
- Not a specific quantum theory (not LQC, not spin foams) — it is a condition on any quantum gravity theory
- Not a boundary condition (no-boundary) — it is a requirement that the quantum extension exists
- Not a quantum state input — the state |Ψ⟩ is the output, not the input

**Critical test on Kasner:**

Does Kasner admit a non-singular quantum extension?

In LQC, the Kasner bouncing model has been studied. The quantum evolution of Kasner in LQC produces a bounce from Kasner contraction to Kasner expansion — the singularity is resolved in the sense that the bounce occurs at finite volume. But: the post-bounce state is also a Kasner-type solution, with potentially large Weyl curvature. LQC resolves the singularity (volume → 0) but does not reduce the Weyl curvature through the bounce.

If the quantum extension of Kasner produces a Kasner-like post-bounce state, then Kasner IS in Γ_ext. NC-2 does not exclude Kasner.

**Unless:** The Weyl curvature of the post-bounce state is constrained to be below a threshold by the quantum gravity resolution mechanism. If the bounce mechanism produces a post-bounce state with Weyl ~ O(M_Planck²) or less, then only those pre-bounce Kasner configurations with Weyl below the post-bounce threshold are "extendable" in the relevant sense.

This argument would produce a conditional exclusion: Kasner configurations with Weyl >> M_Planck² are excluded from Γ_ext. But Kasner configurations with Weyl ~ O(1) Planck units are not excluded. The restriction Γ_ext ⊊ Γ_GR holds but Γ_ext still contains Kasner for typical Planck-scale Weyl values.

**Assessment:** NC-2 produces at most a Planck-scale restriction, similar to P01. It does not exclude all Kasner initial data from the physical initial-data space.

**Status: CONDITIONAL-WEAK for the same reason as P01 — Planck-scale restriction only, not a full Γ_phys ⊊ Γ_GR for the cosmologically relevant regime.**

---

## NC-3 — Relational Initial-Data Selection via Observer-Network Consistency

**Operation class:** α (new covariant constraint)

**Mathematical definition:**

In relational mechanics (Barbour-Bertotti, Mach's principle), physical observables are ratios — they are defined relative to other degrees of freedom in the universe, not absolutely. In the relational formulation of GR, the physical content is encoded in relative configurations.

A relational consistency condition: the initial data (h_ij, K_ij) must be consistent with a well-defined relational description — i.e., must admit a consistent assignment of relational observables (shape observables, complexity measures) to all sub-regions.

**The claim:** Highly inhomogeneous initial data with large Weyl curvature may not admit a consistent relational description — the relative observables may be undefined or inconsistent (e.g., infinite complexity in finite volume).

**Critical test on Kasner:**

In Kasner, the relational observables (ratios of scale factors, shape complexity) are well-defined: the shape of the Kasner configuration is determined by the ratios p₁:p₂:p₃, which are finite. The relational description of Kasner is well-defined.

**Kasner is not excluded by relational consistency.** The constraint of relational describability does not select against Kasner.

**Assessment:** NC-3 fails the adversarial test on Kasner. Relational consistency does not exclude the adversarial class.

**Status: KILLED by adversarial test on Kasner.**

---

## NC-4 — Conformal Completion Existence

**Operation class:** α (new covariant constraint)

**Mathematical definition:**

A spacetime (M,g) admits a conformal completion (Penrose compactification) if it can be embedded as an open subset of a conformally compact spacetime (M̂, ĝ) with ĝ = Ω²g for a smooth conformal factor Ω vanishing on the boundary ∂M̂. For de Sitter and FLRW spacetimes, conformal completions exist (they have smooth I^+). For Kasner, the situation is different.

**Kasner conformal completion:** The Kasner singularity at t=0 is a spacelike singularity where Ω → 0 too rapidly for the conformal factor to be smooth. The conformal completion of Kasner near the singularity is not smooth — the curvature diverges in a way that is not conformally regularizable.

For FLRW (de Sitter): the conformal factor Ω = a(t) (scale factor) vanishes at t=0 as Ω ~ t^α for some α > 0. The conformal structure at the initial singularity can be made smooth if α → 0 (conformal flatness of de Sitter at I^−).

**The proposed constraint:** Physical initial data is required to be compatible with a spacetime that admits a smooth conformal completion at the initial singularity. Kasner does not satisfy this.

**Critical assessment:**

This is exactly Penrose's Weyl curvature hypothesis formulated in terms of conformal completion: initial singularity has Weyl = 0 ↔ smooth conformal completion. The two conditions are equivalent. Therefore this constraint ENCODES the desired conclusion — it is the Weyl curvature hypothesis restated in conformal geometry language.

**Firewall test: FAILS (failure class I — direct conclusion encoding).** The smooth conformal completion condition is equivalent to low Weyl at the initial singularity. Restating Penrose's hypothesis in different mathematical language does not constitute a derivation of it.

**Status: KILLED by firewall — assumption laundering via conformal geometry language.**

---

## NC-5 — Nonsingular Hamiltonian Flow Existence

**Mathematical definition:**

Consider the Hamiltonian flow on Γ_GR generated by the GR Hamiltonian (in some gauge/clock choice). For some initial data configurations, the flow extends for all time (global existence). For others, it terminates at a singularity in finite Hamiltonian time. Define:

  Γ_global = {(h,K) ∈ Γ_GR | the Hamiltonian flow from (h,K) exists for all Hamiltonian time}

**Does Γ_global ⊊ Γ_GR select low-Weyl initial data?**

Known results:
- FLRW: Hamiltonian flow terminates at t=0 (big bang singularity). NOT in Γ_global.
- Kasner: Hamiltonian flow also terminates at t=0. NOT in Γ_global.
- Minkowski space: trivially in Γ_global.

Both FLRW and Kasner fail the Γ_global condition (both have classical singularities). The condition does not distinguish them — it excludes both.

**Status: KILLED. The global existence condition excludes FLRW and Kasner equally. Does not select low-Weyl over high-Weyl within singular cosmological initial data.**

---

## Register Summary

| Class | Operation type | Kasner test | Firewall | Status |
|-------|---------------|-------------|----------|--------|
| NC-1 | η (constraint propagation) | FAILS — Cotton = 0 on Kasner | Passes | CONDITIONAL-WEAK |
| NC-2 | γ' (quantum extension) | FAILS — LQC bounces Kasner | Passes | CONDITIONAL-WEAK |
| NC-3 | α (relational consistency) | FAILS — Kasner has finite relational observables | Passes | KILLED adversarial |
| NC-4 | α (conformal completion) | Would exclude Kasner | FAILS — encodes Weyl=0 | KILLED firewall |
| NC-5 | (global Hamiltonian flow) | FAILS — FLRW also excluded | Passes | KILLED adversarial |

**No new primitive class survives both the adversarial test and the firewall.**

NC-1 and NC-2 survive the firewall but fail to exclude Kasner. They achieve at most Planck-scale restriction (same structural problem as P01).

---

*Document status: NEW CLASS REGISTER COMPLETE*
*No new class survives both adversarial test and firewall.*
*NC-1 and NC-2 are conditional-weak (same structural obstruction as P01).*
*Date: August 2026*
