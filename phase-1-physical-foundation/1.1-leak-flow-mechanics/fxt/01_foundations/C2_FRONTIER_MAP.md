# C2_FRONTIER_MAP.md
## Research Frontier Map — C2 Substrate Project
**Version:** 1.0  
**Date:** 2026-07-24  
**Authority:** Based on all completed C2 audits  
**Purpose:** Identify every remaining mathematical frontier, assess its status, rank it, and show the dependency graph between unresolved problems.

**Status key:** SOLVED-ELSEWHERE | IMPOSSIBLE | UNKNOWN | NEEDS-NEW-AXIOM | NEEDS-NEW-FIELD | NEEDS-NEW-OBSERVABLE | CHANGES-PREDICTION

---

## Preamble

Every completed result from the C2 audits is treated as established in this document. The frontier consists exclusively of what is not yet proved, not yet disproved, and not yet reducible to existing mathematics. For each frontier problem we answer seven questions and then rank the problem.

---

## Part I — Frontier Problem Catalogue

### F1 — Derivation of Microscopic Reversibility (PA1)

**Statement:** Prove that the dynamical evolution map φ: S → S must be invertible, from physically unavoidable principles R1–R7 alone (without assuming AA2: evolution commutativity).

**Seven-Question Analysis:**

1. **Already solved in literature?** No. The Stinespring dilation theorem shows that any CPTP map on a subsystem can be dilated to a unitary on a larger system — but this operates *within* an already-assumed Hilbert space. The problem of deriving invertibility from pre-quantum operational principles without assuming a Hilbert space is not solved anywhere.

2. **Known to be impossible?** No impossibility proof exists. Counterexamples showing irreversibility can be consistent with R1–R6 (classical dissipation) show that R7 is independent, but do not show that R7 is *unjustifiable*.

3. **Merely unknown?** Yes — this is the current status. The derivation has been blocked but not proved impossible.

4. **Requires a new axiom?** Possibly. Route A requires AA2 (evolution commutativity); AA2 is itself not derived. A new axiom replacing AA2 with something more primitive might work.

5. **Requires a new field?** No. The question is internal to operational probability theory and category theory. No new mathematical field is needed — a new proof technique within existing frameworks may suffice.

6. **Requires a new observable?** No. This is a purely mathematical derivation question.

7. **Would solving it change any physical prediction?** Yes — indirectly. If PA1 is derived from R1–R6 alone, it would close the foundational gap in SCC and confirm that the framework has one fewer independent axiom. It would not change numerical predictions but would strengthen the foundational justification.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 5 | Closes the central foundational gap in SCC |
| Mathematical difficulty | 4 | Several routes attempted and failed |
| Dependence on prior results | 2 | Does not depend on any open C2 result |
| Likelihood of being solvable | 3 | No impossibility proof; techniques partially developed |

---

### F2 — Origin of the Ball State Space Geometry

**Statement:** Derive from PR1–PR10 that the pure state space of a physical system is a ball Bⁿ (rather than some other convex body).

**Seven-Question Analysis:**

1. **Already solved in literature?** Partially. Hardy's (2001) reconstruction derives "quantum-like" state spaces from five axioms; Chiribella-D'Ariano-Perinotti (CDP, 2010) derives ℂ-Hilbert space from informational axioms including Purification and Transitivity. But the *origin* of Purification and Transitivity from weaker principles is not solved.

2. **Known to be impossible?** No.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** A principle replacing Purification and Transitivity with something more primitive would qualify. Not clear if such a principle exists.

5. **Requires a new field?** No. Convex geometry, GPT framework, and operational probability theory suffice.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Yes. If the ball geometry is derived, then complex Hilbert space is derived without independent assumption, making quantum mechanics a mathematical theorem of the foundational framework. This would resolve the strongest unresolved question in quantum foundations.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 5 | Most important open problem in quantum reconstruction |
| Mathematical difficulty | 5 | Has resisted solution for 25 years (Hardy 2001 onward) |
| Dependence on prior results | 2 | Requires clean GPT framework only |
| Likelihood of being solvable | 2 | Progress exists but complete solution absent |

