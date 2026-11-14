# EXP3 RESULTS
**Date:** 2026-11-13  
**Status:** Complete  
**Pre-registration:** EXP3_SPECIFICATION.md (written before examining main-experiment results)  
**Audit:** EXP3_AUDIT.md (written before implementation)

---

## Summary

EXP3 addresses the core limitation of EXP2: agents in EXP2 received an explicit
coordination-task announcement (`coord_task_active`) that opened the cooperation gate.
EXP3 removes this gate entirely. Agents must discover and initiate coordination
autonomously, using only their own physiological state and the substrate signal.

The experiment tests three mechanisms independently:

| Mechanism | Condition | Result |
|-----------|-----------|--------|
| Environmental sensing (precursor → field → agent) | precursor_only | **DEMONSTRATED** (d=2.22) |
| Feedback reinforcement (agent → field → agent) | feedback_only | **DEMONSTRATED** (d=0.46) |
| Temporal-structure contribution | spectral vs online ablations | **NOT demonstrated** (spectral ≤ ablations) |
| Predictive information (c_spectral predicts future demand) | AUROC at h=1–8 | **NOT demonstrated** (AUROC ≤ 0.52) |

---

## Experimental Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| tau | 3.0 | Tau scan: only tau where spectral > baseline |
| N_AGENTS | 5 | Fixed |
| MIN_COORD_AGENTS | 3 | Pilot calibration |
| TASK_WINDOW_TICKS | 8 | Pilot calibration (maximises spectral–baseline gap) |
| Task interval | 8–15 ticks | Fixed |
| Precursor probability | 60% (Type A) | Fixed |
| Precursor lead time | 3–8 ticks | Fixed |
| Precursor amplitude | 5.0 (narrow, width=1.5m) | Verified: Δc_spectral ≈ +0.11 |
| Trials | 40 seeds × 7 conditions | Fixed |
| Seeds | 7000–7039 | Fixed |
| Bonferroni α | 0.0083 (6 comparisons) | Pre-registered |

**All ablations are strictly online:** at tick t, no ablation condition accesses
information from ticks later than t. This was verified by diagnostic tests 7, 8,
9, and 13 (15/15 diagnostics passed).

---

## Pilot Calibration Results

| task_window | baseline CCR | spectral CCR |
|-------------|-------------|-------------|
| 3 | 0.415 | 0.414 |
| 5 | 0.437 | 0.442 |
| 8 | 0.439 | 0.470 ← selected |

Window=8 selected: highest spectral–baseline gap (+0.031) while maintaining
baseline in target range (40–75%). Parameters frozen before examining main results.

---

## Tau Scan Results

| tau | spectral CCR | baseline CCR | diff | c_spectral_std |
|-----|-------------|-------------|------|----------------|
| 1.5 | 0.019 | 0.427 | −0.409 | 0.108 |
| 2.0 | 0.111 | 0.427 | −0.316 | 0.133 |
| 2.5 | 0.274 | 0.427 | −0.153 | 0.192 |
| 3.0 | 0.449 | 0.427 | **+0.022** | 0.199 |

tau=3.0 is the only value where spectral outperforms baseline. At tau < 3.0 the
field is predominantly overdamped (c_spectral < 0), which suppresses cooperation
in the spectral condition relative to baseline (signal=0.0). tau=3.0 is the
transition point between overdamped and mixed-propagating regimes.

---

## Main Experiment Results

**40 paired trials (seeds 7000–7039), 100 ticks per trial, tau=3.0, window=8.**

| Condition | CCR mean | CCR std | UCR mean | Coord% |
|-----------|----------|---------|----------|--------|
| baseline | 0.4087 | 0.0522 | 0.4456 | 45.9% |
| spectral | 0.4606 | 0.1069 | 0.5043 | 48.8% |
| online_shuffled | 0.5181 | 0.0566 | 0.5595 | 51.8% |
| online_delayed | 0.4644 | 0.0879 | 0.5055 | 49.3% |
| running_mean | 0.5131 | 0.0756 | 0.5441 | 51.6% |
| **precursor_only** | **0.5588** | **0.0553** | 0.5658 | 53.6% |
| feedback_only | 0.4609 | 0.1010 | 0.4963 | 48.9% |

