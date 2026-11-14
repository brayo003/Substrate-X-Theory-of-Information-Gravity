# PHASE 10 RESULTS
**Project:** SXC-IGC sim_world  
**Date:** 2026-11-13  
**Status:** Complete — all data from verified experimental runs

---

## 1. Experimental Configuration

| Parameter | Value |
|-----------|-------|
| Trials per condition per scenario | 30 |
| Seeds | 1000–1029 (paired across all conditions) |
| Conditions | baseline, legacy_q, spectral, ablation |
| Scenarios | stable (50 ticks), dynamic (60 ticks), disrupted (60 ticks) |
| Agents per trial | 5 |
| Tau (main experiment) | 3.0 |
| Tau scan | 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0 (10 trials each) |
| Total trial records | 450 (360 main + 90 tau scan) |
| Primary metric | mean_final_hunger (lower = better) |
| Bonferroni-corrected alpha | 0.0167 (3 comparisons per scenario) |
| Statistical tests | Paired t-test + Wilcoxon signed-rank (manual implementations) |

**Pairing:** All four conditions within each trial share an identical seed-derived field (random bump positions, amplitudes) and identical agent initial states. The only difference between conditions is the substrate signal delivered to agents.

**Baseline isolation:** The baseline condition uses a completely separate `decide_baseline()` function with no cooperation or building — a genuine no-substrate control.

**Ablation construction:** Time-reversal of the spectral C_spectral time series from an identically-seeded pre-run. Preserves exact marginal distribution; destroys temporal structure.

---

## 2. Intervention Tests (pre-experiment verification)

9/9 tests pass. Agents demonstrably respond to substrate signal changes.

| Test | Result |
|------|--------|
| coordination_capacity is strictly monotone in c_spectral | PASS |
| At c=−0.9 agent explores; at c=+0.9 agent cooperates | PASS |
| Cooperation rate: 10% in low-signal half, 100% in high-signal half (sweep test) | PASS |
| Threshold rises with need pressure (high-need agents require stronger signal) | PASS |
| Cooperate efficiency: stress reduction scales with signal (0.08 at c=0 → 0.12 at c=+1) | PASS |
| Baseline decision function never produces cooperate or build | PASS |
| Coordination-blocked flag prevents cooperation regardless of signal | PASS |
| Critical need (hunger > 0.8, energy < 0.15) overrides substrate in all conditions | PASS |
| SubstrateState.coordination_capacity = 0.5×(1+c_spectral) for all test values | PASS |

**Conclusion from intervention tests:** The agent decision function correctly and monotonically responds to substrate signal. The substrate signal path is functional.

---

## 3. Modal Validation Tests (regression check)

6/6 tests pass — no regression introduced by Phase 10 changes.

| Test | Result |
|------|--------|
| Overdamped mode decays without oscillation (err 1.0%) | PASS |
| Propagating mode frequency (ω_theory=0.646, measured=0.625, err 3.2%) | PASS |
| Propagating mode decay rate (T_theory=6.00, measured=6.57, err 9.6%) | PASS |
| Spectral fractions: τ=0.3 → C=−1.0; τ=10.0 → C=+1.0 | PASS |
| Near-critical mode classified correctly | PASS |
| Mixed-mode field: f_prop=0.495, f_over=0.505 | PASS |

---

## 4. Main Experiment Results

### Primary Metric: mean_final_hunger (lower = better)

#### Scenario: Stable (50 ticks, no disturbances)

| Condition | Mean hunger | Std | Coord% | Task success% |
|-----------|-------------|-----|--------|----------------|
| baseline  | 0.4464 | — | 0.0% | 100.0% |
| legacy_q  | 0.7241 | — | 58.0% | 0.0% |
| spectral  | 0.5959 | — | 31.4% | 49.2% |
| ablation  | 0.7407 | — | 59.1% | 0.0% |

#### Scenario: Dynamic (60 ticks, perturbation events at ticks 15 and 35)

| Condition | Mean hunger | Std | Coord% | Task success% |
|-----------|-------------|-----|--------|----------------|
| baseline  | 0.4522 | — | 0.0% | 100.0% |
| legacy_q  | 0.7313 | — | 56.3% | 0.0% |
| spectral  | 0.7397 | — | 57.5% | 0.0% |
| ablation  | 0.7453 | — | 57.4% | 0.0% |

#### Scenario: Disrupted (60 ticks, coordination blocked ticks 20–29, field reset at tick 25)