---

### F3 — Derivation of Purification from Weaker Principles

**Statement:** Prove that Purification (every mixed state is a marginal of a pure joint state) follows from physically unavoidable principles without assuming it directly.

**Seven-Question Analysis:**

1. **Already solved in literature?** No. All known reconstructions of QM from GPT axioms (Hardy, CDP, Masanes-Müller, Dakić-Brukner) either assume Purification directly or use axioms equivalent to it.

2. **Known to be impossible?** No impossibility proof.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** Possibly a weaker substitute (e.g., a probabilistic form of Purification — "approximate purification" — might be derivable). No such substitute is known.

5. **Requires a new field?** No.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Indirectly. Deriving Purification from weaker principles would tighten the logical foundation of QM without changing numerical predictions.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 4 | Key axiom in all known QM reconstructions |
| Mathematical difficulty | 5 | Resisted solution in GPT framework since CDP 2010 |
| Dependence on prior results | 2 | Fairly independent |
| Likelihood of being solvable | 2 | No clear attack strategy currently known |

---

### F4 — Lorentz Group Derivation

**Statement:** Derive SO(3,1) as an internal symmetry from any C2 candidate (CCA, SCC, C1–C5) without assuming Lorentz invariance.

**Seven-Question Analysis:**

1. **Already solved in literature?** In causal set theory (Bombelli-Lee-Meyer-Sorkin 1987), Lorentz invariance emerges *statistically* in the large-N limit — but this is a conjecture, not a theorem. In algebraic QFT, Lorentz covariance is an axiom (Haag-Kastler axioms), not derived. In causal dynamical triangulations (CDT), approximate Lorentz symmetry appears numerically. No rigorous derivation from first principles exists.

2. **Known to be impossible?** No. The Malament theorem shows causal order determines the conformal structure; a separate volume measure determines the scale. This provides a partial derivation path: causal order + volume → Lorentzian geometry (up to conformal factor). Full Lorentz group emergence from discrete causal sets is unproved but not known to be blocked.

3. **Merely unknown?** Yes — this is the status of the causal set conjecture.

4. **Requires a new axiom?** Possibly. The continuum limit of a causal set requires a "manifoldlike" faithfulness condition — an additional postulate on the density of embedding.

5. **Requires a new field?** Possibly. A rigorous proof of the causal set continuum limit likely requires new results in random geometry or stochastic differential geometry — areas at the boundary of existing mathematics.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Significantly. Deriving Lorentz symmetry from C2 foundations would imply that special relativity is not an independent postulate but a consequence of causal-compositional structure. This is a paradigm-level result.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 5 | Derives special relativity from first principles |
| Mathematical difficulty | 5 | Open for 40 years in causal set community |
| Dependence on prior results | 3 | Requires continuum limit (OP-16 related) |
| Likelihood of being solvable | 2 | Partial progress (Malament theorem) but full solution distant |

---

### F5 — Gauge Group Selection (Why U(1)×SU(2)×SU(3)?)

**Statement:** Derive the Standard Model gauge group from a C2 principle without assuming it.

**Seven-Question Analysis:**

1. **Already solved in literature?** No. In string theory, the SM gauge group can appear from specific compactifications, but this requires enormous additional structure (string landscape). In algebraic QFT, gauge symmetry is axiomatized (Doplicher-Haag-Roberts analysis derives that localized charges define a compact group, but the specific group is an input). No derivation from pre-quantum principles.

2. **Known to be impossible?** Not as a mathematical impossibility theorem. But the Doplicher-Haag-Roberts (DHR) analysis shows that any compact gauge group is consistent with the axioms of algebraic QFT — so consistency does not select a unique group. Selection would require additional physical input.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** Almost certainly. Something equivalent to a "uniqueness of the gauge group" principle has no known derivation. This may require a principle about the number of superselection sectors or about information capacity.

