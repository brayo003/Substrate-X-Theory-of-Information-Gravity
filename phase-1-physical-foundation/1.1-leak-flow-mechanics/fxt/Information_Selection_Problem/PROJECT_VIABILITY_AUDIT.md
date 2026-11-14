# SXC-IGC PROJECT VIABILITY AUDIT

**Date:** 2026-08-24  
**Basis:** Repository evidence only. No assumed inputs.  
**Standard:** Adversarial. The project gets no benefit of the doubt.

---

## 1. What the project is actually trying to accomplish

The project attempts to derive a selection function F: Γ_GR → {0,1} that restricts physical gravitational initial data to low-Weyl configurations, from premises that do not encode low Weyl as input. This is the formal statement of R1 (final formulation, 09_FINAL_FORMULATION.md).

The original SXC-IGC framing ("Substrate X," "leak-flow mechanics," "information gravity") was an earlier ontological hypothesis. That hypothesis was investigated through the Giga program and reduced to standard differential geometry — it produced no experimentally distinguishable prediction (00_FOUNDATIONAL_REASSESSMENT.md, Giga 07 verdict: EQUIVALENT TO KNOWN PHYSICS). The current Information_Selection_Problem workspace explicitly inherits nothing from SXC-IGC's ontology (CHARTER.md §1). The SXC-IGC name is therefore a label for a dead framework attached to an active, cleaner research question.

The live question is: does the AS (Asymptotic Safety) UV fixed-point structure, specifically via the cubic Weyl coupling w₃*, provide the selection function F?

---

## 2. What has genuinely been established

The following are established with cited evidence and are not contestable:

**A. R1 is a genuine open problem.**  
A 28-mechanism audit found no existing theory derives Γ_phys ⊊ Γ_GR with low-Weyl restriction from independent premises (GATE6_P01_FINAL_VERDICT.md, INFORMATION_SATURATION.md). Ekpyrosis is the strongest existing partial mechanism but fails in the pre-contraction regime. This is a genuine scientific gap, not an artifact.

**B. The C² route is exactly eliminated.**  
Bach_{μν} = 0 on all Ricci-flat vacuum spacetimes is an exact algebraic consequence of the contracted Bianchi identity. No calculation is needed beyond the identity. Kasner is an exact saddle of every C²-containing effective action for any coupling value. This is not a truncation artifact. (Gate 1, KASNER_FULL_ACTION_AUDIT.md)

**C. The W3 Euler-Lagrange tensor is nonzero on Kasner.**  
E_{11} = E_{22} = 3968/(243 t^{22/3}), E_{33} = 6272/(243 t^{16/3}). Computed exactly (gate1b_kasner_variation.py). W3 genuinely modifies the Kasner equation of motion. This is a real mathematical result.

**D. The W3 source term A_W3 = 0 in the EH+C²+W3 AS truncation.**  
The canonical computation (gate2_canonical.py) establishes: five TT W3 Hessian eigenvalues {−2,+2,−2,+1,+1} sum to zero; the C² Hessian coefficient α₂=1 is identical for all five TT modes; the regulated denominator is therefore sector-independent; the threshold integral factors out; A_W3 = (Σ K_s) × I = 0. This is an exact algebraic result within the stated truncation.

**E. The original SXC-IGC substrate ontology is exhausted.**  
Giga 01–07 systematically reduced every primitive in the Substrate X framework to standard differential geometry or eliminated it on structural grounds. No genuinely new primitive survived (00_FOUNDATIONAL_REASSESSMENT.md).

**F. None of the six required capabilities is provided by SXC-IGC.**  
08_SXC_IGC_CAPABILITY_AUDIT.md tests SXC-IGC against six independent criteria (new measure on Γ_GR, new covariant constraint, new dynamical attractor, quantum-state selection, action modification, superselection structure). Score: 0/6. No capability is derived.

---

## 3. What has been falsified

**Within the tested truncation:**  
The specific mechanism "AS generates w₃* ≠ 0 in EH+C²+W3 truncation, removing Kasner saddle" is falsified. w₃* = 0 is the unique fixed point. This is not a failure of calculation — it is the correct answer for this truncation.

**The C² mechanism:**  
Eliminated exactly, not approximately. The gap between β* ~ 0.05 (computed) and β* > 23 (required) is a factor of 460+, and there is no mechanism within AS to bridge it. This gap is not narrowing with truncation order.

**The SXC-IGC substrate ontology:**  
Reduced to known physics. Not falsified as mathematics — falsified as a source of new physical content.