CCR = coordination task completion rate (fraction of task-active ticks where ≥3 agents cooperate).  
UCR = unnecessary cooperation rate (fraction of task-inactive ticks where ≥3 agents cooperate).

### Primary comparisons (Bonferroni α = 0.0083)

| Comparison | Diff | 95% CI | p | d | Significant |
|------------|------|--------|---|---|-------------|
| spectral vs baseline | +0.052 | [+0.013, +0.087] | 0.0071 | 0.43 | ✓ |
| spectral vs online_shuffled | −0.058 | [−0.086, −0.031] | <0.001 | −0.63 | ✓ |
| spectral vs online_delayed | −0.004 | [−0.024, +0.016] | 0.72 | −0.06 | ✗ |
| spectral vs running_mean | −0.053 | [−0.077, −0.028] | <0.001 | −0.63 | ✓ |
| precursor_only vs baseline | +0.150 | [+0.129, +0.170] | <0.001 | 2.22 | ✓ |
| feedback_only vs baseline | +0.052 | [+0.014, +0.086] | 0.0037 | 0.46 | ✓ |

---

## Finding 1 — Environmental sensing is confirmed with large effect size

**precursor_only vs baseline: +0.150, d=2.22, p<0.001.**

The precursor_only condition disables agent-to-field perturbations while preserving
the independent environmental precursor. The substrate signal in this condition comes
only from the precursor (and initial field conditions). That it substantially
outperforms baseline (d=2.22) confirms:

1. The independent physical precursor produces a detectable spectral signature
   (verified in diagnostics: Δc_spectral ≈ +0.10 at tick of precursor).
2. This signature reaches agents through the actual field-solver pipeline
   (s(x,t) → FFT → D_k → modal classification → C_spectral → agent decision).
3. The signal improves coordination without any explicit task announcement.

**This is the strongest result in EXP3.** Environmental sensing through the
physical substrate is confirmed at a very large effect size.

---

## Finding 2 — Feedback reinforcement is confirmed at medium effect size

**feedback_only vs baseline: +0.052, d=0.46, p=0.0037.**

The feedback_only condition disables the environmental precursor while preserving
agent-to-field perturbations. That it outperforms baseline confirms:

1. When agents cooperate, they perturb the field.
2. These perturbations modify C_spectral.
3. The modified C_spectral influences subsequent agent cooperation decisions.
4. This creates a positive feedback loop that modestly increases CCR over baseline.

The effect size (d=0.46) is similar to the spectral condition (d=0.43 vs baseline),
suggesting that **feedback reinforcement is the dominant mechanism in the full
spectral condition** — the precursor contribution is cancelled by feedback noise.

---

## Finding 3 — Full spectral condition does NOT outperform temporal ablations

**spectral vs online_shuffled: −0.058, d=−0.63, p<0.001.**
**spectral vs running_mean: −0.053, d=−0.63, p<0.001.**

Counterintuitively, the online shuffled and running mean conditions outperform the
actual spectral condition. Both ablations are strictly causal: they use only past
c_spectral values from the same run.

**Why ablations outperform spectral:**

The online_shuffled condition draws from its own c_history, which includes values
from periods when the field was more active. The running mean similarly integrates
over the entire past trajectory. Both tend to deliver a higher, more stable signal
than the instantaneous spectral value.

The actual spectral condition's signal is noisier (std=0.107 vs 0.057 for
precursor_only). When agent feedback perturbations are active, they add high-k
power that creates short-term c_spectral spikes during non-task periods. This noise
causes more unnecessary cooperation (UCR=0.504 vs baseline=0.446), which drains
agent resources and sometimes prevents cooperation during actual tasks.