5. **Requires a new field?** Possibly. The question of why exactly three generations and why these specific gauge groups touches number theory and exceptional Lie algebras (octonions, E₈) — areas where no clear C2 connection has been established.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Enormously. Deriving the SM gauge group would mean all known particle physics follows from a single structural principle.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 5 | Derives all known particle physics forces |
| Mathematical difficulty | 5 | No known approach from C2 foundations |
| Dependence on prior results | 5 | Requires F4 (Lorentz) + QFT emergence + more |
| Likelihood of being solvable | 1 | No known approach; highly speculative |

---

### F6 — Quantum Field Theory Emergence

**Statement:** Generate QFT (renormalization, running couplings, vacuum structure, second quantization) internally from a C2 candidate.

**Seven-Question Analysis:**

1. **Already solved in literature?** Partially. Algebraic QFT (Haag-Kastler, Osterwalder-Schrader) axiomatizes QFT but does not derive it from pre-quantum principles. The OS reconstruction theorem shows that Euclidean QFT data reconstruct Minkowski QFT — but both sides are still QFT. No derivation from combinatorial, categorical, or information-theoretic primitives exists.

2. **Known to be impossible?** No — but the UV divergences of QFT (O3 obstruction) mean that any derivation of QFT from discrete/finite principles must explain how infinities arise in the continuum limit. This is understood (O3 derived from O2 + local interactions) but generating the specific structure of QFT (not just the existence of divergences) from C2 primitives is unaddressed.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** Probably. Some analog of "local covariant quantum fields" must emerge from C2 structure — this is not currently derivable.

5. **Requires a new field?** Possibly. Second quantization (Fock space construction) requires a way to go from single-particle Hilbert space to many-particle spaces; this is a new layer not addressed by any C2 candidate.

6. **Requires a new observable?** No — QFT observables (S-matrix elements, correlation functions) are defined once the framework is in place.

7. **Would solving it change any physical prediction?** Enormously. All of the Standard Model's quantitative predictions (anomalous magnetic moment, running couplings, etc.) would follow from a single microscopic principle.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 5 | Derives all of relativistic quantum field theory |
| Mathematical difficulty | 5 | Hardest open problem in mathematical physics |
| Dependence on prior results | 5 | Requires F4, F5, QM emergence, continuum limit |
| Likelihood of being solvable | 1 | No known approach from C2 foundations |

---

### F7 — Large-N Universality Forces O1 and O2

**Statement:** Prove that in any framework satisfying U1–U6 with N → ∞ interacting degrees of freedom, complex phase coherence (O1) and effective continuous field equations (O2) emerge generically.

**Seven-Question Analysis:**

1. **Already solved in literature?** Partially. The central limit theorem applied to sums of many random variables produces Gaussian distributions — a form of O2 emergence. De Finetti's theorem produces continuum parameters from infinite exchangeable sequences — partial O2 emergence. But O1 (complex structure, interference) emerging generically from large-N real-valued systems is not established.

2. **Known to be impossible?** No. Classical statistical mechanics has N → ∞ and produces O2 but not O1. This shows O1 does not follow from N → ∞ alone — additional conditions (e.g., symmetry group SO(2)) are needed.

3. **Merely unknown?** Yes — whether the additional conditions (2D state space, rotational symmetry) themselves emerge generically from large-N U1–U6 systems is unknown.

4. **Requires a new axiom?** Possibly. A new universality class theorem would be needed showing that all sufficiently complex large-N systems develop rotational symmetry in their coarse-grained description.

5. **Requires a new field?** Possibly. Classifying the universality classes of large-N systems with respect to complex structure emergence may require new techniques combining random matrix theory, ergodic theory, and topological methods.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Yes — it would upgrade the project from Result B to Result A. All of quantum mechanics would be a necessary consequence of large-N statistics, rather than an independent postulate.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 5 | The central open question of the entire project |
| Mathematical difficulty | 5 | Requires new universality theorem |
| Dependence on prior results | 1 | Independent; requires U1–U6 only |
| Likelihood of being solvable | 2 | No impossibility proof; some partial results exist |

---

### F8 — CCA GNS Representation Theorem