**The claim that AS fixes the initial state:**  
AS is a theory of quantum gravity dynamics. It determines the effective action. It does not determine the quantum state of the universe. This is a category error, identified clearly in AS_QUANTUM_STATE_AUDIT.md. No AS computation can supply an initial state without a separate boundary condition.

---

## 4. What remains merely mathematical

**W3/Kasner variation (Gate 1B):**  
The result E_{μν} ≠ 0 on Kasner is real mathematics, but it is not a physical mechanism. It establishes that if w₃* were nonzero, Kasner would not be a saddle. The antecedent is false in the tested truncation. The result is mathematically interesting but physically inert without the antecedent.

**W3 Hessian structure {−2,+2,−2,+1,+1}:**  
A correctly computed tensor result on S²×S². It has no physical consequence beyond its role in the now-resolved Gate 2 calculation, where it led to A_W3 = 0.

**The operator basis audit (I5 = 2I6 in 4D):**  
A correct algebraic identity. Value: eliminates a potential obstruction that turned out not to matter because A_W3 = 0 by a different mechanism.

**The R1 formalization machinery:**  
The precise formulation of R1-D and the 9-condition requirement for the selection function F are well-constructed. This is conceptual work with genuine clarity. It is not a physical theory.

---

## 5. First unresolved physical link

The causal chain the project requires is:

```
(1) Fundamental ontology (AS UV fixed point)
      ↓ [ESTABLISHED — literature]
(2) w₃* ≠ 0 at the fixed point
      ↓ [FALSIFIED in EH+C²+W3 truncation; unknown in full theory]
(3) Kasner excluded as saddle of AS effective action
      ↓ [MISSING — requires (2)]
(4) All high-Weyl initial data excluded
      ↓ [MISSING — not demonstrated even if (3) held]
(5) Observable consequence
      ↓ [STRUCTURALLY BLOCKED — Planck-scale physics, inflation erasure]
```

The first indispensable missing link is **arrow (2)**: w₃* ≠ 0 in the full or extended AS effective action. This has been tested in the simplest truncation and found to be zero. Whether it is nonzero in an extended truncation is unknown but not supported by any existing result.

Even if (2) were established, arrow (4) would remain entirely unaddressed: excluding Kasner does not exclude Bianchi IX, Mixmaster, or generic inhomogeneous high-Weyl initial data. R1 requires all of them to be excluded.

And even if (4) were established, arrow (5) is structurally blocked: any Planck-scale initial-state mechanism produces predictions erased by inflation at observable scales. No distinguishable prediction has been identified.

---

## 6. Does SXC-IGC currently qualify as a physical theory?

Auditing the 12 criteria:

| # | Criterion | Status | Evidence |
|---|-----------|--------|---------|
| 1 | Well-defined physical degrees of freedom | FAIL | SXC-IGC substrate ontology reduced to known geometry (Giga 07) |
| 2 | Well-defined state space | FAIL | No state space defined; R1 formulation clarifies the gap |
| 3 | Dynamical law | FAIL | Giga 07: transition-relation dynamics = geodesic motion = GR |
| 4 | Variational principle | NOT DEFINED | No action derived from SXC-IGC primitives |
| 5 | Coupling to spacetime with physical meaning | FAIL | Giga 07: coupling reduces to equivalence principle |
| 6 | Recovery limit to established physics | PARTIAL | Giga 07 shows GR recovery, but as reduction not limit |
| 7 | Initial-value formulation | FAIL | Not defined |
| 8 | Stability/unitarity/causality | NOT DEFINED | No propagator, no spectrum |
| 9 | Parameter determination | FAIL | Radial exponent α, coupling A(M) are free parameters |
| 10 | At least one falsifiable prediction | FAIL | 0/6 capabilities derived; no prediction identified |
| 11 | Distinction from existing theories | FAIL | Giga 07 verdict: equivalent to known physics |
| 12 | Mechanism that addresses R1 | FAIL | 08_SXC_IGC_CAPABILITY_AUDIT: 0/6 |

**Answer: SXC-IGC is not a physical theory. It is not a candidate mathematical framework with defined physical content. It is a research label applied to an exhausted ontological hypothesis combined with a legitimately open scientific problem (R1) that the hypothesis cannot address.**

---

## 7. Has R1 been solved?

No. Not partially. Not approximately.

Testing the required demonstration items:

| Item | Status |
|------|--------|
| A. Exclusion of Kasner | FAILED — w₃* = 0; Kasner is a saddle of the tested effective action |
| B. Exclusion of Bianchi-type high-Weyl states | NOT ATTEMPTED |
| C. Exclusion of generic anisotropic initial data | NOT ATTEMPTED |
| D. Selection of low-Weyl data in full phase space | NOT ATTEMPTED |
| E. Dynamical attraction toward low-Weyl states | NOT ATTEMPTED |
| F. Compatibility with FLRW | NOT DEMONSTRATED |
| G. Compatibility with known early-universe physics | NOT DEMONSTRATED |
| H. Survival through inflation | STRUCTURALLY BLOCKED |

A alone would not constitute solving R1. Items A through H are all required. None is established.

---

## 8. Strongest reason to continue

**The honest version:** There is one genuinely nontrivial result. Gate 1B established that the W3 Euler-Lagrange tensor is exactly nonzero on Kasner. This is a real mathematical fact. It means the Kasner obstruction for C² (Bach = 0) is not universal — it is specific to the C² operator. There exist operators in the gravitational action whose variation does not vanish on Kasner.

This opens a legitimate question: is there any extended AS truncation — beyond EH+C²+W3, perhaps including C⁴ or other operators — in which some combination of higher-derivative couplings acquires a nonzero fixed-point value that removes the Kasner saddle? The question is not answered by the current computation. It is a well-defined mathematical question about the AS fixed-point structure.

Additionally, R1 itself is a genuine open problem that is correctly formulated in this project's documents. The analytical framework built here — the precise statement of what a solution requires (9 conditions), the elimination of 28 candidate mechanisms, the structural no-go for Ricci-polynomial conditions — is a real contribution to understanding why the problem is hard.

---

## 9. Strongest reason to stop

**Five independent arguments:**

**Argument 1 — The original framework is dead.** SXC-IGC's substrate ontology was fully reduced to known physics. The project has been operating without its proposed foundation for the past several months. The remaining work is AS research, which already has a large independent community. There is no SXC-IGC content left.

**Argument 2 — The mechanism has now been tested and failed.** The specific route — AS UV fixed point generating w₃* ≠ 0, removing Kasner saddle — was the last identifiable route within the project's framework. Gate 2 closed it. There is no next route defined by the project's own logic that is not speculative.

**Argument 3 — The structural obstruction is severe.** In vacuum GR, all non-trivial curvature information is Weyl. Any covariant condition that avoids explicitly referencing C_{αβγδ} is satisfied by Kasner (06_NO_GO_ANALYSIS.md, near-theorem). Any mechanism that works by generating a term whose variation removes the Kasner saddle must explicitly generate W3 dependence. The AS mechanism was supposed to do this; it doesn't. The next operator in the series (C⁴, etc.) would need to be tested individually, with no theoretical reason to expect a different result.

**Argument 4 — Observable predictions are structurally inaccessible.** Any Planck-scale initial-state mechanism — whether it works or not — produces predictions at angular scales far smaller than the CMB resolution after inflation processes them. The mechanism could be exactly correct and be observationally indistinguishable from standard inflation + GR. This is not a problem that more mathematics will solve. It is a physical blockade.

**Argument 5 — The project has already audited itself to exhaustion.** The repository contains a 28-mechanism elimination, a full SXC-IGC capability audit (0/6), three full G rounds of substrate testing, two rounds of foundational reassessment, and a precisely stated open problem (R1) with no surviving mechanism. This is not a research program that is close to closure. It is a research program that has systematically eliminated everything it has tried.

---

## 10. Research-director decision

**D — ARCHIVE**

**Reason:** The original SXC-IGC framework has been reduced to known physics and provides no new mechanism. The one surviving computation (Gate 1B: W3 variation nonzero on Kasner) established a necessary condition for a mechanism that subsequently failed to exist (Gate 2: w₃* = 0). There is no defined next step that is not speculative exploration of a different AS truncation — work that properly belongs to the broader AS research community, not to a project whose core framework is exhausted.

**What evidence would have justified continuation and why the project lacks it:**

To justify ongoing investment, the project needed at least one of:
- A nonzero w₃* in any AS truncation (not found; Gate 2 failed)
- A genuinely new mathematical primitive surviving the 28-mechanism elimination (not found; all candidates failed or were eliminated as equivalent to known physics)
- A physical mechanism distinct from known AS work that addresses R1 (not found; SXC-IGC adds nothing to the AS program that the AS community is not already pursuing)
- A falsifiable prediction distinguishable from ΛCDM+inflation (not found; structurally inaccessible)

