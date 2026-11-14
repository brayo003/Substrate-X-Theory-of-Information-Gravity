# EXP9 Experimental Protocol

**Date:** 2026-11-13  
**Freeze rule:** Pilot explores ranges; confirmatory seeds and parameters freeze in `exp9_configuration.json` before confirmatory inspection. No retuning on confirmatory data.

---

## 1. Shared environment geometry

- Domain \([0,50]^2\), grid \(30\times30\), \(\Delta t=0.05\).  
- \(K=4\) landmark posts at fixed public coordinates (corners of a square inset).  
- Exactly one correct landmark \(k^\*\) drawn per trial (evaluator-only).  
- Evidence patches: \(N_{\mathrm{ev}}\) noisy observation sites near \(k^\*\) (true evidence) plus distractor patches near wrong landmarks.  
- Agents: \(N_a=4\) (default), random initial poses, speed \(v_{\max}=2.0\), \(\rho_{\mathrm{obs}}=3.5\), \(\rho_{\mathrm{read}}=5.0\).

---

## 2. Experiment A — Distributed evidence → collective decision

**Question:** Can agents integrate incomplete noisy local evidence into a correct landmark commitment via the substrate vs fair baselines?

**Conditions (required):**

1. `nonlinear_sub`  
2. `linear_sub`  
3. `independent`  
4. `direct_msg`  
5. `blackboard`  
6. `pheromone`  
7. `hybrid` (nonlinear field + budget-capped messaging)

**Primary outcome (pre-declared):** correct collective decision rate = fraction of trials where the first majority commitment equals \(k^\*\) (ties → incorrect).

**Secondary:** FPR (commit wrong), FNR (no commit by \(T_{\max}\)), decision latency, useful depositors, comm volume, deposits, reads, travel distance, completion rate, resource expenditure; sweeps: observation noise \(\sigma\), agent disconnect, async evidence onset.

**Hypothesis A1:** Nonlinear substrate improves correct rate vs linear under matched deposit budgets when true evidence requires multi-agent coincidence near \(k^\*\).  
**Hypothesis A2:** Messaging/blackboard may match or beat substrate (not a failure; report trade-offs).  
**Hypothesis A3:** Independent underperforms when no single agent sees enough evidence.

---

## 3. Experiment B — Coincidence → hysteretic decision chain

**Sequence:** multi-agent deposits → spatial coincidence latch → persistent high basin → scout detects activated landmark by visiting → environmental action (commit).

**Ablations:** full nl, linear, reaction_off, no_hysteresis, readout_disabled, deposit_disabled, no_propagation, fixed_random_policy.

**Primary:** causal chain success rate (correct commit) under full nl; each ablation must drop success for its claimed mechanism when applicable.

**Note:** Task 8 found latch without propagation at sep≈3. B reports which mechanisms are necessary **in the agent setting**, not assumed.

---

## 4. Experiment C — Temporal integration (async arrival)

Evidence-bearing agents arrive / deposit at delays \(\delta\in\{0,2,5,10,15,20,40\}\) ticks (Task 8 window scale).

**Measures:** performance vs delay; vs number of contributors; false activation from unrelated deposits; persistence after latch; recovery after contradictory/obsolete evidence; latency.

**Distinctions recorded separately:** accumulation vs retention vs order sensitivity vs discrimination.  
**Limitation carry-forward:** scalar bistability did not support order logic in Task 7/8 — re-test lightly; if fails, record limitation (do not claim temporal reasoning).

---

## 5. Experiment D — Spatial coordination

Variants: clustered evidence, dispersed, spatial distractors, competing targets, noisy deposits, disconnect, varied initial distributions.

**Primary:** correct commit rate and travel cost; whether agents use spatial field structure (gradient / local search) vs scalar max at a single planted ROI.

---

## 6. Numerical validation (before confirmatory claims)

Stronger than Task 8 binary-only grid check:

- dt ∈ {0.05, 0.025, 0.0125}: field amplitude L2 / local_max error + decision agreement  
- grid 30×30 vs 40×40 vs 50×50: profile error, activation-boundary displacement, **agent decision** agreement  
- BC sensitivity note (Dirichlet-like)  
- high deposit density stability  
- seed reproducibility  
- Report whether refinement changes agent decisions — do not call “converged” on binary-only agreement if continuous error is large.

Artifact: `EXP9_NUMERICAL_VALIDATION.md` + results block in `exp9_results.json`.

---

## 7. Statistical protocol

| Phase | Seeds | Use |
|---|---|---|
| Pilot | 0–7 | difficulty, ranges, failure modes, N estimate |
| Freeze | — | write `exp9_configuration.json` |
| Confirmatory | 400–423 (N=24) unless pilot justifies change **before** freeze | inference |

- Paired seed-matched architecture comparisons.  
- Effect size (paired mean diff, Cohen’s \(d_z\)).  
- Exact/permutation tests where feasible; Wilcoxon signed-rank as robustness.  
- Bonferroni (or Holm) across pre-declared primary family.  
- Report raw per-seed rows; missing/failed runs; exclusions.  
- **No composite score as sole evidence.**

**Primary family (confirmatory):**

1. A: nl vs linear correct-rate  
2. A: nl vs independent  
3. A: nl vs direct_msg (non-inferiority not required; report)  
4. B: full vs reaction_off chain success  
5. C: delay0 vs delay40 activation/correct  

---

## 8. Acceptance mapping

| Level | Criterion (evidence-gated) |
|---|---|
| 0 | No reliable field use |
| 1 | Deposit/read interface works; no collective benefit |
| 2 | Decisions causally depend on field; basic controls hold |
| 3 | ≥2 Task-8 primitives in verified causal chain (Exp B) |
| 4 | Autonomous collective utility vs fair baselines under noise/async/partial obs (Exp A/C/D) |
| 5 | Distinctive architectural contribution not explained by messaging/BB/pheromone/local compute |

Do not award beyond evidence. Negative results are first-class.

---

## 9. Pilot → freeze checklist

Before confirmatory:

- [x] Interface tests pass  
- [x] Ablation tests pass  
- [x] Numerical block recorded  
- [x] Pilot JSON written  
- [x] `exp9_configuration.json` frozen  
- [x] Task 6–8 checksums still match before-manifest

**Freeze note:** `DEP_AMP=0.45`, `COMMIT_HOLD_TICKS=20`, `MSG_MIN_SUPPORT=2`, evidence carry enabled. Pilot preview Level 4; confirmatory authoritative Level **2**.
