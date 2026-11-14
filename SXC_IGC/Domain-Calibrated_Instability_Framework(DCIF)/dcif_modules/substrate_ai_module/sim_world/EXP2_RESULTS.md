# EXP2 RESULTS REPORT
**Experiment:** Controlled Spectral Substrate Coordination Experiment  
**Date:** 2026-11-13  
**Status:** Complete — all numbers from verified experimental runs

---

## 1. What Was Implemented

### New files (all in `sim_world/`)

| File | Purpose |
|------|---------|
| `exp2_environment.py` | CoordinationTaskEnvironment: hidden schedule, bidirectional coupling, 5-condition signal delivery, per-tick records |
| `exp2_runner.py` | 5-condition runner with paired seeds, isolated RNG streams, statistical analysis, lead-lag |
| `exp2_diagnostics.py` | 12 diagnostic tests |
| `EXP2_AUDIT.md` | Pre-implementation audit |

### Design decisions

**Primary metric:** `coord_completion_rate` = fraction of coordination task opportunities where ≥3 agents committed to cooperate within the task window. Pre-registered; not changed after inspecting results.

**Bidirectional coupling:** When ≥3 agents cooperate successfully, a coherent concentrated perturbation (amplitude 3.5 × n_participating, width 2.5m) is applied to the field at the coordination zone. Individual actions apply dispersed perturbations (amplitude 0.4, width 5.0m). This encodes coordination history into C_spectral.

**Task schedule:** Generated from a separate RNG (seed + 2000), isolated from field and agent streams. Never accessible to agents. Agents see only: coord_task_active (bool), coord_task_zone (x,y), indep_slots_available.

**Ablations:**
- `time_reversed`: exact temporal reverse of the spectral series from an identically-seeded reference run
- `shuffled`: same values, random permutation (rng_ablation = seed + 3000)
- `constant`: constant value = mean of reference spectral series

---

## 2. What Was Tested

**Diagnostic batch:** 10 seeds × 5 conditions × 80 ticks = 4,000 tick records  
**Main experiment:** 30 seeds × 5 conditions × 80 ticks = 12,000 tick records  
**Tau:** 3.0 for all runs  
**Seeds:** 5000–5029 (main), 5000–5009 (diagnostic)

### Diagnostic results: 12/12 tests pass

| Test | Result |
|------|--------|
| Field solver finite | PASS |
| Spectral analysis valid | PASS |
| C_spectral schedule-independent | PASS |
| Per-tick records complete | PASS |
| Baseline signal = 0.0 | PASS |
| Schedule not in observation | PASS |
| **C_spectral varies with coupling** | **PASS: std=0.197, range=[0.161, 0.759], 33/80 coord successes** |
| Paired conditions identical schedule | PASS |
| No lookahead leakage | PASS |
| Ablation marginal distributions match | PASS |
| Experiment IDs unique | PASS |
| Modal validation regression (6/6) | PASS |

---

## 3. What Was Measured

### Main experiment — primary metric (coord_completion_rate)

| Condition | Mean | Std | Coord% |
|-----------|------|-----|--------|
| baseline | 0.9461 | 0.0586 | 41.3% |
| spectral | 0.9672 | 0.0357 | 42.2% |
| time_reversed | 0.9715 | 0.0360 | 42.3% |
| shuffled | 0.9625 | 0.0424 | 42.1% |
| constant | 0.9655 | 0.0405 | 42.1% |

### Paired statistical comparisons (n=30 paired trials)

Bonferroni-corrected alpha = 0.0125 (4 comparisons).  
Positive diff = spectral is better (higher completion rate).