**Implication:** The temporal structure of C_spectral carries no additional value
over its time-averaged properties. This replicates the EXP2 finding under a more
rigorous (online, causal) ablation design.

---

## Finding 4 — Precursor signal is CANCELLED by feedback noise in full spectral condition

**spectral vs precursor_only: −0.098, d=−0.82, p<0.001.**

The full spectral condition (both precursor and feedback active) performs
*significantly worse* than the precursor_only condition (precursor active, feedback
disabled). The difference −0.098 is highly significant.

Event-type analysis reveals the mechanism:

| Condition | Type A CCR (precursor+task) | Type B CCR (task only) | A−B |
|-----------|---------------------------|------------------------|-----|
| baseline | 0.432 | 0.407 | +0.025 |
| spectral | **0.349** | **0.465** | −0.116 |
| precursor_only | 0.553 | 0.559 | −0.006 |

In the spectral condition, coordination is *worse* during precursor events (Type A)
than during bare task events (Type B). The precursor creates a large spike in
C_spectral (+0.11+), which raises cooperation probability everywhere — including
Type C ticks (precursor without task), which increases unnecessary cooperation and
depletes agent resources. By the time the actual task arrives (3–8 ticks after
the precursor), agents have burned energy and resources on unnecessary coordination,
leaving fewer available to cooperate when needed.

The precursor_only condition avoids this because there is no feedback noise: the
signal is cleaner and agents don't over-cooperate during precursor-only periods.

---

## Finding 5 — C_spectral does not predict future coordination demand

**AUROC at all measured horizons:**

| Horizon h | AUROC | vs chance | Brier | Skill |
|-----------|-------|-----------|-------|-------|
| h=1 | 0.461 | −0.039 | 0.561 | −1.62 |
| h=2 | 0.457 | −0.043 | 0.564 | −1.67 |
| h=3 | 0.458 | −0.042 | 0.566 | −1.71 |
| h=5 | 0.477 | −0.023 | 0.561 | −1.77 |
| h=8 | **0.516** | **+0.016** | 0.539 | −1.66 |

For h=1 through h=5, AUROC < 0.5 (c_spectral is anticorrelated with future demand).
At h=8, AUROC=0.516 (barely above chance, +0.016).

**Why AUROC < 0.5 at short horizons:** When a coordination task becomes active,
agents cooperate, which perturbs the field, which raises C_spectral contemporaneously.
So high C_spectral occurs *during* tasks, not before them. At short leads (h=1–5),
pairing c_spectral[t] with demand[t+h] picks up this signal in reverse — high
c_spectral now predicts low demand at t+h (because the current task window is
ending). This is the same reactive-lagging pattern found in EXP2.

**At h=8:** The relationship reverses because the precursor fires 3–8 ticks before
tasks. At h≈8, some high c_spectral values at tick t were caused by precursors
that lead to tasks at t+8. AUROC=0.516 reflects this weak predictive signal, but
it is insufficient for reliable prediction.

**Conclusion:** C_spectral does not contain usefully predictive information about
upcoming coordination demand at any measured horizon in EXP3.

---

## Finding 6 — Lead-lag cross-correlation confirms reactive signal

**Peak cross-correlation at lag=+8 (c_spectral leads demand by 8): xcorr=+0.034.**

| Lag | Mean xcorr | Interpretation |
|-----|-----------|----------------|
| −8 | −0.058 | c_spectral lags demand by 8 |
| −5 | +0.010 | c_spectral lags demand by 5 |
| −3 | +0.014 | c_spectral lags demand by 3 |
| −2 | −0.005 | c_spectral lags demand by 2 |
| −1 | −0.040 | c_spectral lags demand by 1 |
| 0 | −0.077 | contemporaneous |
| +1 | −0.090 | c_spectral leads demand by 1 |
| +2 | −0.093 | c_spectral leads demand by 2 |
| +3 | −0.084 | c_spectral leads demand by 3 |
| +5 | −0.038 | c_spectral leads demand by 5 |
| **+8** | **+0.034** | **c_spectral leads demand by 8** ← **peak** |