**Statement:** Prove that every abstract CCA is representable as a CCA of matrices with partial order given by a time-like order (the CCA analogue of the GNS theorem for C*-algebras).

**Seven-Question Analysis:**

1. **Already solved in literature?** No. The GNS theorem for C*-algebras is standard [KR]. A CCA analogue is not known.

2. **Known to be impossible?** No.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** Possibly. A separability or nuclearity condition on the CCA may be needed (analogous to separability of the Hilbert space in GNS).

5. **Requires a new field?** No. This is internal to category theory + functional analysis. New results within existing fields are likely sufficient.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Indirectly. A representation theorem would give a concrete matrix realization of every CCA, making the structure computationally accessible and enabling new derivations.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 3 | Important for CCA development, not directly physical |
| Mathematical difficulty | 3 | Analogous to known GNS result; likely solvable |
| Dependence on prior results | 1 | Independent |
| Likelihood of being solvable | 4 | Clear analogy with GNS; techniques may transfer |

---

### F9 — CCA Causal Entropy Non-Decrease (Second Law from CCA)

**Statement:** Prove H_c(B) ≥ H_c(A) for any causal evolution m: A → B in the CCA, i.e., causal entropy is non-decreasing.

**Seven-Question Analysis:**

1. **Already solved in literature?** Partially. The data processing inequality for Shannon entropy is standard [KR]: H(Tp) ≥ H(p) for doubly stochastic T. The causal entropy H_c = H + λ·r adds a topological term. Whether the combined quantity is non-decreasing under CCA morphisms requires a new proof.

2. **Known to be impossible?** No.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** Possibly a condition on the weight function ε ensuring doubly stochastic behavior. The current Ax4 requires Σε(m:A→B) = 1 in the B-direction but not necessarily in the A-direction.

5. **Requires a new field?** No.

6. **Requires a new observable?** No.

7. **Would solving it change any physical prediction?** Yes. A derivation of the second law (entropy non-decrease) from the CCA axioms alone would make thermodynamics a mathematical theorem of the foundational structure.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 4 | Derives the second law from structure |
| Mathematical difficulty | 3 | Analogous to data processing inequality |
| Dependence on prior results | 1 | Independent |
| Likelihood of being solvable | 4 | Clear strategy exists; requires new CCA lemma |

---

### F10 — Quantum Coupling Constant g

**Statement:** Derive the quantum-classical coupling constant g = [J·m²·s/info] from the substrate framework without treating it as a free parameter.

**Seven-Question Analysis:**

1. **Already solved in literature?** No. The coupling constant between a quantum system and a classical background field is always a measured input in phenomenological models. No derivation from first principles exists in any framework.

2. **Known to be impossible?** Not as a mathematical impossibility. But the dimensional argument suggests g must bridge quantum units (ℏ) and substrate units (c, τ), so its value may encode a new physical constant.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** Possibly a new principle relating quantum and classical scales. This is the "quantum-classical interface problem" which has no general solution.

5. **Requires a new field?** No. The problem is dimensional analysis + a physical argument for the coupling scale.

6. **Requires a new observable?** Yes. An independent measurement of g (separate from the Ramsey fit) would constrain its value. This requires an experimental measurement of at least two independently varying quantities related by g.

7. **Would solving it change any physical prediction?** Yes — it would make k_rot = 8g²s₀²r_q²τ/(3ℏ²) a parameter-free prediction rather than a fit.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 3 | Required for quantitative predictions |
| Mathematical difficulty | 3 | Requires physical argument, not just math |
| Dependence on prior results | 3 | Depends on M1, M2 being settled |
| Likelihood of being solvable | 2 | No known approach |

---

### F11 — Non-Markovian Decoherence Corrections

**Statement:** Derive corrections to Γ_φ = k_rot · ω_rot² when the Markov approximation (A-HC2) fails, i.e., when τ is not small compared to Γ_φ⁻¹.

**Seven-Question Analysis:**

1. **Already solved in literature?** Partially. Non-Markovian open quantum systems are an active research area (Breuer-Petruccione [KR]). Time-convolutionless master equations and Nakajima-Zwanzig equations exist for general non-Markovian systems. Application to the specific substrate current autocorrelation C_JJ is not done.

