# PHASE 10 EXPERIMENTAL PROTOCOL
**Project:** SXC-IGC sim_world  
**Version:** 1.0  
**Date:** 2026-11-13  
**Status:** Pre-registered — written before examining comparative results  

---

## 1. Scientific Question

> Does meaningful spectral substrate information improve autonomous-agent performance
> compared with an equivalent agent system without that information?

This question is answered for a deterministic rule-based agent system within
the existing sim_world simulation. LLM-based reasoning is excluded from the
primary experiment to prevent non-determinism from contaminating results.

---

## 2. Hypotheses

All hypotheses are stated before data collection and analysis.

**H1 (Primary):**  
The spectral substrate condition produces lower mean final hunger than the
baseline condition, averaged across all seeds and scenarios.  
(Lower mean_final_hunger = better task performance = agents managed needs more
effectively.)

**H2 (Information-specificity):**  
The spectral substrate condition produces lower mean final hunger than the
ablation condition. If H1 holds but H2 does not, the effect is due to having
*some* substrate signal rather than the specific temporal structure of the
spectral signal.

**H3 (Regime conditionality):**  
The spectral advantage (spectral − baseline difference in mean_final_hunger)
varies significantly across tau values, with the largest advantage occurring in
the tau range where the spectral transition occurs (around τ ≈ 1.5–3.0).

**H0 (Null):**  
No statistically significant difference in mean_final_hunger between spectral
and any comparison condition.

---

## 3. Primary Endpoint

**`mean_final_hunger`**: mean of all agents' final hunger values at the end of
the run. Range [0, 1]. Lower is better.

**Rationale for this choice:** It is continuous (better statistical power than
binary task_success), directly interpretable (agents with lower final hunger
managed their needs better), and not systematically biased by coordination rate
(a highly-coordinating agent that also forages sufficiently will score well).

**Direction of test:** One-sided — testing whether spectral < comparison (spectral
produces lower hunger = better). Report both one-sided and two-sided p-values.

---

## 4. Secondary Endpoints

Collected for all trials. Reported separately. Not used for primary significance
determination.

1. `mean_final_energy` — mean energy at end of run (higher = better)
2. `mean_final_stress` — mean stress at end (lower = better)
3. `task_success_rate` — fraction of agents with zero hunger-spike-above-0.75 events
4. `coordination_rate` — fraction of agent-ticks spent cooperating
5. `build_rate` — fraction of agent-ticks building
6. `forage_rate` — fraction of agent-ticks foraging
7. `resource_efficiency` — total hunger reduction / (n_agents × n_ticks)
8. `mean_stress_reduction` — initial minus final stress, averaged over agents

**Trade-off analysis:** Explicitly examine whether conditions with higher
coordination_rate have lower task_success_rate or higher final_hunger. Report
the coordination-hunger trade-off table for each scenario.

---

## 5. Experimental Conditions

### Condition A — Baseline (no substrate)

Agents use need-based rules only. No substrate signal enters the decision function.

Decision logic:
- hunger > 0.8 → forage
- energy < 0.15 → rest  
- hunger > 0.5 → forage
- energy < 0.4 → rest
- else → explore

No cooperation. No building. This is a genuine no-substrate control. It
establishes what agents do from need-pressure alone.

### Condition B — Legacy Q

Agents receive the local gradient observable `Q_local = 4c²τ²|∇ln s|² − 1`
at the measurement coordinate (15.0, 12.0, 0.0), normalised to [−1, +1] via:

`signal = 2.0 / (1.0 + exp(−q_value / 5.0)) − 1.0`

This is the deprecated quantity, retained as a comparison to show whether the
corrected spectral observable performs differently.

### Condition C — Spectral Substrate

Agents receive `C_spectral = f_prop − f_over` from the corrected
`compute_spectral_transport_observable()` (background-subtracted FFT, epsilon
tolerance 0.05). Range [−1, +1].

Decision uses continuous coordination_capacity:
`coordination_capacity = 0.5 * (1 + c_spectral)`

### Condition D — Ablation (time-reversal control)

For each trial, the spectral C_spectral time series is computed by running
the same field forward with the same seed. The series is then reversed:
tick i receives the signal that spectral tick (n−1−i) would have received.

This preserves the exact marginal distribution and value range of C_spectral
while destroying its temporal relationship to agent state and needs. It is a
valid distribution-preserving control.

**What is preserved:** Marginal distribution of C_spectral values, field
physics, agent physics, same initial conditions.  
**What is destroyed:** The temporal correlation between substrate state and
agent decision timing.

---

## 6. Pairing

Each trial is identified by an integer seed `s = base_seed + trial_index`.

