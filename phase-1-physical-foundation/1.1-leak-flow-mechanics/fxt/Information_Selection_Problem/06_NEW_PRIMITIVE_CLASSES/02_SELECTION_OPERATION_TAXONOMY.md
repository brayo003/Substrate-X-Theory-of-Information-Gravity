# 02_SELECTION_OPERATION_TAXONOMY
## What Mathematical Operations Can Select Γ_phys ⊊ Γ_GR?

**Date:** August 2026

This document catalogs all mathematically distinct selection operations, tests each against the structural requirements, and identifies which are genuinely unexplored.

The question being answered: WHAT KIND OF MATHEMATICAL STRUCTURE CAN DERIVE Γ_phys ⊊ Γ_GR WITHOUT ENCODING LOW WEYL IN ITS DEFINITION?

---

## Preliminaries: What Γ_GR Is

Γ_GR is the space of initial data (h_ij, K_ij) on a 3-manifold Σ satisfying the GR constraint equations:
- Hamiltonian constraint: H = R_Σ + K² − K_{ij}K^{ij} − 16πGρ = 0
- Momentum constraint: H_i = ∇_j(K^j_i − δ^j_i K) − 8πG J_i = 0

This space is infinite-dimensional. It includes FLRW, Kasner, Bianchi IX, Schwarzschild, and generic inhomogeneous data. R1 asks for a derivation of Γ_phys ⊊ Γ_GR.

---

## Operation Class α — Modification of the Constraint Equations

**Description:** Add a new constraint C[h,K] = 0 that is not equivalent to the existing GR constraints. The physical phase space is then:

  Γ_phys = {(h,K) ∈ Γ_GR | C[h,K] = 0}

**Requirements:**
- C must be background-independent (covariant, evaluable on any (h,K))
- C must not encode low Weyl in its definition
- C must be independently motivated
- C ≠ H or H_i (not equivalent to existing constraints)

**Status of known implementations:**
- Shape dynamics: adds conformal constraint → killed (Newtonian N-body, not GR cosmology)
- LQG physical Hilbert space: kernel of quantum constraints → includes all GR solutions (P06 failure class A)

**New potential:** A constraint derived from a fundamentally different principle — not GR dynamics, not quantum consistency, but from something like global extension conditions or discrete-to-continuum regularity. Not yet attempted.

**Structural test:** Does any known physical principle produce a new covariant constraint on (h,K) that is not equivalent to H=0, H_i=0, and that specifically excludes high-Weyl vacuum data?

**Verdict: OPEN. No such constraint known, but the operation class itself is not closed.**

---

## Operation Class β — Restriction by Functional-Analytic Condition

**Description:** The GR constraint equations (H=0, H_i=0) are a system of PDEs on Σ. Not every 3-manifold admits solutions. The conformal method (York-Lichnerowicz decomposition) decomposes initial data into free data (conformal geometry + extrinsic curvature trace-free part) and determined data (conformal factor, trace of K). The conformal factor satisfies the Lichnerowicz equation:

  ΔΨ − (R̄/8)Ψ + (K²/12)Ψ⁵ − (|σ̄|²/8)Ψ^{-7} − 2πGρΨ^{-3} = 0

For given free data (ĥ_{ij}, σ̄^{ij}, K, ρ), this equation may or may not have a positive solution Ψ > 0. If it does not, the initial data is not in Γ_GR.

**The question for R1:** Does the Lichnerowicz equation have fewer positive solutions for high-Weyl free data than for low-Weyl free data? If so, high-Weyl configurations would be excluded from Γ_GR more severely, producing a de facto restriction.

**Known results:** Choquet-Bruhat (1952), Isenberg (1995): the Lichnerowicz equation has a positive solution under certain conditions on the Yamabe class of the conformal metric. High-curvature conformal metrics (large Weyl) may be in different Yamabe classes. However, the relevant question is whether the exclusion is specifically of high-Weyl data. The answer is not known.

**Critical test:** Is there a high-Weyl free conformal datum (ĥ_ij with large C̄) for which the Lichnerowicz equation has no positive solution? Kasner conformal class: flat R³ with anisotropic scaling — the Yamabe class of Kasner is the positive Yamabe class (since Kasner conformally maps to flat space), so Ψ exists. Kasner is not excluded by the Lichnerowicz equation.