The contemporaneous (lag=0) and short-lead correlations are strongly negative:
high C_spectral co-occurs with active tasks (from agent feedback), and the
cooperation ends as the task window closes. The positive peak at lag=+8 is the
precursor signal: the precursor fires 3–8 ticks before some tasks, so c_spectral
at t predicts demand at t+8 with weak positive correlation.

All cross-correlations are small (|xcorr| ≤ 0.093). The relationship is structurally
correct (precursor produces a leading signal) but quantitatively too weak for
reliable prediction at the current coupling amplitudes.

---

## Summary Table: Research Questions

### 1. Coordination advantage demonstrated?

**Yes, partially.** Spectral condition outperforms baseline (+0.052, d=0.43, p=0.007).
But this advantage is NOT explained by temporal structure — online ablations (shuffled,
running mean) outperform spectral, suggesting the advantage comes from time-averaged
signal level, not predictive content.

### 2. Environmental sensing demonstrated?

**Yes, strongly.** precursor_only vs baseline: +0.150, d=2.22, p<0.001.
The independent precursor creates a detectable field signature that improves
coordination. This is the clearest positive result in the experiment.

**However:** in the full spectral condition, the precursor advantage is cancelled
by feedback noise. precursor_only significantly outperforms spectral (−0.098, d=−0.82).

### 3. Feedback reinforcement demonstrated?

**Yes.** feedback_only vs baseline: +0.052, d=0.46, p=0.0037.
Agent cooperation perturbs the field, which modestly reinforces future cooperation.

### 4. Temporal structure carries additional value?

**No.** spectral is significantly worse than online_shuffled and running_mean.
The temporal pattern of C_spectral has no value over its running mean.

### 5. Predictive information demonstrated?

**No.** AUROC ≤ 0.52 at all tested horizons. C_spectral does not reliably predict
upcoming coordination demand. At short horizons it is anticorrelated (reactive
signal from past events). At h=8 there is a marginal positive signal from the
precursor but it is too weak (AUROC=0.516) to be operationally useful.

### 6. Resource costs and false-positive behaviour?

The full spectral condition has higher unnecessary cooperation rate (UCR=0.504)
than baseline (UCR=0.446). The precursor events create field spikes that raise
cooperation probability on spurious (Type C) ticks. precursor_only also has elevated
UCR (0.566) because the precursor signal is strong and persistent.

There is a genuine trade-off between CCR and UCR: precursor_only achieves the
highest CCR (0.559) at the cost of the highest coordination rate (53.6%), including
many unnecessary coordinations.

---

## Limitations

### 1. Precursor signal destroyed by feedback in full spectral condition

The most important limitation: adding agent feedback to the precursor condition
*reduces* rather than enhances performance. The spectral condition is worse than
precursor_only by 0.098 CCR points. The precursor produces a strong but brief
signal spike; agent feedback perturbations create background noise that makes
the spike indistinguishable from non-task high-activity periods.

**What this requires for a successor experiment:**
Decouple the precursor and feedback pathways spatially or spectrally, so the
precursor signal is distinguishable from agent-generated noise.

### 2. Task window duration affects interpretation

CCR is measured per tick (not per task event). A task lasting 8 ticks contributes
8 to the opportunity count. This means CCR measures the agent's per-tick cooperation
rate during active tasks, not whether they "solve" each task. The two interpretations
converge at short windows; they diverge at longer windows.

### 3. Online shuffled paradox

The online_shuffled condition outperforms spectral by 0.058 CCR. This occurs because
the shuffled signal tends to deliver a higher average signal than the instantaneous
spectral value: the history includes values from both high and low periods, while
the current spectral value tracks the instantaneous (noisy) field state. This
confirms that the temporal structure of C_spectral has negative, not positive, value
in the current design.

