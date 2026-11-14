# EXP9 Experimental Report — Autonomous Substrate-Mediated Collective Computation

**Date:** 2026-11-13  
**Acceptance level (confirmatory, evidence-gated):** **2**  
**Pilot preview level (non-confirmatory):** 4 (did not replicate on frozen confirmatory seeds)

---

## Central question

Has the project progressed from demonstrating computational properties of a nonlinear substrate to demonstrating that autonomous agents can use those properties as part of a larger collective computational architecture?

**Answer:** **Partially — Level 2.** Agents can deposit/read through a valid local interface, and collective correct rate under the nonlinear substrate exceeds independent agents on confirmatory seeds. The project has **not** established Level 3 composed causal chains at confirmatory scale, nor Level 4/5 reliable autonomous collective utility or distinctive advantage over fair conventional channels.

---

## What was tested

| Exp | Question |
|---|---|
| A | Distributed noisy evidence → majority landmark commitment across 7 architectures |
| B | Coincidence → hysteretic commit ablations (reaction, propagation, hold, readout, deposit, random) |
| C | Asynchronous true-evidence onset delays |
| D | Clustered vs dispersed evidence, high noise, one-agent disconnect |
| Numerical | Continuous field-error metrics + smoke coincidence latch |

## What was actually implemented

- Isolated package `sim_world/exp9/` + entrypoint `exp9_autonomous_collective.py`
- Reuses Task 8 solver path (`evolve_field_nonlinear` / `apply_perturbation`) **without editing** Task 6–8 files
- Local Gaussian deposits; local max readout in `READ_RADIUS`; public landmarks; **\(k^*\) withheld**
- Anti-confound order: **read/commit → deposit → evolve**
- Sustained-hold commit (`COMMIT_HOLD_TICKS=20`) on field media; shorter hold on msg/pheromone
- Evidence carry (agent memory of own sensing) to improve temporal coincidence of deposits
- Fair baselines: independent, direct_msg (≥2 support), blackboard, pheromone, linear substrate, hybrid

Field equation coefficients \((r,a,b,\tau,c)\) unchanged. `DEP_AMP=0.45` (vs Task 8’s 0.50) chosen so sustained-hold separates bistable latch from linear multi-deposit transients; controlled smoke still passes.

## What agents could and could not observe

**Could:** noisy local evidence scalars within `SENSOR_RADIUS`; local medium readout at visited/nearby landmarks; own private evidence memory; own pending carry.

**Could not:** true landmark index \(k^*\); other agents’ deposit logs; global field argmax; GT `is_true` on patches; precomputed collective answer.

---

## Confirmatory results (seeds 400–423, N=24)

### Experiment A — collective decision rates

| Architecture | Correct | FP | FN | Mean latency | Mean resource |
|---|---:|---:|---:|---:|---:|
| nonlinear_sub | 0.292 | 0.042 | 0.667 | 86.8 | 207.0 |
| linear_sub | 0.042 | 0.000 | 0.958 | 28.7 | 236.2 |
| independent | 0.042 | 0.000 | 0.958 | 42.0 | 13.3 |
| direct_msg | 0.333 | 0.167 | 0.500 | 27.8 | 166.1 |
| blackboard | **0.417** | 0.167 | 0.417 | 33.3 | 151.5 |
| pheromone | 0.042 | 0.000 | 0.958 | 13.0 | 236.4 |
| hybrid | 0.333 | 0.000 | 0.667 | 57.2 | 384.9 |

### Paired contrasts (permutation; Bonferroni m=5, α=0.05)

| Contrast | mean_diff | d_z | p_perm | p_adj | reject |
|---|---:|---:|---:|---:|---|
| nl − linear | +0.250 | 0.57 | 0.031 | 0.156 | no |
| nl − independent | +0.250 | 0.57 | 0.028 | 0.138 | no |
| nl − direct_msg | −0.042 | −0.12 | 1.0 | 1.0 | no |

Unadjusted directional advantage vs independent/linear is present; **multiple-comparison–adjusted significance is not claimed.**

### Experiment B — causal ablations

| Ablation | Correct rate |
|---|---:|
| nonlinear_full | 0.292 |
| linear_telegraph | 0.042 |
| reaction_off | 0.042 |
| no_propagation | 0.625 |
| no_hysteresis | 0.125 |
| readout_disabled | 0.000 |
| deposit_disabled | 0.000 |
| fixed_random_policy | 0.125 |

`chain_supported = False` on confirmatory (full rate 0.292 < 0.35 gate). Readout and deposit are necessary. Reaction drop vs full is +0.25 absolute. **Propagation is not necessary** — `no_propagation` outperformed full (local energy retention aids latch; diffusion can dissipate coincident amplitude). This matches Task 8’s local-overlap finding and is reported as a mechanism result, not a failure of preservation.

