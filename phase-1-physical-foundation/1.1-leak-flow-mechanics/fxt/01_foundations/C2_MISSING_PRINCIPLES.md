# C2_MISSING_PRINCIPLES.md
## Minimum Missing Principles — C2 Substrate Project
**Version:** 1.0  
**Date:** 2026-07-24  
**Authority:** Based on all completed C2 audits  
**Purpose:** For every unresolved issue, identify the smallest additional mathematical principle that would close the gap. If no such principle exists, prove why.

**Ground rules:**
1. The current C2 mathematics is assumed correct in its entirety.
2. No redesign of C2. No new particles. No new forces.
3. Each proposed principle must be: (a) minimal, (b) non-circular, (c) mathematically precise, (d) compatible with the existing substrate.
4. If no such principle exists, a proof of non-existence is given.

---

## Problem 1 — Born Rule

**Current status:** The Born rule p = |⟨φ|ψ⟩|² is derived from Gleason's theorem *given* a complex Hilbert space. The complex Hilbert space itself is reconstructed (not derived from scratch) because M8 (complex vector space structure) is an independent input to the SCC framework.

**The gap:** The Born rule derivation is complete conditional on the Hilbert space. The gap is not the Born rule itself — it is the *origin of the complex Hilbert space* as the correct state space. Given Hilbert space ≥ dim 3, Gleason closes the gap uniquely with no free parameters.

**Is there a missing principle?** Yes.

**Smallest Missing Principle BP-1:**

> **Principle BP-1 (Local Tomography):**  
> The state of a composite system AB is completely determined by the joint probabilities of local measurements on A and B separately. Formally: for any two states ρ, σ of AB, if ⟨a ⊗ b | ρ | a ⊗ b⟩ = ⟨a ⊗ b | σ | a ⊗ b⟩ for all local product measurements a ⊗ b, then ρ = σ.

**Why BP-1 is minimal:** Local Tomography (PR5 + PR8 in the minimal origin audit) eliminates real Hilbert space quantum mechanics (real QM fails local tomography for composite systems: there exist distinct real density matrices that agree on all product measurements) and quaternionic QM (fails local tomography by the same argument). Combined with the ball state space geometry (which follows from convexity of the state space, positivity, and reproducibility), BP-1 forces ℂ-Hilbert space as the unique remaining option.

**Why BP-1 is non-circular:** BP-1 makes no reference to complex numbers, Hilbert spaces, or probability rules. It states a relation between composite and subsystem descriptions — a property about how information about parts relates to information about wholes.

**Why BP-1 is compatible with C2:** The C2 framework has composability (U3/A3) and locality (PR8) already as principles. BP-1 is a *strengthening* of locality from "no-signaling" to "full tomographic locality" — a quantitative sharpening of an existing C2 principle.

**What BP-1 does NOT fix:** BP-1 does not derive the ball geometry of the pure state space. That requires a separate principle (see Problem 4 below). BP-1 closes the Born rule gap *given* ball geometry.

**Confidence:** HIGH — BP-1 (local tomography) is the standard principle used in all known GPT reconstructions (CDP 2010, Hardy 2001, Masanes-Müller 2011). The mathematical path from BP-1 + ball geometry to ℂ-Hilbert space is a known theorem [KR].

---

## Problem 2 — Planck Constant

**Current status:** The Planck constant ℏ appears in the theory as a dimensional conversion factor between substrate units and quantum units:
- In the Lindblad master equation: Γ_φ = (4g²/ℏ²) ∫ C_JJ(τ) dτ
- In the coupling constant: g has dimensions [J·m²·s/info], and ℏ converts between energy scales.

ℏ is not derived from any current C2 result. It enters as an empirical constant.

**The gap:** ℏ sets the scale at which quantum discreteness becomes observable. In the C2 framework, all dynamics is either purely classical (PRW, transport) or quantum via independent axioms M1, M2. The ratio of classical to quantum scales is controlled by ℏ, but ℏ has no derivation.

**Is there a missing principle?** Yes.

**Smallest Missing Principle HC-1:**