### 4. Minimal predictive signal requires larger amplitude or cleaner mechanism

The precursor produces Δc_spectral ≈ +0.10 on the tick it fires. This is physically
correct and verifiably passes through field dynamics. But the signal decays within
5–8 ticks, and the feedback noise from agent cooperation creates comparable-magnitude
fluctuations. AUROC at h=8 is only 0.516.

A physically justified way to strengthen this: increase the precursor amplitude
(requires stability analysis) or select a tau that sits more precisely in the
mixed-mode transition region where the spectral observable is most sensitive to
injected high-k modes.

---

## What a Valid Successor Experiment (EXP4) Requires

1. **Spatial separation:** Place precursor zones at a fixed spatial location, task
   zones at a different location. This creates a spatial correlation between precursor
   location and task location that agents could exploit if they had spatial observations.

2. **Stronger or more targeted coupling:** Increase precursor amplitude with stability
   testing. Document the resulting field response and verify it doesn't blow up.

3. **Decouple feedback spatially:** If agent perturbations occur at fixed agent positions
   and precursors at a separate location, C_spectral can distinguish the two contributions
   by using spatial modal analysis rather than a single global observable.

4. **Shorter feedback perturbation width (higher k):** Current AGENT_PERT_WIDTH=5.0m
   produces medium-k energy that contributes significantly to C_spectral. Increase to
   wide (10–15m, low-k) for agent perturbations, so agent feedback pushes the field
   toward *overdamped* modes, leaving the high-k propagating regime as a cleaner
   precursor-only signal.

5. **Online ablations are confirmed correct:** EXP3's ablations are strictly causal.
   Retain this design in EXP4.

---

## Files Produced

| File | Description |
|------|-------------|
| `EXP3_AUDIT.md` | Pre-implementation audit of architecture and design |
| `EXP3_SPECIFICATION.md` | Pre-registered protocol |
| `exp3_environment.py` | EXP3 environment (no gate, precursor, 7 conditions) |
| `exp3_runner.py` | Pilot, tau scan, main experiment runner |
| `exp3_diagnostics.py` | 15 diagnostic tests (all pass) |
| `exp3_analysis.py` | Statistical + predictive information analysis |
| `exp3_diagnostic_results.json` | Diagnostic test results (15/15 pass) |
| `exp3_pilot_results.json` | Pilot calibration results |
| `exp3_tau_scan.json` | Tau scan results (4 tau values × 10 seeds) |
| `exp3_main_results.json` | Trial summaries (280 trials) |
| `exp3_main_analysis.json` | Main statistical analysis |
| `exp3_main_per_tick.jsonl` | Raw per-tick records (28,000 records) |
| `exp3_predictive_analysis.json` | Predictive information analysis |

---

## Reproduction Instructions

```bash
cd sim_world
PYTHONPATH=.. .venv/bin/python exp3_diagnostics.py      # 15/15 must pass
PYTHONPATH=.. .venv/bin/python exp3_runner.py --pilot --tau 3.0
PYTHONPATH=.. .venv/bin/python exp3_runner.py --tau-scan
PYTHONPATH=.. .venv/bin/python exp3_runner.py --main --tau 3.0 --window 8
PYTHONPATH=.. .venv/bin/python exp3_analysis.py
```

All results are deterministic given fixed seeds. The random number streams are
isolated per RNG role (field, agents, schedule, decision, ablation, precursor).
Running the same commands produces identical results.

---

*EXP3 is complete. The key finding is that environmental sensing through the physical
substrate is demonstrably possible (d=2.22) but requires isolating the precursor
pathway from agent feedback noise. The full substrate pipeline (precursor + feedback)
underperforms the precursor-only configuration due to feedback noise cancelling the
precursor advantage. This motivates a spatially-aware redesign in EXP4.*
