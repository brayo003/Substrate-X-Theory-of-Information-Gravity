# EXP6 — Nonlinear Substrate Agentic Advantage: Final Scientific Assessment

**Date:** 2026-11-13  
**Experiment:** `exp6_nonlinear_advantage.py`  
**Data:** `exp6_pilot_results.json`, `exp6_results.json`  
**Status:** Complete — all criteria answered

---

## 1. Research Question

Does the nonlinear reaction-telegraph substrate provide a measurable performance
advantage for multi-agent systems compared to conventional communication and
shared memory, and under what conditions?

---

## 2. Experimental Design

### Conditions

| Label | Mechanism |
|---|---|
| A — independent | No shared memory or messaging |
| B — direct_msg | Broadcast messages; TTL=8 ticks |
| C — blackboard | Global shared list; entries expire at 20 ticks |
| D — pheromone | Evaporating spatial grid per event type |
| E — nonlinear_sub | Reaction-telegraph field (r=−0.5, a=2.0, b=1.0) |
| F — linear_sub | Same architecture, r=a=b=0 (linear ablation) |

Information budget matched: all non-independent conditions deposit one Gaussian
per sensed event per agent (identical write rate).

### Task Families (concurrent within each trial)

- **Task 1 — Resource discovery:** 8 sites, staggered availability. Metric: discovery rate, duplicate-work fraction.
- **Task 2 — Hazard coordination:** 5 hazard zones, 8–30 tick duration. Metric: hazard exposure rate (lower = better).
- **Task 3 — Task allocation:** 6 slots requiring 1–2 agents. Metric: completion rate.

### Statistical Design

- Paired comparisons: identical event schedules per seed across all conditions.
- Pilot: N=20 seeds (seeds 0–19). Confirmatory: N=60 seeds (seeds 100–159, disjoint).
- Bootstrap 95% CIs (2000 resamples), Cohen's d, paired t-test.
- Bonferroni correction: 5 comparisons vs Independent, α_corrected = 0.010.

---

## 3. Confirmatory Results (N=60 seeds per condition)

### Per-condition means

| Condition | Composite | Res rate | Hz exp | Task rate | Info acc |
|---|---|---|---|---|---|
| independent | 0.288 | 0.254 | 0.836 | 0.228 | 0.958 |
| direct_msg | 0.510 | 0.300 | 0.259 | 0.264 | 0.929 |
| blackboard | 0.518 | 0.279 | 0.214 | 0.258 | 0.932 |
| pheromone | 0.514 | 0.267 | 0.193 | 0.272 | 0.836 |
| **nonlinear_sub** | **0.457** | **0.546** | **0.604** | **0.233** | **0.810** |
| linear_sub | 0.426 | 0.408 | 0.561 | 0.231 | 0.830 |

Composite score = 0.35·res_rate + 0.35·(1−hz_exp) + 0.20·task_rate + 0.10·info_acc.

### Pairwise vs Independent (Bonferroni α=0.010)

| Condition | Composite Δ | Cohen's d | p-value | Sig? |
|---|---|---|---|---|
| direct_msg | +0.222 | 2.049 | <0.0001 | *** |
| blackboard | +0.230 | 2.115 | <0.0001 | *** |
| pheromone | +0.226 | 2.109 | <0.0001 | *** |
| **nonlinear_sub** | **+0.169** | **1.464** | **<0.0001** | *** |
| linear_sub | +0.138 | 1.048 | <0.0001 | *** |

All five conditions significantly outperform independent agents after correction.

---

## 4. Ablation: Nonlinear vs Linear Substrate (E vs F)

| Metric | nonlinear_sub | linear_sub | Δ |
|---|---|---|---|
| Composite | 0.457 | 0.426 | **+0.031** |
| Resource rate | 0.546 | 0.408 | **+0.138** |
| Hazard exposure | 0.604 | 0.561 | +0.043 (worse) |
| Task rate | 0.233 | 0.231 | +0.002 |

The nonlinear advantage over the linear ablation is concentrated in resource
discovery (+0.138). Mechanism: bistability (equilibria at s=0, s≈0.293
separatrix, s≈1.707) extends the lifetime of positive-perturbation deposits.
Once a resource discovery pushes local field above the separatrix, the field
persists near s≈1.707 rather than decaying, giving other agents a longer
detection window.

---

## 5. What Was Demonstrated

### Confirmed

**Information transmission** — both substrate conditions carry resource location
information across agents. The increase in resource rate above independent confirms
agents exploit previously-deposited field states.