| Comparison | mean_diff | 95% CI (bootstrap) | p (raw) | Cohen's d | Significant? |
|------------|-----------|-------------------|---------|-----------|--------------|
| spectral vs baseline | +0.0210 | [+0.006, +0.037] | 0.0096 | +0.473 | **YES** |
| spectral vs time_reversed | −0.0043 | [−0.017, +0.009] | 0.509 | −0.120 | no |
| spectral vs shuffled | +0.0047 | [−0.005, +0.015] | 0.367 | +0.165 | no |
| spectral vs constant | +0.0017 | [−0.009, +0.013] | 0.769 | +0.054 | no |

### Lead-lag cross-correlation (spectral condition, main experiment)

| Metric | Value |
|--------|-------|
| Contemporaneous xcorr (lag=0) | 0.034 |
| Peak xcorr | 0.128 at lag=−3 |
| Interpretation | C_spectral **lags** coordination demand by 3 ticks (reactive) |

---

## 4. What the Data Demonstrates

### Finding 1 — Outcome B: Temporal-structure contribution NOT demonstrated

The spectral condition outperforms baseline (mean_diff=+0.021, p=0.0096, d=0.47 — significant at Bonferroni-corrected α=0.0125). However, it does **not** significantly outperform time_reversed, shuffled, or constant controls.

This means: **having some substrate signal helps, but its specific temporal structure does not add measurable value over signal values with destroyed temporal order**.

The agent improves relative to no-substrate baseline because the signal modulates cooperation willingness upward (C_spectral ≈ +0.6 at tau=3.0 on average, giving coordination_capacity ≈ 0.80). But a time-reversed or shuffled signal would do the same thing, since all these conditions see the same distribution of C_spectral values.

### Finding 2 — Outcome C: State-tracking only (not predictive)

The lead-lag analysis shows peak correlation at lag=−3: C_spectral **lags** coordination demand by 3 ticks, not leads it.

This means C_spectral is a reactive signal — it rises **after** coordination events (because successful coordination applies coherent perturbations that increase C_spectral). It does not carry forward-looking information about upcoming task demand.

The diagnostic batch showed peak_lag=+1 at smaller scale, but the main experiment with 30 seeds and full per-tick records converges on peak_lag=−3. The diagnostic signal was too noisy (n=10) to establish the direction reliably.

**Practical implication:** Agents cannot use C_spectral to anticipate upcoming coordination tasks. They can only use it to know that recent coordination was successful. This is a contemporaneous/lagging indicator, not a leading one.

### Finding 3 — Outcome A (partial): Demonstrated substrate advantage over no-substrate

The spectral condition significantly and reproducibly outperforms the genuine no-substrate baseline. Effect size d=0.47 (medium) is practically meaningful given the task.

However, this advantage exists because:
1. At tau=3.0, C_spectral ≈ +0.6 on average, raising coordination_capacity above typical need-based thresholds.
2. This is functionally equivalent to a constant bias toward cooperation.
3. The advantage over constant (which delivers the same mean signal) is +0.0017, negligible and not significant.

The substrate's value here is as a consistent high-coordination-capacity signal, not as temporally-structured information about the environment.

---

## 5. What Remains Unverified

1. **Whether temporal structure of C_spectral would become useful** with a faster-varying schedule that creates genuine temporal gaps between task clusters. The current cluster structure (3–6 tasks every ~8–12 ticks) produces demand patterns that cannot be predicted 1–5 ticks ahead from the field state.

2. **Whether the signal would become predictive at different tau values.** The tau scan was not run in this experiment. At tau values near the spectral transition (1.5–2.0), field dynamics are more sensitive to individual perturbations, potentially creating a tighter link between agent coordination and field state.

3. **Whether more agents (N>5) would amplify the coupling signal** enough to produce predictive rather than reactive C_spectral behaviour.

4. **LLM path.** Not tested. The context_builder.py now passes SubstrateState to agent prompts but whether an LLM uses it differently from the deterministic rule policy is unknown.

---

## 6. Outcome Classification

**Primary classification: B (Temporal-structure contribution not demonstrated) with partial A (demonstrated signal advantage over no-signal)**