| Condition | Mean hunger | Std | Coord% | Task success% |
|-----------|-------------|-----|--------|----------------|
| baseline  | 0.4522 | — | 0.0% | 100.0% |
| legacy_q  | 0.7200 | — | 52.4% | 0.0% |
| spectral  | 0.7407 | — | 54.1% | 0.0% |
| ablation  | 0.7453 | — | 53.9% | 0.0% |

---

## 5. Paired Statistical Comparisons

All comparisons are spectral minus comparison condition.  
**Negative mean_diff = spectral is better (lower hunger).**  
Bonferroni-corrected significance threshold: α = 0.0167.  
A result is declared significant only if BOTH t-test and Wilcoxon p-values are below threshold.

### H1: Spectral vs Baseline

| Scenario | mean_diff | 95% CI (bootstrap) | Cohen's d | p-value | Significant? | Direction |
|----------|-----------|--------------------|-----------|---------|--------------|-----------|
| stable   | +0.2961   | [+0.288, +0.306]   | +10.74    | ≈0.000  | YES          | spectral_worse |
| dynamic  | +0.2875   | [+0.276, +0.300]   | +8.26     | ≈0.000  | YES          | spectral_worse |
| disrupted| +0.2885   | [+0.281, +0.296]   | +13.62    | ≈0.000  | YES          | spectral_worse |

**H1 verdict: REJECTED.** Spectral is significantly and substantially *worse* than baseline on the primary metric in all three scenarios. Effect sizes are large (d > 8). The spectral condition consistently produces higher final hunger than the no-substrate baseline.

### H2: Spectral vs Ablation (information-specificity test)

| Scenario | mean_diff | 95% CI (bootstrap) | Cohen's d | p-value | Significant? | Direction |
|----------|-----------|--------------------|-----------|---------|--------------|-----------|
| stable   | +0.0018   | [−0.005, +0.008]   | +0.10     | 0.585   | NO           | spectral_worse (not sig) |
| dynamic  | −0.0056   | [−0.013, 0.000]    | −0.31     | 0.098   | NO           | spectral_better (not sig) |
| disrupted| −0.0046   | [−0.011, +0.002]   | −0.26     | 0.165   | NO           | spectral_better (not sig) |

**H2 verdict: NOT ESTABLISHED.** No significant difference between spectral and ablation in any scenario. The spectral signal provides no detectable advantage over randomly-timed substrate values. The substrate signal provides no measurable benefit that depends on its temporal relationship to agent state.

### H3: Spectral vs Legacy-Q

| Scenario | mean_diff | 95% CI (bootstrap) | Cohen's d | p-value | Significant? | Direction |
|----------|-----------|--------------------|-----------|---------|--------------|-----------|
| stable   | +0.0184   | [+0.006, +0.029]   | +0.56     | 0.0049  | YES          | spectral_worse |
| dynamic  | +0.0084   | [−0.005, +0.021]   | +0.22     | 0.231   | NO           | spectral_worse (not sig) |
| disrupted| +0.0207   | [+0.007, +0.032]   | +0.60     | 0.0025  | YES          | spectral_worse |

**H3 finding:** Spectral is significantly worse than legacy-Q in stable and disrupted scenarios, not significantly different in dynamic. Legacy-Q drives higher coordination rates and thereby more hunger accumulation — but the spectral condition does the same without being significantly different from legacy-Q in dynamic/disrupted conditions. The spectral observable does not outperform the legacy observable.

---

## 6. Coordination-Hunger Trade-off

The central finding is a consistent coordination-hunger trade-off. Conditions that drive high coordination rates (legacy_q, spectral, ablation) all produce substantially worse hunger outcomes than the baseline, which never coordinates.

**Stable scenario summary:**
- baseline:  0.0% coordination → 0.4464 mean hunger → 100.0% task success
- spectral:  31.4% coordination → 0.5959 mean hunger → 49.2% task success
- ablation:  59.1% coordination → 0.7407 mean hunger → 0.0% task success
- legacy_q:  58.0% coordination → 0.7241 mean hunger → 0.0% task success

The spectral condition at tau=3.0 is intermediate: its C_spectral values hover around +0.57 on average, driving substantial coordination (31%), which prevents enough foraging to maintain hunger below the 0.75 spike threshold for about half the agents. The ablation and legacy_q — which drive higher coordination — do worse.

The baseline, with no coordination, outperforms all substrate conditions on the primary metric (hunger management) in every scenario.

---

## 7. Tau Calibration Scan

Spectral condition, Scenario: stable, 10 trials per tau value.