2. **Known to be impossible?** No.

3. **Merely unknown?** Yes.

4. **Requires a new axiom?** No — requires only relaxation of A-HC2 within the existing framework.

5. **Requires a new field?** No.

6. **Requires a new observable?** Possibly — non-Markovian signatures would require time-resolved correlation measurements beyond current Ramsey data.

7. **Would solving it change any physical prediction?** Yes — the ω_rot² scaling would acquire corrections at large ω_rot, providing a distinguishing prediction between Markovian and non-Markovian substrate models.

**Ranking:**

| Criterion | Score (1–5) | Notes |
|-----------|------------|-------|
| Scientific importance | 3 | Extends prediction to strong coupling regime |
| Mathematical difficulty | 2 | Standard non-Markovian techniques available |
| Dependence on prior results | 3 | Requires settled C_JJ form |
| Likelihood of being solvable | 5 | Clear technical path within existing framework |

---

## Part II — Ranked Frontier Summary

### By Scientific Importance

| Rank | Problem | Importance | Status |
|------|---------|-----------|--------|
| 1 | F7: Large-N forces O1 and O2 | 5 | UNKNOWN |
| 2 | F2: Ball state space origin | 5 | UNKNOWN |
| 3 | F4: Lorentz group derivation | 5 | UNKNOWN |
| 4 | F6: QFT emergence | 5 | UNKNOWN |
| 5 | F5: Gauge group selection | 5 | UNKNOWN |
| 6 | F1: Microscopic reversibility PA1 | 5 | UNKNOWN |
| 7 | F9: CCA second law | 4 | UNKNOWN |
| 8 | F3: Purification derivation | 4 | UNKNOWN |
| 9 | F10: Coupling constant g | 3 | NEEDS-NEW-OBSERVABLE |
| 10 | F8: CCA GNS theorem | 3 | UNKNOWN |
| 11 | F11: Non-Markovian corrections | 3 | UNKNOWN |

### By Likelihood of Being Solvable (Near Term)

| Rank | Problem | Likelihood | Reason |
|------|---------|-----------|--------|
| 1 | F11: Non-Markovian corrections | 5/5 | Standard techniques available |
| 2 | F8: CCA GNS theorem | 4/5 | Clear analogy with existing result |
| 3 | F9: CCA second law | 4/5 | Clear strategy; requires one new lemma |
| 4 | F1: PA1 reversibility | 3/5 | No impossibility proof; route partially developed |
| 5 | F7: Large-N universality | 2/5 | Central question; no known complete attack |
| 6 | F2: Ball geometry | 2/5 | Long-standing; partial progress |
| 7 | F3: Purification | 2/5 | Long-standing; no known approach |
| 8 | F4: Lorentz group | 2/5 | Partial (Malament); full proof distant |
| 9 | F10: Coupling constant g | 2/5 | Requires new physical argument |
| 10 | F5: Gauge group | 1/5 | No known approach from C2 |
| 11 | F6: QFT emergence | 1/5 | Hardest open problem in mathematical physics |

### By Dependence on Other Frontier Problems

Problems with no prerequisites (can be attacked immediately):
- **F1** (PA1) — requires R1–R7 only
- **F7** (Large-N) — requires U1–U6 only
- **F8** (CCA GNS) — internal CCA
- **F9** (CCA second law) — internal CCA
- **F11** (Non-Markovian) — requires only relaxing A-HC2

Problems with strong prerequisites:
- **F4** (Lorentz) depends on: continuum limit tools, large-N (F7)
- **F5** (Gauge group) depends on: F4 + QFT structure
- **F6** (QFT) depends on: F4 + F2 + QM emergence

---

## Part III — Frontier Dependency Graph