The spectral substrate provides a reproducible and statistically significant improvement over baseline (+2.1%, p=0.0096, d=0.47). This is a real finding. However, it cannot be attributed to the *temporal structure* of the spectral signal — time-reversed and shuffled controls perform equivalently. The advantage comes from the signal's mean value, not its timing.

The substrate is functioning as a bias amplifier for cooperation, not as an information channel about coordination timing.

---

## 7. Reproducibility Instructions

### Environment setup

```bash
cd sim_world
# Python 3.10 venv with numpy already installed
.venv/bin/python --version  # 3.10.x
.venv/bin/python -c "import numpy; print(numpy.__version__)"
```

### Run diagnostics

```bash
PYTHONPATH=$(dirname $(pwd)) .venv/bin/python exp2_diagnostics.py
# Expected: 12/12 tests pass
# Saves: exp2_diagnostic_results.json
```

### Run diagnostic batch

```bash
PYTHONPATH=$(dirname $(pwd)) .venv/bin/python exp2_runner.py --diagnostic
# Expected: 50 trials (10 seeds × 5 conditions), ~140s
# Saves: exp2_diag_results.json, exp2_diag_analysis.json, exp2_diag_per_tick.jsonl
```

### Run main experiment

```bash
PYTHONPATH=$(dirname $(pwd)) .venv/bin/python exp2_runner.py --main
# Expected: 150 trials (30 seeds × 5 conditions), ~370s
# Saves: exp2_main_results.json, exp2_main_analysis.json, exp2_main_per_tick.jsonl
```

### Verify results

```bash
PYTHONPATH=$(dirname $(pwd)) .venv/bin/python -c "
import json
with open('exp2_main_results.json') as f:
    r = json.load(f)
print('N trials:', len(r))
from collections import Counter
print('Per condition:', Counter(t['condition'] for t in r))
spec = [t['coord_completion_rate'] for t in r if t['condition']=='spectral']
base = [t['coord_completion_rate'] for t in r if t['condition']=='baseline']
import numpy as np
print('Spectral mean:', round(np.mean(spec),4))
print('Baseline mean:', round(np.mean(base),4))
print('Diff:', round(np.mean(spec)-np.mean(base),4))
"
```

Expected output:
```
N trials: 150
Per condition: Counter({'baseline': 30, 'spectral': 30, 'time_reversed': 30, 'shuffled': 30, 'constant': 30})
Spectral mean: 0.9672
Baseline mean: 0.9461
Diff: 0.0210
```

### Raw data files

| File | Contents | Size |
|------|----------|------|
| `exp2_main_results.json` | 150 trial summaries with all metrics | 84KB |
| `exp2_main_analysis.json` | Paired comparisons, CIs, effect sizes | 3KB |
| `exp2_main_per_tick.jsonl` | 12,000 per-tick records | ~2MB |
| `exp2_diag_results.json` | 50 diagnostic trial summaries | 28KB |
| `exp2_diagnostic_results.json` | 12 diagnostic test results | <1KB |

Every reported aggregate can be reproduced from the raw trial summaries in `exp2_main_results.json`.

### Key design parameters (do not change without documenting)

| Parameter | Value | Location |
|-----------|-------|----------|
| MIN_COORD_AGENTS | 3 | exp2_environment.py |
| COHERENT_PERT_AMP | 3.5 per agent | exp2_environment.py |
| PERT_WIDTH_COHERENT | 2.5m | exp2_environment.py |
| INDEP_PERT_AMP | 0.4 | exp2_environment.py |
| TASK_WINDOW_TICKS | 3 | exp2_environment.py |
| tau (main) | 3.0 | exp2_runner.py |
| n_ticks | 80 | exp2_runner.py |
| n_trials | 30 | exp2_runner.py |
| base_seed | 5000 | exp2_runner.py |
| Bonferroni alpha | 0.0125 (0.05/4) | exp2_runner.py |