**Specialized spatial memory advantage** — the nonlinear substrate (res_rate=0.546)
outperforms both the linear substrate (0.408) and independent agents (0.254) on
resource discovery. Bistable persistence is a mechanistically distinct memory
mechanism from simple field decay.

**Statistically robust advantage over no-communication baseline** — Bonferroni-
corrected d=1.464, p<0.0001 on composite score over 60 paired seeds.

### Not Demonstrated

**General superiority over conventional alternatives** — direct_msg, blackboard,
and pheromone all outperform the nonlinear substrate on composite score
(Δ=0.22–0.23 vs Δ=0.169). The substrate does not provide a general advantage.

**Hazard coordination advantage** — the nonlinear substrate is worse than
pheromone (hz_exp=0.604 vs 0.193) on hazard avoidance. Negative-perturbation
encoding in a bistable field is mechanistically antagonistic: the autocatalytic
term partially counteracts negative deposits before cubic saturation takes hold.

**Task allocation advantage** — all conditions cluster tightly (0.228–0.272).
Task allocation is dominated by spatial proximity, not information quality.

**Collective information processing beyond superposition** — the controlled
multi-agent injection test specified in §5 of the task (inject X, inject Y,
measure whether C recovers X+Y interaction) was not executed. That test requires
a separate controlled protocol and is not addressed by this trial design.

**Multi-channel encoding** — only a single scalar field was used. The task
specification calls for testing multi-channel encoding; this is left for future
work.

---

## 6. Limitations

**Substrate instability** — repeated large perturbations trigger overflow in the
nonlinear solver on some seeds. The exception handler resets the field; this
counts as degraded performance and may suppress the substrate's advantage on
high-activity seeds.

**Hazard encoding design** — negative deposits were used to encode hazard zones.
This is antagonistic to bistable dynamics. A separate channel or threshold-based
encoding was not tested. The current results therefore underestimate the
substrate's potential hazard-avoidance performance under a better-designed encoding.

**Agent movement policy** — agents do not explicitly route around hazard zones
using the substrate readout. A policy that acts on hazard field values would
more directly reveal the value of accurate hazard encoding.

**Info-recovery metric** — `info_recovery_acc` measures readout calibration, not
utility. Independent agents score highest because they have zero readout noise.
The metric does not capture noisy-but-useful substrate signals.

---

## 7. Outcome Classification

**OUTCOME 2 — Specialized Advantage**

The nonlinear substrate delivers a reproducible, large-effect advantage in
spatial persistent memory for resource discovery. It does not provide general
superiority over conventional communication alternatives under the tested
conditions and encoding scheme.

The automated classifier returned Outcome 3 based on counting Bonferroni-
significant metrics vs independent. Manual review overrides this: the
relevant comparison is against conventional alternatives (not no-communication),
and on that comparison the substrate does not win.

---

## 8. Answers to the Core Questions

| Question | Answer |
|---|---|
| Measurable advantage over no communication? | **Yes.** d=1.464, p<0.0001, Δ=+0.169 composite |
| Outperforms conventional alternatives? | **No.** Blackboard/pheromone/direct_msg all score higher |
| Which specific capability? | Persistent spatial memory for resource discovery |
| Is the nonlinear advantage separate from linear? | **Partially.** +0.031 composite, +0.138 resource rate over linear_sub |
| When does substrate excel? | Positive-signal persistent spatial memory |
| When does substrate fail? | Negative-signal encoding (hazard); task allocation |
| What would reveal broader advantage? | Multi-channel fields; policy that exploits hazard readouts; collective injection test |

---

## 9. Substrate Parameters (registered before confirmatory run)

| Parameter | Value |
|---|---|
| r | −0.5 |
| a | 2.0 |
| b | 1.0 |
| τ | 1.0 s |
| c | 1.0 m/s |
| dt | 0.05 s |
| Grid | 30×30 nodes, 50×50 m |
| dx | ≈1.72 m |
| Courant number | 0.029 |
| Equilibria | s=0 (stable), s≈0.293 (separatrix), s≈1.707 (stable) |
| BCs | Zero-Laplacian (artifact documented in prior audit) |

No parameters were changed between pilot and confirmatory runs.

---

## 10. Replication

```bash
cd sim_world/
python exp6_nonlinear_advantage.py --pilot          # 14 s, seeds 0–19
python exp6_nonlinear_advantage.py --seeds 60       # ~55 s, seeds 100–159
```

All seeds are fixed. Conditions use identical event schedules per seed.
Results are fully reproducible without retraining or parameter search.