> **Principle HC-1 (Quantum-Classical Scale Relation):**  
> The quantum of action ℏ is determined by the substrate correlation time τ and the characteristic substrate wave speed c through the dimensional relation:  
> ℏ = m_eff · c · ξ_c  
> where ξ_c = 2cτ is the substrate coherence length and m_eff is the effective mass scale of the smallest localized excitation of the substrate.

**Assessment of HC-1:**

HC-1 is dimensionally consistent: [ℏ] = J·s = kg·m²/s. [m_eff · c · ξ_c] = kg · (m/s) · m = kg·m²/s. ✓

However, HC-1 introduces m_eff as a new parameter — the effective mass of the smallest substrate excitation. This mass is not defined anywhere in the current C2 framework, which is a massless wave theory (the PRW has no mass). Therefore HC-1 as stated merely relocates the problem from ℏ to m_eff.

**A sharper attempt — HC-2:**

> **Principle HC-2 (Discreteness from Causal Depth):**  
> The minimum action for any distinguishable process in the CCA framework is one unit of causal entropy: ΔS_causal ≥ 1. The Planck constant ℏ is defined as the ratio of this minimum action to the substrate's characteristic angular frequency: ℏ = ΔS_min / ω_char.

**Assessment of HC-2:**

HC-2 defines ℏ operationally in terms of CCA structure (causal entropy) and substrate dynamics (ω_char). It is non-circular (no reference to QM). However, "minimum action" in the CCA is not yet established mathematically (the causal action principle, CCA-C3, is a conjecture). HC-2 is logically dependent on the unproved conjecture CCA-C3.

**Verdict:** No currently provable minimal principle for ℏ exists within C2. Both HC-1 and HC-2 require either an additional undetermined parameter (m_eff) or an unproved conjecture (CCA-C3). The Planck constant gap cannot be closed by adding a single non-circular principle to the current proved results.

**Why no principle exists (provisional proof):**

The C2 transport layer is dimensionless in structure (the telegrapher equation τ s_{tt} + s_t = c²τ ∇²s involves only the dimensionless ratio cτ/L). The quantum layer (M1, M2) introduces ℏ as an independent dimensional scale. No dimensionally consistent relation between the classical substrate scale (c, τ, substrate length) and ℏ is derivable without introducing a new mass scale or using an unproved structural theorem. Therefore, within the current proved C2 mathematics, ℏ is an irreducibly independent constant.

**Confidence:** MEDIUM — this assessment is based on current gaps; HC-2 could become valid if CCA-C3 is proved.

---

## Problem 3 — Measurement

**Current status:** The measurement problem is addressed at two levels in C2:
- At the transport level: the Q diagnostic classifies states as oscillatory (pre-measurement, coherent) or overdamped (post-measurement, decohered). This is a regime classification, not a measurement theory.
- At the quantum level: the Lindblad master equation ME-FINAL describes decoherence (off-diagonal decay) but does not explain wavefunction collapse or the selection of a definite outcome.

**The gap:** The C2 framework derives decoherence (loss of coherence in the quantum state) from the substrate. But decoherence is not the same as measurement. Measurement additionally requires:
1. That a definite outcome is obtained (not a mixture of outcomes).
2. That the outcome probability is given by Born's rule.
3. That subsequent measurements on the same system give the same outcome (repeatability).

The C2 framework addresses (2) via Gleason's theorem (conditional on Hilbert space), but not (1) and (3).

**Is there a missing principle?** Yes.

**Smallest Missing Principle M-1:**

> **Principle M-1 (Causal Outcome Selection):**  
> When a measurement interaction produces a definite record — i.e., when the measurement apparatus transitions from a causal-order-incomparable superposition to a causally ordered sequence of events — the physical outcome corresponds to a single element of the basis selected by the causal order of the measurement apparatus.

**Assessment of M-1:**

M-1 is a precise restatement of the Einselection principle (environment-induced superselection, Zurek 2003) in causal-order language. It says: the measurement basis is selected by the causal structure of the interaction (the preferred basis is the one that is causally ordered in the apparatus record).

M-1 is non-circular: it references causal order (a C2 primitive) rather than "classical states" or "macroscopic systems" (which would be circular).

M-1 is compatible with C2: the CCA has a causal partial order (Ax2) which provides exactly the causal ordering needed.

