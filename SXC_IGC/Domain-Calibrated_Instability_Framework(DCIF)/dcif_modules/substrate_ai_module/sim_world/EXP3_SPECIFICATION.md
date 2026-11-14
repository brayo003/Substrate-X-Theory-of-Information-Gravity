# EXP3 SPECIFICATION
**Status:** Pre-registered — written before examining main experiment results  
**Date:** 2026-11-13

---

## 1. Research Question

Does the actual field-derived spectral observable (C_spectral) enable autonomous
agents to initiate or prepare for coordination requirements without receiving
explicit task announcements, and does it do so through environmental sensing
(precursor signal), feedback reinforcement (past-coordination signal), or both?

---

## 2. Pre-registered Hypotheses

**H1 (Primary — coordination advantage):**  
The spectral condition produces higher coordination task completion rate (CCR)
than baseline, across 40 paired trials.

**H2 (Environmental sensing):**  
The precursor_only condition (environmental precursor active, agent perturbations
disabled) produces higher CCR than baseline. If confirmed, this establishes that
the substrate encodes independent environmental information.

**H3 (Temporal-structure contribution):**  
The spectral condition outperforms all online temporal ablations (online_shuffled,
online_delayed, running_mean). If H3 holds but H2 does not, the advantage is
from feedback reinforcement rather than environmental sensing.

**H4 (Predictive information):**  
C_spectral at tick t predicts coordination demand at tick t+h (h∈{1,2,3,5,8})
better than a no-substrate baseline predictor, as measured by AUROC > 0.5 on
held-out seeds.

**H0 (Null):** No significant difference in CCR between spectral and baseline.

---

## 3. Primary Endpoint

**`coord_completion_rate` (CCR):** fraction of coordination task opportunities
where ≥ MIN_COORD_AGENTS agents independently chose to cooperate within the
task window, in the same tick.

Higher is better. Pre-registered direction: spectral > baseline.

---

## 4. Secondary Endpoints

Collected for all trials. Not used for primary significance determination.

1. `unnecessary_coop_rate` — fraction of non-task ticks where ≥ MIN_COORD_AGENTS cooperate
2. `indep_completion_rate` — fraction of independent tasks completed  
3. `mean_resources` — total resources per agent at end
4. `mean_hunger`, `mean_energy`, `mean_stress`
5. `precursor_tp_rate` — CCR on tasks with precursors (Type A events)
6. `precursor_fn_rate` — 1 − CCR on tasks without precursors (Type B events)
7. `false_positive_rate` — unnecessary coordination rate during precursor-only ticks (Type C)
8. `c_spectral_mean`, `c_spectral_std` — field signal statistics

**Trade-off analysis:** explicitly examine CCR vs unnecessary_coop_rate trade-off.
A condition that maximizes CCR by cooperating on every tick is not better.

---

## 5. Experimental Conditions

### Condition 1 — Baseline
Signal delivered to agent policy: 0.0 (constant).  
Agent perturbations: enabled.  
Environmental precursor: enabled (but agents cannot observe it directly).  
Description: agents act without substrate information. Establishes no-substrate CCR.

### Condition 2 — Spectral
Signal: actual C_spectral from `compute_spectral_transport_observable`.  
Agent perturbations: enabled.  
Environmental precursor: enabled.  
Description: full substrate pipeline. Tests combined effect.

### Condition 3 — Online shuffled
Signal: at tick t, draw uniformly from C_spectral history[0..t].  
Agent perturbations: enabled.  
Environmental precursor: enabled.  
Description: same value distribution as spectral (up to early-tick bias),
destroyed temporal order. Online — no future information.

### Condition 4 — Online delayed (delay=5 ticks)
Signal: C_spectral[max(0, t-5)].  
Agent perturbations: enabled.  
Environmental precursor: enabled.  
Description: past signal with known fixed delay. Preserves temporal autocorrelation
but shifts it. Tests whether temporal structure matters at a fixed lag.

### Condition 5 — Running mean
Signal: mean(C_spectral[0..t]).  
Agent perturbations: enabled.  
Environmental precursor: enabled.  
Description: causal running mean — no future information. Removes all temporal
variation while preserving expected value trajectory.

### Condition 6 — Precursor only (environmental sensing isolation)
Signal: actual C_spectral.  
Agent perturbations: **disabled** (agents do NOT perturb the field).  
Environmental precursor: enabled.  
Description: substrate signal comes only from the independent precursor and
initial conditions. Removes feedback reinforcement. If CCR > baseline, this
demonstrates environmental sensing.

### Condition 7 — Feedback only
Signal: actual C_spectral.  
Agent perturbations: enabled.  
Environmental precursor: **disabled**.  
Description: substrate signal comes only from agent coordination history.
Removes environmental sensing. If CCR > baseline, this demonstrates feedback
reinforcement.

---

## 6. Environmental Precursor Design

**Physical mechanism:**  
An external event at tick t_precursor applies a narrow Gaussian perturbation
(amplitude=5.0, width=1.5m) to the field at a fixed precursor zone.