**Verdict: Kasner survives functional-analytic constraint. This operation does not produce the required restriction for Kasner specifically, though it may restrict more extreme configurations.**

---

## Operation Class γ — Selection by Global Inextendibility / Completeness

**Description:** In classical GR, some initial data leads to geodesically complete spacetimes and some does not (singularity theorems). The set of initial data that produces a geodesically complete (or globally hyperbolic, maximally extended) spacetime is a subset of Γ_GR. Call this Γ_complete ⊊ Γ_GR.

**Does Γ_complete favor low-Weyl initial data?**

Known results:
- Penrose singularity theorem: data with a trapped surface produces geodesic incompleteness.
- BKL conjecture: generic initial data near a cosmological singularity (including Kasner) leads to a spacelike singularity. Kasner IS geodesically incomplete (it has a spacelike singularity at t=0).
- FLRW: also geodesically incomplete (the big bang singularity).

So both FLRW and Kasner are geodesically incomplete. This operation does not distinguish them.

However: in the context of a bouncing cosmology or quantum gravity singularity resolution, the question becomes: which initial data can be extended through a quantum gravity regime into a non-singular spacetime? This is a different operation — extension through quantum gravity rather than classical completeness.

**This is Operation Class γ' — Quantum Extension Completeness.** Does every GR initial-data set admit a quantum gravity completion, or only a restricted subset? Not known.

**Verdict for classical completeness: Does not select low-Weyl over Kasner (both are incomplete). Quantum extension completeness is genuinely unexplored.**

---

## Operation Class δ — Selection by Dirac Observable / Relational Structure

**Description:** In canonical GR, the physical observables are Dirac observables — functions on Γ_GR that commute with all constraints. The space of Dirac observables may have a different structure than Γ_GR itself. Specifically: can two distinct initial-data sets (h₁,K₁) and (h₂,K₂) have identical Dirac observables? If yes, they are gauge-equivalent. If the gauge orbits group Bianchi I with FLRW (different Dirac observables), they are physically distinct.

**Can this select low-Weyl initial data?**

Dirac observables include the ADM energy, momentum, and all gauge-invariant local quantities. The Weyl tensor is gauge-invariant (under diffeomorphisms). So Weyl curvature IS a Dirac observable (in principle). The Dirac observable space does not reduce the initial data space below the constraint surface — it is equivalent to Γ_GR modulo diffeomorphisms.

**Verdict: Dirac observable structure is equivalent to Γ_GR/Diff. This does not select a proper subset of GR physics. Does not help with R1.**

---

## Operation Class ε — Discrete-to-Continuum Regularity Conditions

**Description:** If the fundamental description of spacetime is discrete (causal sets, spin foams, group field theory), the continuum limit may exist only for configurations satisfying specific regularity conditions. A coarsening-to-continuum procedure (analogous to taking a thermodynamic limit) may produce a FLRW-like result only for initial configurations satisfying certain uniformity conditions.

**Key question:** Do highly inhomogeneous discrete configurations (corresponding to high-Weyl initial data in the continuum) have a well-defined continuum limit? If not, they are not in Γ_phys even though they would be in Γ_GR.

**Status:**
- Causal set theory: the continuum limit (Hauptvermutung) exists only for sprinklings of causal sets from a Lorentzian manifold. But every Lorentzian manifold (including Kasner) can be sprinkled — no restriction on Weyl curvature follows.
- CDT (Causal Dynamical Triangulations): the continuum limit exists in phase C (de Sitter-like). Other phases correspond to different continuum limits or no continuum limit. But CDT restricts to S³ topology and specific coupling regimes — already killed (P09, failure class F).
- Group field theory (GFT): the "condensate cosmology" in GFT (Oriti et al.) produces an effective Friedmann equation from a GFT condensate state. But the condensate state is a specific quantum state of the GFT field — it corresponds to a specific initial condition for the discrete theory. This is a quantum state input (failure class C).

**Assessment:** No existing discrete theory demonstrates that high-Weyl continuum configurations are excluded from the continuum limit without the exclusion arising from a topological, domain, or state-selection input.

**Verdict: Not established. The operation class is legitimate but no mechanism implements it without running into failure classes F or C.**

---

## Operation Class ζ — Symplectic/Geometric Quantization Conditions