M-1 does NOT fully solve the measurement problem — it selects the basis but does not explain why a single outcome is obtained (rather than a superposition of outcomes, each occurring). This residual is the "preferred basis problem" vs. the "actualization problem." M-1 closes only the basis selection gap.

**Smallest Missing Principle M-2 (for actualization):**

> **Principle M-2 (Irreversibility = Actualization):**  
> A definite outcome is actualized when the measurement interaction is irreversible in the sense that the causal entropy H_c increases by at least 1 unit. The outcome that is actualized is the one consistent with the increased causal entropy.

**Assessment of M-2:**

M-2 connects actualization to causal entropy increase — using the causal entropy defined in the CCA framework. It is mathematically precise if the causal entropy conjecture (CCA-C3/F9) holds.

M-2 is non-circular provided H_c is defined from CCA structure, which it is (T CCA-6).

However, M-2 identifies a definite outcome with "increased causal entropy" but does not specify *which* outcome in a superposition is selected. It states that entropy increases but not which branch actualizes. This is still the hard part of the measurement problem.

**Verdict:** Two principles (M-1 + M-2) are the smallest pair that collectively close the measurement gap: M-1 selects the basis (non-circular, compatible); M-2 ties actualization to entropy increase (requires CCA-C9 conjecture, partially conditional). Neither alone is sufficient. The pair together is minimal.

**Confidence:** MEDIUM — M-1 is on solid ground; M-2 requires CCA second law (F9) to be proved.

---

## Problem 4 — Quantum Probabilities (Ball Geometry / State Space Origin)

**Current status:** The C2 framework derives the Born rule from Gleason's theorem given a complex Hilbert space. The Hilbert space is reconstructed given local tomography (BP-1, Problem 1) and a ball state space geometry. The *origin* of the ball geometry from PR1–PR10 is not established.

**The gap:** Why is the pure state space of a two-outcome quantum system a circle S¹ (Bloch equator), and the mixed state space a ball B³ (Bloch ball)? This is the "ball geometry" question.

**Is there a missing principle?** Yes.

**Smallest Missing Principle QP-1:**

> **Principle QP-1 (Continuous Reversibility):**  
> For any system satisfying PR1–PR10, the group of reversible transformations acts continuously on the state space (i.e., there is no minimal nonzero angle of rotation — the transformation group is a connected Lie group, not a discrete group).

**Assessment of QP-1:**

QP-1 (continuous reversibility) is the principle used by Masanes-Müller (2011) and related by Dakić-Brukner (2009) to derive the ball geometry. The argument: if reversible transformations act continuously on the state space, and if the state space is compact (from PR5: finite information) and convex (from PR4: reproducibility via mixtures), and if the system has the minimum non-trivial structure (2 distinguishable states), then the unique compact convex set admitting a continuous transitive group of reversible transformations on its extreme boundary (pure states) is the ball Bⁿ.

This is a known theorem [KR] (compact convex sets with transitive continuous symmetry group on extreme boundary are balls — follows from Montgomery-Samelson-Zippin theorem on compact transformation groups acting transitively on manifolds).

QP-1 is minimal: it adds only "continuous" to the existing PR6 (some transformations are invertible). It does not add complex numbers, Hilbert spaces, or any quantum postulate.

QP-1 is non-circular: continuity of the transformation group makes no reference to quantum mechanics.

QP-1 is compatible with C2: the C2 framework already has continuous structures (the SCC framework, the transport layer) and reversibility (PR6). QP-1 is a precision of how "continuously" the reversible group acts.

**Combined result with BP-1:** QP-1 + BP-1 together derive the complex Hilbert space state space, and Gleason then gives the Born rule. The complete chain is:

```
PR1–PR10 + QP-1 (continuous reversibility) + BP-1 (local tomography)
    │
    ▼
Ball state space [T via Montgomery-Samelson-Zippin + convexity]
    │
    ▼
Local tomography eliminates real and quaternionic QM [T, KR]
    │
    ▼
Complex Hilbert space [T]
    │
    ▼
Gleason's theorem: Born rule [KR]
```

**Confidence:** HIGH — QP-1 is the standard missing principle in GPT reconstructions. The mathematical chain from QP-1 + BP-1 to Born rule is established in the literature.

---

## Problem 5 — Superselection Uniqueness