This is the minimum physically defensible precursor: a concentrated injection
of field energy that is narrow in space, pushing power into high-k modes that
produce a detectable C_spectral increase (Δ≈+0.11 at tau=2.0, persistent 8+
ticks).

**Independence:**  
Generated from rng_precursor = seed + 5000, fully isolated from field, agent,
schedule, and decision RNGs.

**Four event types** (determined by schedule generator, hidden from agents):

| Type | Precursor | Task | Purpose |
|------|-----------|------|---------|
| A | Yes | Yes (3-8 ticks after) | True positive opportunity |
| B | No | Yes | False negative opportunity (can substrate still help?) |
| C | Yes | No | False positive risk (precursor with no task) |
| D | No | No | True negative opportunity |

**What agents observe:** Only C_spectral (condition-dependent). Never precursor
label, precursor zone identity, or event type.

**What is recorded (for evaluation only):** `precursor_active`, `event_type`,
`ticks_since_precursor` — stored in per-tick records but never passed to agents.

---

## 7. Agent Policy

**No coordination gate.** Agents decide to cooperate independently on every tick.

```
coord_cap(signal) = 0.5 * (1 + clip(signal, -1, 1))   ∈ [0, 1]
P(agent cooperates | signal) = coord_cap(signal)
decision: rng_decision.random() < coord_cap(signal)
```

Additional overrides (physical constraints, not task announcements):
- hunger > 0.85 → forage (not cooperate)
- energy < 0.10 → rest (not cooperate)

No `coord_task_active` check. No `coord_task_zone`. No schedule information.

**Information available to agents:**
- Own hunger, energy, stress (local state)
- Own resources (outcome history)
- Substrate signal (condition-dependent)
- Nothing else

---

## 8. Task Parameters (to be frozen after pilot)

Target: baseline CCR 50–70%.  
Pilot range: task_window ∈ {3, 4, 5}, min_coord ∈ {3, 4}.  
Freeze parameters before examining condition comparisons.

**Expected post-pilot configuration (from physics measurements):**
- N_AGENTS = 5
- MIN_COORD = 4
- TASK_WINDOW = 4 ticks
- Task rate: one task every 10–15 ticks (8–10 tasks per 100-tick run)
- Precursor lead: 3–8 ticks before task (rng-drawn)
- 60% of tasks have precursor (Type A); 40% have no precursor (Type B)
- 30% of precursor events have no subsequent task (Type C)

---

## 9. Statistical Design

**Paired seeds:** seeds 7000–7039 for main experiment.  
All 7 conditions within a trial share the same seed.

**Isolated RNG streams:**
- rng_field:    seed
- rng_agents:   seed + 1000
- rng_schedule: seed + 2000
- rng_decision: seed + 4000
- rng_precursor: seed + 5000
- rng_ablation: seed + 3000

**Primary comparison:** spectral vs baseline, paired t-test on CCR differences.  
**Bonferroni alpha:** 0.05 / 6 = 0.0083 (6 primary comparisons).

Comparisons (all vs spectral):
1. spectral vs baseline
2. spectral vs online_shuffled
3. spectral vs online_delayed
4. spectral vs running_mean
5. precursor_only vs baseline (environmental sensing test)
6. feedback_only vs baseline (feedback test)

**Effect sizes:** Cohen's d on paired differences.  
**Bootstrap CI:** 2000 resamples, percentile method.  
**Wilcoxon signed-rank** as nonparametric check for each comparison.

---

## 10. Predictive Information Analysis

For the spectral condition only. Uses per-tick records.

**Features:** C_spectral at tick t (the signal actually received).  
**Target:** coord_task_active at tick t+h for h ∈ {1,2,3,5,8}.  
**Baseline predictor:** cooperation base rate (mean CCR across all past ticks).  
**Method:** threshold-sweep on C_spectral to predict task activity at lead h.

Report per horizon h:
- Precision, recall, F1
- False-positive rate
- AUROC (trapezoidal)
- Brier score
- Improvement over baseline predictor

**Validation:** Train threshold on seeds 7000–7019 (first 20), evaluate on
7020–7039 (last 20). Do not select threshold on evaluation set.

---

## 11. Tau Scan

**Exploratory.** Not used to select tau for main experiment.

Tau values: 1.5, 2.0, 2.5, 3.0.  
Seeds: 8000–8009 (10 trials each).  
Conditions: spectral + baseline.  
Run before main experiment; freeze tau based on pilot CCR targets.

---

## 12. Exclusion Criteria

A trial is excluded if:
- Any agent's final hunger exceeds 1.0 (numerical error)
- C_spectral is NaN or Inf at any tick
- An unhandled exception occurs

Exclusions documented with reason. No imputation.

---

## 13. What This Experiment Can and Cannot Establish

**Can establish:**
- Whether removing the task announcement gate eliminates the advantage
- Whether an independent precursor signal reaches the agent through C_spectral
- Whether spectral outperforms online temporal ablations (temporal structure)
- Whether feedback reinforcement vs environmental sensing is the mechanism
- Predictive accuracy at defined lead times

**Cannot establish:**
- Whether the advantage generalises to different field geometries
- Whether an LLM-based agent would use the signal differently
- Whether the mechanism extends to multi-environment systems