### Experiment C — async delays (nonlinear)

| Delay | Correct rate |
|---|---:|
| 0 | 0.292 |
| 2–20 | 0.167–0.208 |
| 40 | 0.083 |

Performance decays with delayed true evidence. **Temporal order discrimination is not supported** (scalar field has no order operator).

### Numerical

`numerical.all_pass = True` (continuous amplitude/profile criteria, not binary-only). Smoke coincidence: nl activates, linear does not.

---

## What the substrate contributed

1. **Operational interface (Level 1):** deposit/read cycle works; controlled two-deposit latch distinguishes nl vs linear.
2. **Agent-level utility vs no-communication (Level 2):** confirmatory nl correct rate ≫ independent (0.292 vs 0.042); decisions depend on field state (readout/deposit ablations → 0).
3. **Mechanism:** nonlinear reaction + persistence under sustained-hold; local coincidence, not long-range propagation, drives usable latch in this geometry.
4. **Not contributed:** reliable majority correctness; superiority to messaging/blackboard; confirmatory composed Level-3 chain under the predeclared `full>0.35` gate; distinctive Level-5 architectural necessity.

## Which conventional baselines matched or outperformed

- **Blackboard (0.417) and direct_msg (0.333) ≥ nonlinear (0.292)** under matched observation and multi-source commit rules.
- **Hybrid (0.333)** similar to messaging; higher resource cost (solver + messages).
- **Pheromone** collapsed under evaporative dynamics vs multi-source threshold (0.042) — a trade-off of the fairness settings, not evidence that pheromone is generally useless.

## Hypotheses that failed

- Pilot Level 4 does not replicate on confirmatory seeds (nl drops 0.625 → 0.292).
- Composed coincidence→hysteresis agent chain not confirmatory-supported under predeclared gates.
- Substrate superiority over messaging/blackboard not established.
- Temporal order reasoning not available from scalar field dynamics.
- Simple field-amplitude maximization is insufficient when distractors and async onset are present (high FN).

## Numerical / statistical limitations

- Confirmatory N=24; Bonferroni-adjusted primary contrasts do not reject H₀.
- Pilot seeds 0–7 were optimistic; confirmatory seeds 400+ are authoritative.
- `DEP_AMP` slightly below Task 8’s 0.50 (documented); equation coefficients frozen.
- Dirichlet-like boundaries not swept; \(\tau\neq1\) Laplacian docstring ambiguity unused.
- High FN (missed latch / insufficient coincident deposits) dominates error mode for field architectures.

## Acceptance reasons

- Level 1: deposit/read + controlled latch interface OK
- Level 2: nl collective correct_rate exceeds independent
- Level 5 withheld: requires distinctive advantage vs fair messaging/BB not explained by conventional channels

## Claims remaining unsupported

- Substrate superiority over direct messaging / blackboard
- Composed coincidence→hysteresis agent chain at confirmatory acceptance gates
- Temporal order discrimination
- Level 4 autonomous collective reliability under noise/async
- Level 5 distinctive architectural contribution

## Preservation

Task 6–8 protected MD5 manifests: **21/21 + 17/17 + 22/22 unchanged** after Task 9 (`EXP9_PRESERVATION_CHECK.md`).

## Artifact index

- `exp9/EXP9_PRE_IMPLEMENTATION_AUDIT.md`
- `exp9/EXP9_ARCHITECTURAL_SPECIFICATION.md`
- `exp9/EXP9_EXPERIMENTAL_PROTOCOL.md`
- `exp9/EXP9_BASELINE_FAIRNESS_AUDIT.md`
- `exp9/EXP9_NUMERICAL_VALIDATION.md`
- `exp9/EXP9_PRESERVATION_CHECK.md`
- `exp9_configuration.json` / `exp9_results.json` / `exp9_pilot_results.json`
- `exp9/exp9_raw_per_seed.json`
- `exp9/exp9_checksums.txt`
- `tests/test_exp9_interface.py`, `tests/test_exp9_ablations.py`
- `exp9_autonomous_collective.py`

---

## Bottom line

Task 9 demonstrates a **working autonomous agent–substrate interface** and a **directional collective benefit over independent agents**, causally dependent on deposit/readout. It does **not** yet show that the nonlinear substrate is a reliable or distinctive collective computer relative to fair messaging/blackboard under the frozen protocol. Progress from Task 8’s controlled primitives to operational agent use is real at Level 2; Levels 3–5 remain open scientific requirements (higher latch reliability under exploration noise, stronger confirmatory causal gates, and a capability messaging cannot cheaply duplicate).