```
[F7: Large-N universality] ──────────────────────────────────────────────────┐
(independent; central question)                                              │
    │                                                                        │
    ▼                                                                        │
[O1 (complex) emerges generically] ──► [F2: Ball geometry]                  │
    │                                         │                             │
    │                                         ▼                             │
    │                             [F3: Purification]                        │
    │                                         │                             │
    │                                         ▼                             │
    │                             [Full QM reconstruction]                  │
    │                                         │                             │
    ▼                                         │                             │
[O2 (continuum) emerges generically]          │                             │
    │                                         │                             │
    ▼                                         │                             │
[F4: Lorentz group] ◄──────────────────────── ┘                             │
    │                                                                        │
    ├──► [F5: Gauge group selection]                                         │
    │           │                                                            │
    │           ▼                                                            │
    │    [F6: QFT emergence] ◄────────────────────────────────────────────── ┘
    │
[F1: PA1 reversibility] ──────────────► [SCC without AA2] ──► [QM via SCC]
(independent)

[F8: CCA GNS theorem] ──────────────── (independent; enables CCA computation)
    │
    ▼
[F9: CCA second law] ─────────────────► [Thermodynamics from CCA]
    │
    ▼
[Second law + QM + spacetime] ──► [Full thermodynamic QFT]

[F10: Coupling constant g] ──────────── (depends on M1, M2 settled)
    │
    ▼
[F11: Non-Markovian corrections] ────── (depends on F10; independent otherwise)
    │
    ▼
[Parameter-free experimental prediction]
```

### Critical Path to Result A

The minimum sequence of frontier problems whose solution would upgrade the project from Result B to Result A (all physical structures derived from U1–U6 alone):

```
F7 (Large-N) → F2 (Ball geometry) → F3 (Purification) → Full QM
     │
     └──► F4 (Lorentz) → F4 + Full QM → Relativistic QM
                              │
                              └──► F5 (Gauge group) → SM physics
                                        │
                                        └──► F6 (QFT) → Complete theory
```

Additionally required (independent of the above path):
- F1 (PA1): to remove AA2 from SCC
- F8, F9: to establish CCA as a rigorous foundation (internal mathematical development)

---

## Part IV — Problems Currently Solvable Within Existing Mathematics

The following frontier problems do not require a new mathematical field and have a plausible proof strategy within established techniques. They are the recommended near-term research targets.

### F11 — Non-Markovian Corrections (Recommended first)

**Strategy:** Use the time-convolutionless (TCL) projection operator technique or Nakajima-Zwanzig equation with the substrate autocorrelation C_JJ(τ) = ⟨(δJ)²⟩ · exp(−|τ|/τ_sub). Compute the leading correction to Γ_φ in powers of τ·Γ_φ. The result will be of the form Γ_φ^(NM) = k_rot · ω_rot² · (1 + c₁ τ Γ_φ + …). This is an analytical calculation requiring no new axioms.

### F9 — CCA Second Law (Recommended second)

**Strategy:** Show that the weight function ε satisfies a doubly stochastic condition when restricted to causal morphisms (m: A → B with A ≤ B). The data processing inequality then gives H(B) ≥ H(A). Adding the rank term: r(B) ≥ r(A) by definition of the causal order (B is later than A). Therefore H_c(B) = H(B) + λ·r(B) ≥ H(A) + λ·r(A) = H_c(A). This strategy requires proving the doubly stochastic property of ε restricted to causal morphisms — a lemma about Ax4 in the presence of Ax2.

### F8 — CCA GNS Theorem (Recommended third)

**Strategy:** Mimic the GNS construction for C*-algebras. For a state ω: CCA → [0,1] (a positive normalized functional on the morphism algebra), construct the pre-Hilbert space H_ω = M / N_ω where N_ω is the null space of the inner product ⟨m₁, m₂⟩_ω = ω(m₂† ⊗ m₁). The GNS representation theorem would then state that every state on the CCA is a vector state in some H_ω. This requires showing that the CCA morphism algebra is a *-algebra (requires that ε and ⊗ give a normed *-algebra structure) — a nontrivial but likely tractable technical step.

---

*End of C2_FRONTIER_MAP.md*  
*Date: 2026-07-24*  
*All established results taken from completed C2 audits. No new mathematics introduced in this document.*