The project possesses none of these. It possesses several negative results of genuine value (see Part VII below) and a correctly formulated open problem. These do not justify a continuation of the SXC-IGC research program.

---

## 11. If continuing: one bounded decisive test

Not applicable (decision: Archive). However, for completeness, the single test that could have changed the decision:

**Compute w₃* in the EH+C²+W3+C⁴ truncation.** If A_W3 ≠ 0 in an extended truncation, the mechanism is revived. This is a well-defined calculation. If it also returns zero due to a similar cancellation, the pattern constitutes strong evidence that all higher-derivative Weyl truncations will cancel, and the program is terminated.

This test should be done by the AS community as a standalone calculation, not as a central research program.

---

## 12. Explicit stop condition

The stop condition is already met: the last identified mechanism (W3/AS) has been tested and returned zero. The project has no defined next mechanism that is not speculative extension. The original ontological framework (SXC-IGC substrate) is exhausted. The open problem (R1) is correctly formulated but cannot be advanced within this project's framework.

If the stop condition is disputed and continuation is desired: **the hard stop is one additional AS truncation calculation.** If w₃* = 0 also in the EH+C²+W3+C⁴ truncation (computable within 2–4 weeks of focused work by a single researcher), the project terminates. If w₃* ≠ 0 in that truncation, the calculation should be published as a standalone AS result and evaluated on its own merits by the AS community — not continued as SXC-IGC.

There is no scenario in which "more exploration" of new candidate operators within this framework constitutes a rational research allocation.

---

## 13. FINAL VERDICT

**Classification of major unresolved claims:**

| Claim | Classification |
|-------|---------------|
| w₃* ≠ 0 in some AS truncation | OPEN WITH EVIDENCE AGAINST IT — one truncation gave zero; no reason to expect nonzero in extensions |
| AS mechanism solves R1 | EFFECTIVELY FALSIFIED WITHIN THE CURRENT FRAMEWORK |
| SXC-IGC substrate provides new physics | EFFECTIVELY FALSIFIED — Giga 07, 00_FOUNDATIONAL_REASSESSMENT |
| R1 is solvable by any known mechanism | OPEN AND HIGHLY SPECULATIVE |
| Gate 1B result is physically significant | MATHEMATICALLY POSSIBLE BUT PHYSICALLY UNMOTIVATED without w₃* ≠ 0 |
| Observable prediction from Planck-scale initial-state mechanism | NOT EVEN WELL-DEFINED ENOUGH TO TEST at current observational resolution |

**Value of existing work:**

| Category | Item | Genuine value? |
|----------|------|----------------|
| Scientific discoveries | R1 is a genuine open problem (28-mechanism audit) | YES — independent of SXC-IGC |
| Scientific discoveries | C²/Kasner obstruction (Bach = 0 exactly) | YES — clean exact result with broad validity |
| Scientific discoveries | W3/Kasner variation nonzero (Gate 1B) | MODERATE — correct result, limited utility without w₃* ≠ 0 |
| Useful negative results | Gate 2: w₃* = 0, A_W3 = 0 exactly | YES — closes the W3/AS route definitively |
| Useful negative results | Giga 01–07: substrate → known physics | YES — saves future researchers from this path |
| Useful negative results | SXC-IGC 0/6 capability audit | YES — clean audit methodology |
| Reusable math | W3 Hessian {−2,+2,−2,+1,+1} on S²×S² | YES — correct tensor computation |
| Reusable math | C² sector-independence proof on Einstein backgrounds | YES — useful for AS community |
| Reusable math | R1 precise formulation and 9-condition requirement | YES — clarifies the problem for future work |
| Methodological | FRGE trace audit methodology | MODERATE — superseded by existing AS literature |
| Organizational | Documentation apparatus | LOW — internal to project |
| Low significance | 40+ numbered scripts exploring same calculation | LOW |

**THE MATHEMATICAL PROGRAM IS REAL, BUT ITS PHYSICAL CORE IS NOT CURRENTLY ESTABLISHED.**

The negative results are genuine and some have value independent of SXC-IGC. The mathematical computations are correct. But the physical framework — Substrate X, leak-flow mechanics, information gravity — is exhausted and produces nothing not already in GR and AS. The surviving work is a well-posed open problem (R1) and a set of negative results about what does not solve it. Neither constitutes a physical research program.

The project should be archived. The R1 formulation and the negative results should be written up as a concise paper for the AS and quantum gravity communities. Further work on R1 belongs in those communities, not in a project whose central hypothesis has been reduced to known physics.