| tau   | n  | Mean hunger ± std     | Coord% |
|-------|----|-----------------------|--------|
| 0.30  | 10 | 0.4483 ± 0.0199       | 0.0%   |
| 0.50  | 10 | 0.4483 ± 0.0199       | 0.0%   |
| 0.75  | 10 | 0.4483 ± 0.0199       | 0.0%   |
| 1.00  | 10 | 0.4483 ± 0.0199       | 0.0%   |
| 1.50  | 10 | 0.4491 ± 0.0232       | 2.2%   |
| 2.00  | 10 | 0.4439 ± 0.0211       | 10.1%  |
| 3.00  | 100| 0.7421 ± 0.0224       | 57.3%  |
| 5.00  | 10 | 0.7425 ± 0.0263       | 63.6%  |
| 10.00 | 10 | 0.7425 ± 0.0263       | 63.6%  |

**Key findings:**

1. **Transition is reproducible across seeds.** The tau=1.5→2.0 regime transition is consistent: at tau=1.5, coordination begins (2.2%); at tau=2.0, it reaches 10.1%; at tau=3.0, it reaches 57.3%. The standard deviations across 10 trials are small (0.02), confirming the transition is not noise.

2. **Hunger worsens monotonically above tau=2.0.** At tau≤2.0, mean hunger ≈ 0.44–0.45 — agents forage effectively. At tau≥3.0, mean hunger ≈ 0.74 — agents are chronically near the spike threshold. The jump is sharp between tau=2.0 and tau=3.0.

3. **The best operating region for hunger management is tau ≤ 2.0.** At these values, the substrate is in the overdamped or low-coherence regime; agents receive low coordination_capacity signals and default to foraging, which is what actually maintains hunger.

4. **tau = 3.0 is NOT the optimal operating point for the primary metric.** It was chosen for the main experiment as the "coherent regime" operating point, which is correct for testing whether coordination can be elicited, but it produces the worst hunger outcomes.

5. **High-tau task-success collapse confirmed and reproducible.** At tau≥3.0, task_success_rate ≈ 0% across all 10 trials per tau. This was first observed in Phase 7 (single run) and is now confirmed across repeated trials.

6. **The transition location does not appear to vary across scenarios** in this experiment (the tau scan used only the stable scenario), so cross-scenario generalisation of the transition location is not established.

---

## 8. Runtime and Computational Overhead

| Phase | Description | Time (approx.) |
|-------|-------------|----------------|
| Main experiment (360 trials) | 4 conditions × 3 scenarios × 30 trials | ~3 minutes |
| Tau scan (90 trials) | 9 tau values × 10 trials | ~1 minute |
| Statistical analysis | Full paired comparisons + bootstrap | <5 seconds |
| Intervention tests | 9 tests | <2 seconds |
| Modal validation | 6 tests | ~20 seconds |

No computational overhead issues. The spectral condition is not significantly more expensive than baseline within the simulation loop, since the FFT operates on a 30×30 grid.

---

## 9. Data Files

All raw data is available for independent inspection:

| File | Contents |
|------|----------|
| `phase10_raw_trials.json` | 450 per-trial records with seed, condition, scenario, all metrics |
| `phase10_raw_trials.jsonl` | Same data, one record per line |
| `phase10_summary.json` | Aggregated summaries by condition and scenario |
| `phase10_analysis_results.json` | Full paired statistics, CIs, effect sizes, tau analysis |
| `phase10_intervention_results.json` | 9 intervention test results |

---

## 10. Limitations

1. **LLM path not tested.** The context_builder.py passes full SubstrateState to agent prompts, but no LLM was available. Whether an LLM uses the substrate information is unknown.

2. **Single tau value for main experiment.** The main experiment used tau=3.0 (the coherent regime operating point). Tau=3.0 is where the coordination-hunger trade-off is most severe. Results might differ at tau≈1.5–2.0, which the tau scan suggests is a better operating region.

3. **Deterministic agent rules.** The agent decision function is a fixed rule-based system. A system with learning or more flexible policy structure might use the substrate signal differently.

4. **Field-condition coupling.** The field evolves differently under each condition because agents take different actions. This is intentional (testing the full substrate-agent loop) but means conditions see slightly different field histories. This is documented as a design choice in the protocol.

5. **No recovery-time metric.** The disrupted scenario was intended to test recovery after the coordination block lifts at tick 29. A recovery-time metric was not implemented — the final-hunger metric conflates pre-disruption and post-disruption performance.

6. **Wilcoxon implemented without scipy.** The manual Wilcoxon implementation uses normal approximation for n≥10. For n=30 this is adequate but introduces minor inaccuracy compared to exact computation.