**Description:** The phase space Γ_GR carries a symplectic structure ω (the Liouville form on the cotangent bundle of the space of 3-metrics). Geometric quantization requires:
1. Prequantum line bundle: the symplectic form must be integral (ω ∈ H²(Γ_GR, ℤ) in appropriate sense).
2. Polarization: a choice of half the phase-space directions as "positions."
3. Metaplectic correction.

The quantizable subspace of classical phase space may be restricted by integrality conditions on the symplectic form.

**Does this restrict to low-Weyl initial data?**

In GR, the symplectic form is ω = ∫Σ δπ^{ij} ∧ δh_{ij} d³x (schematically). The integrality condition from geometric quantization requires ω/ℏ to have integer periods over 2-cycles in Γ_GR. For the infinite-dimensional phase space of GR, this is a formal statement whose implications have not been worked out.

In LQG, geometric quantization of the connection formulation produces the kinematic Hilbert space L²(Ā, dμ_AL) where Ā is the space of generalized connections and dμ_AL is the Ashtekar-Lewandowski measure. This is a specific quantization choice that produces the LQG Hilbert space. The question is whether this quantization procedure restricts the physical initial-data space.

**The Ashtekar-Lewandowski measure:** The AL measure is the unique diffeomorphism and gauge-invariant measure on Ā. It treats all connections on equal footing — no preference for smooth or low-curvature connections. The kinematic Hilbert space includes states corresponding to all of Γ_GR. No restriction on Weyl curvature follows from the AL measure alone.

**Verdict: Geometric quantization does not restrict to low-Weyl initial data in any known formulation. This operation class appears closed.**

---

## Operation Class η — Constraint-Propagation Stability

**Description:** The GR constraints H=0, H_i=0 must be preserved under time evolution (constraint propagation). In classical GR, this is automatic (the constraint algebra is first-class). In quantum gravity, or in modified gravity with additional constraints, constraint propagation may fail for some initial data.

**New potential:** In a theory with additional constraints beyond H and H_i (e.g., from quantum gravity corrections), the constraint-propagation condition (the requirement that the new constraint is preserved under the new Hamiltonian flow) generates secondary constraints. The full set of constraints may exclude some initial data.

This is the Dirac algorithm applied to extended gravity. The question is whether the Dirac algorithm for any independently motivated extension of GR produces secondary constraints that specifically exclude high-Weyl initial data.

**Test against Kasner:** For Kasner, the primary GR constraints are satisfied. Any secondary constraint from a specific modification of GR may or may not be satisfied by Kasner, depending on the modification. This is a calculational question that depends on the specific extension.

**Assessment:** This is a genuinely open operation class. It requires specifying an independently motivated extension of GR's constraints and computing the Dirac algorithm. The result depends on the specific extension.

**Verdict: OPEN. Not excluded in principle. Requires a specific physical extension of GR's constraint structure.**

---

## Summary: Available vs Closed Operation Classes

| Class | Description | Status for R1 |
|-------|-------------|---------------|
| α | New covariant constraint | OPEN — no known implementation |
| β | Functional-analytic (Lichnerowicz) | CLOSED — Kasner has positive conformal factor |
| γ | Classical geodesic completeness | CLOSED — FLRW and Kasner both incomplete |
| γ' | Quantum extension completeness | OPEN — genuinely unexplored |
| δ | Dirac observables / relational | CLOSED — equivalent to Γ_GR/Diff |
| ε | Discrete-to-continuum regularity | OPEN in principle, no mechanism without F or C failures |
| ζ | Geometric quantization | CLOSED — AL measure includes all of Γ_GR |
| η | Constraint-propagation stability | OPEN — requires specific extension of GR constraints |

**Three genuinely open operation classes remain: α, γ', η.**

The most promising for R1 is **η (constraint-propagation stability for extended GR)** — it is closest to existing physics, most tractable, and has the clearest path to a calculation.

**γ' (quantum extension completeness)** is conceptually interesting but requires non-perturbative quantum gravity that does not exist.

**α (new covariant constraint)** is the most powerful but requires identifying an independently motivated physical principle that generates such a constraint.

---

*Document status: SELECTION OPERATION TAXONOMY COMPLETE*
*Open operation classes: α, γ', η*
*Date: August 2026*