**Current status:** The C2 framework, via the SCC construction, generates a Hilbert space structure and a unitary group. The state space decomposes into superselection sectors — subspaces H_α such that no coherent superposition between different sectors is physically observable. The question is whether the decomposition into sectors is unique, and whether the C2 framework selects a specific superselection structure.

**The gap:** The SCC derives *that* superselection sectors exist (from the group representation theory: irreducible representations of G decompose H into invariant subspaces). But:
1. The specific decomposition depends on the choice of G (compact symmetry group). G is not uniquely determined by C2.
2. Why physical states do not mix sectors (the superselection rule) is typically justified by a symmetry argument (Wick-Wightman-Wigner 1952), which requires the symmetry group to be a direct symmetry (not a gauge symmetry) — a distinction not made in C2.
3. The number of sectors and their physical interpretation are not derivable from C2 alone.

**Is there a missing principle?** Yes.

**Smallest Missing Principle SS-1:**

> **Principle SS-1 (Symmetry Completeness):**  
> The symmetry group G of the C2 framework is the *maximal* group of transformations consistent with the causal structure: G = Aut_causal(CCA), the group of all automorphisms of the CCA that preserve the causal order and the weight function ε.

**Assessment of SS-1:**

SS-1 defines G uniquely from the CCA structure rather than choosing G as an external input. If G = Aut_causal(CCA) is uniquely determined by the CCA axioms, then the superselection decomposition H = ⊕_α H_α is uniquely determined as the decomposition into irreducible representations of G, and the superselection rule follows from the requirement that only G-invariant states are physically preparable.

SS-1 is minimal: it adds only "maximality of G" to the existing SCC construction. It does not add new particles or forces.

SS-1 is non-circular: it defines G from structure already present in the CCA (automorphisms preserving causal order and weights).

**Key mathematical question (open):** Is Aut_causal(CCA) well-defined and computable from Ax1–Ax5? This depends on the CCA GNS theorem (F8). If F8 is proved, SS-1 becomes a well-defined and potentially computable principle.

**Confidence:** MEDIUM-LOW — SS-1 is logically sound and minimal, but its applicability depends on CCA GNS (F8, currently unproved). If F8 is proved, SS-1 has a clear path to uniqueness of superselection decomposition.

---

## Summary Table

| Problem | Smallest Missing Principle | Confidence | Reason |
|---------|--------------------------|------------|--------|
| Born Rule | BP-1: Local Tomography | HIGH | Standard GPT reconstruction; known mathematical path |
| Planck Constant | None provable currently | LOW | ℏ requires mass scale or unproved CCA-C3 conjecture |
| Measurement (basis selection) | M-1: Causal Outcome Selection | MEDIUM | Relies on CCA causal order (established); partial solution only |
| Measurement (actualization) | M-2: Irreversibility = Actualization | MEDIUM | Requires CCA second law (F9, unproved) |
| Quantum Probabilities (ball geometry) | QP-1: Continuous Reversibility | HIGH | Standard GPT principle; mathematical chain established |
| Superselection Uniqueness | SS-1: Symmetry Completeness | MEDIUM-LOW | Logically sound but requires CCA GNS (F8, unproved) |

---

## Notes on Minimality

The following pairs of principles jointly close larger gaps and cannot be individually reduced further:

**Pair (QP-1, BP-1):** Together derive the Born rule from PR1–PR10 + reversibility + locality. Neither alone suffices. QP-1 alone gives only that the state space is a ball — but which ball (real, complex, quaternionic) requires BP-1. BP-1 alone gives only that full tomography holds — but without ball geometry, the Hilbert space is not specified.

**Pair (M-1, M-2):** Together close the measurement gap (basis selection + actualization). M-1 alone selects the basis but not the outcome. M-2 alone identifies entropy increase with actualization but not which outcome. Both are needed.

The Planck constant is the only gap for which no minimal principle is currently identifiable within proved C2 results. It is the sole irreducibly empirical constant in the framework at this stage.

---

*End of C2_MISSING_PRINCIPLES.md*  
*Date: 2026-07-24*  
*All proposed principles are compatible with existing C2 mathematics.*  
*No C2 structure has been redesigned or extended beyond what the principles require.*