The seed controls:
- Bump positions: 4 bumps at `rng.uniform(10, 40)` for x and y
- Bump amplitudes: `rng.uniform(2.0, 4.0)` per bump
- Agent initial states: small uniform noise around default values
- Environmental disturbance timing (scenarios 2 and 3)

All four conditions within a trial use the identical seed-derived initial
conditions. The only difference between conditions is the substrate signal
(or its absence) presented to agents.

This pairing enables paired statistical tests that cancel out between-trial
variation in initial conditions.

---

## 7. Environmental Scenarios

### Scenario 1 — Stable

- 50 ticks
- 4 Gaussian bumps at seed-derived positions, amplitude 2.0–4.0, width 3.0
- No disturbances
- Purpose: establish whether spectral substrate provides benefit under
  predictable conditions; check that it does not introduce unnecessary overhead

### Scenario 2 — Dynamic

- 60 ticks
- 4 initial bumps as in Scenario 1
- At tick 15: 2 additional perturbations at seed-derived positions (amplitude 2.0)
- At tick 35: 2 more perturbations at different seed-derived positions
- Purpose: test whether temporal substrate information improves adaptation to
  changing resource landscape

### Scenario 3 — Disrupted

- 60 ticks
- 4 initial bumps as in Scenario 1
- Ticks 20–29: coordination blocked (agents cannot cooperate; decision falls through)
- At tick 25: field reset to fresh initialisation with same seed
- Purpose: test whether substrate improves resilience and recovery after disruption

---

## 8. Trial Count and Seeds

- **Main experiment:** 30 trials per condition per scenario = 360 trials total
- **Seeds:** 1000, 1001, ..., 1029 for trials 0–29
- **Tau scan:** Spectral condition, Scenario 1 only, 10 trials per tau value,
  seeds 2000–2009, tau values [0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
- **Tau for main experiment:** 3.0 (coherent regime based on Phase 7 findings)

---

## 9. Statistical Methods

### Primary comparison

For each (scenario, comparison_pair):

1. Extract paired vectors: `spectral_values[i]` and `other_values[i]` for seed i
2. Compute paired differences: `d[i] = spectral[i] - other[i]`
   (negative d = spectral is better for mean_final_hunger)
3. **Paired t-test:** `t, p = scipy.stats.ttest_rel(spectral_values, other_values)`
4. **Wilcoxon signed-rank:** `stat, p = scipy.stats.wilcoxon(d)` (nonparametric check)
5. **Bootstrap 95% CI on mean(d):** 1000 resamples with replacement, percentile method
6. **Cohen's d:** `mean(d) / std(d, ddof=1)`
7. **Bonferroni correction:** adjusted alpha = 0.05 / 3 = 0.0167

### Reporting

For each comparison report:
- n_trials
- mean(spectral), std(spectral)
- mean(other), std(other)
- mean(d), std(d)
- 95% CI on mean(d) [analytical and bootstrap]
- t-statistic, raw p-value, Bonferroni-corrected p-value
- Wilcoxon p-value
- Cohen's d
- Interpretation: significant? practically meaningful?

Cohen's d interpretation: |d| < 0.2 negligible, 0.2–0.5 small, 0.5–0.8 medium, > 0.8 large.

### Multiple comparisons

Three primary comparisons per scenario:
1. Spectral vs Baseline
2. Spectral vs Legacy-Q
3. Spectral vs Ablation

Bonferroni-corrected alpha = 0.0167.

A result is declared significant only if BOTH t-test and Wilcoxon p-values are
below the corrected alpha.

---

## 10. Exclusion Criteria

A trial is excluded if:
- Any agent's final hunger exceeds 1.0 (numerical error)
- The field produces NaN or Inf values in C_spectral
- The trial raises an unhandled exception

Excluded trials are documented with reason. Missing data is NOT replaced with
zero or any imputed value. If exclusion rate exceeds 10% for any condition, that
condition's results are flagged as unreliable.

---

## 11. Tau Investigation

Separate from the main experiment. Spectral condition only. Scenario 1. 10 trials.
Seeds 2000–2009. Tau values as listed above.

For each tau value report:
- Mean and std of mean_final_hunger across 10 trials
- Mean and std of coordination_rate
- Mean and std of task_success_rate
- Dominant spectral regime (from mean C_spectral)

Determine:
1. Whether the spectral transition is reproducible across seeds
2. Whether the behavioural transition tracks the spectral transition
3. Whether an apparent operating region exists (tau where task outcomes are good)

---

## 12. Intervention Tests (Separate from Main Experiment)

Independently verify that the agent decision function responds monotonically
to c_spectral by holding all other inputs constant and varying only c_spectral.

If the function does not respond monotonically, the main experiment is testing
a system where the substrate signal has no guaranteed effect, which would explain
null results.

Report the response curve and monotonicity finding before interpreting the main results.
